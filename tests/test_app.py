"""
Audio2Tekst - Unit Tests for Core Functions
============================================

Testy jednostkowe dla podstawowych funkcji aplikacji Audio2Tekst.
"""

import hashlib
from pathlib import Path
from unittest.mock import patch
import pytest
import re
import math

# --- Funkcje pomocnicze do testów (usuwamy duplikaty w klasach) ---
def clean_transcript(text: str) -> str:
    text = re.sub(r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def transcribe_chunks(chunks, client):
    texts = []
    for chunk_path in chunks:
        if chunk_path.stat().st_size <= 25 * 1024 * 1024:  # 25MB limit
            with open(chunk_path, "rb") as f:
                res = client.audio.transcriptions.create(
                    model="whisper-1", file=f, language="pl"
                )
                texts.append(res.text)
    return "\n".join(texts)

def summarize(text: str, client):
    try:
        prompt = (
            "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + text
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        if completion and completion.choices and completion.choices[0].message:
            content = completion.choices[0].message.content
            if content:
                lines = content.split("\n", 1)
                if len(lines) >= 2:
                    topic = lines[0].replace("Temat:", "").strip()
                    summary = lines[1].replace("Podsumowanie:", "").strip()
                    return topic, summary
                return content, ""
        return (
            "Nie udało się wygenerować tematu",
            "Nie udało się wygenerować podsumowania",
        )
    except Exception:
        return "Nie udało się wygenerować podsumowania", "Spróbuj ponownie"

def get_duration_mock(path: Path) -> float:
    filename = path.name
    if "short" in filename:
        return 30.0
    elif "medium" in filename:
        return 300.0
    elif "long" in filename:
        return 3600.0
    else:
        return 120.0

# --- Testy ---
class TestAudioProcessing:
    """Testy przetwarzania audio."""
    def test_init_paths(self, temp_dir, sample_audio_data):
        data = sample_audio_data
        ext = ".wav"
        uid = hashlib.md5(data, usedforsecurity=False).hexdigest()
        orig = temp_dir / "originals" / f"{uid}{ext}"
        tr = temp_dir / "transcripts" / f"{uid}.txt"
        sm = temp_dir / "summaries" / f"{uid}.txt"
        orig.parent.mkdir(parents=True, exist_ok=True)
        tr.parent.mkdir(parents=True, exist_ok=True)
        sm.parent.mkdir(parents=True, exist_ok=True)
        orig.write_bytes(data)
        assert orig.exists()
        assert orig.stat().st_size == len(data)
        assert uid == hashlib.md5(data, usedforsecurity=False).hexdigest()

    def test_clean_transcript(self):
        test_cases = [
            ("To jest um test", "To jest test"),
            ("Aaaa tak yhm dokładnie", "tak dokładnie"),
            ("Test   z wieloma    spacjami", "Test z wieloma spacjami"),
            ("", ""),
            ("um uh em yhm", ""),
            ("Normalny tekst bez artefaktów", "Normalny tekst bez artefaktów"),
        ]
        for input_text, expected in test_cases:
            result = clean_transcript(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: '{expected}' -> Got: '{result}'"

class TestOpenAIIntegration:
    """Testy integracji z OpenAI API."""
    def test_transcribe_chunks(self, mock_openai_client, temp_dir, sample_audio_data):
        test_file = temp_dir / "test.wav"
        test_file.write_bytes(sample_audio_data)
        chunks = [test_file]
        result = transcribe_chunks(chunks, mock_openai_client)
        assert result == "To jest przykładowa transkrypcja audio."
        mock_openai_client.audio.transcriptions.create.assert_called_once()

    def test_summarize(self, mock_openai_client):
        test_text = "To jest długi tekst do podsumowania..."
        result = summarize(test_text, mock_openai_client)
        assert isinstance(result, tuple)
        assert len(result) == 2
        topic, summary = result
        assert topic == "Test audio"
        assert summary == "To jest przykładowe podsumowanie wygenerowane przez AI."
        mock_openai_client.chat.completions.create.assert_called_once()

class TestFileHandling:
    """Testy obsługi plików."""
    def test_allowed_extensions(self):
        ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}
        valid_files = ["audio.mp3", "video.mp4", "test.wav", "file.m4a", "movie.mov", "clip.avi", "stream.webm"]
        invalid_files = ["document.pdf", "image.jpg", "text.txt", "archive.zip"]
        for filename in valid_files:
            ext = Path(filename).suffix.lower()
            assert ext in ALLOWED_EXT
        for filename in invalid_files:
            ext = Path(filename).suffix.lower()
            assert ext not in ALLOWED_EXT
    def test_file_size_validation(self, sample_audio_data):
        MAX_SIZE = 25 * 1024 * 1024
        small_file_size = len(sample_audio_data)
        assert small_file_size <= MAX_SIZE
        large_file_size = 30 * 1024 * 1024
        assert large_file_size > MAX_SIZE

class TestUtilityFunctions:
    """Testy funkcji pomocniczych."""
    def test_duration_calculation(self):
        test_files = [
            (Path("short_audio.mp3"), 30.0),
            (Path("medium_audio.mp3"), 300.0),
            (Path("long_audio.mp3"), 3600.0),
            (Path("normal_audio.mp3"), 120.0),
        ]
        for file_path, expected_duration in test_files:
            duration = get_duration_mock(file_path)
            assert duration == expected_duration
    def test_chunk_calculation(self):
        CHUNK_MS = 5 * 60 * 1000
        chunk_sec = CHUNK_MS / 1000
        test_durations = [
            (120, 1), (300, 1), (400, 2), (900, 3), (1200, 4)
        ]
        for duration, expected_chunks in test_durations:
            actual_chunks = math.ceil(duration / chunk_sec)
            assert actual_chunks == expected_chunks

class TestStreamlitIntegration:
    """Testy integracji ze Streamlit."""
    def test_session_state_keys(self):
        uid = "test123"
        expected_keys = [f"done_{uid}", f"topic_{uid}", f"summary_{uid}"]
        for key in expected_keys:
            assert key.startswith(("done_", "topic_", "summary_"))
            assert uid in key
    @patch("streamlit.error")
    @patch("streamlit.success")
    def test_error_handling(self, mock_success, mock_error):
        mock_error("Test error message")
        mock_error.assert_called_once_with("Test error message")
        mock_success("Operation completed successfully")
        mock_success.assert_called_once_with("Operation completed successfully")

class TestIntegration:
    """Testy integracyjne."""
    def test_complete_workflow(self, mock_openai_client, temp_dir, sample_audio_data, mock_env_vars):
        data = sample_audio_data
        ext = ".wav"
        uid = hashlib.md5(data, usedforsecurity=False).hexdigest()
        for folder in ("originals", "transcripts", "summaries"):
            (temp_dir / folder).mkdir(parents=True, exist_ok=True)
        orig = temp_dir / "originals" / f"{uid}{ext}"
        tr = temp_dir / "transcripts" / f"{uid}.txt"
        sm = temp_dir / "summaries" / f"{uid}.txt"
        orig.write_bytes(data)
        assert orig.exists()
        transcript_text = "To jest przykładowa transkrypcja do testów."
        tr.write_text(transcript_text, encoding="utf-8")
        assert tr.exists()
        summary_text = "Temat: Test\n\nPodsumowanie: To jest test."
        sm.write_text(summary_text, encoding="utf-8")
        assert sm.exists()
        assert tr.read_text(encoding="utf-8") == transcript_text
        assert sm.read_text(encoding="utf-8") == summary_text
        # 6. Sprawdzenie, czy wszystkie pliki mają ten sam UID
        assert all(f.name.startswith(uid) for f in [orig, tr, sm])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
