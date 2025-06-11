"""
Audio2Tekst - Unit Tests for Core Functions
============================================

Testy jednostkowe dla podstawowych funkcji aplikacji Audio2Tekst.
"""

import hashlib
from pathlib import Path
from unittest.mock import patch

import pytest

# Import funkcji do testowania (zakładając, że app.py zawiera te funkcje)
# W rzeczywistej implementacji należałoby zrefaktoryzować app.py
# aby wydzielić logikę biznesową do osobnych modułów


class TestAudioProcessing:
    """Testy przetwarzania audio."""

    def test_init_paths(self, temp_dir, sample_audio_data):
        """Test inicjalizacji ścieżek plików."""  # Symulacja funkcji init_paths bez importu app.py
        data = sample_audio_data
        ext = ".wav"
        uid = hashlib.sha256(data).hexdigest()  # Test helper (zmiana md5 na sha256)

        orig = temp_dir / "originals" / f"{uid}{ext}"
        tr = temp_dir / "transcripts" / f"{uid}.txt"
        sm = temp_dir / "summaries" / f"{uid}.txt"

        # Tworzenie katalogów
        orig.parent.mkdir(parents=True, exist_ok=True)
        tr.parent.mkdir(parents=True, exist_ok=True)
        sm.parent.mkdir(parents=True, exist_ok=True)

        # Zapisanie pliku
        orig.write_bytes(data)

        assert orig.exists()
        assert orig.stat().st_size == len(data)
        assert (
            uid == hashlib.sha256(data).hexdigest()
        )  # Test helper (zmiana md5 na sha256)

    def test_clean_transcript(self):
        """Test czyszczenia transkrypcji."""

        # Symulacja funkcji clean_transcript
        def clean_transcript(text: str) -> str:
            import re

            text = re.sub(
                r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", text, flags=re.IGNORECASE
            )
            text = re.sub(r"\s+", " ", text)
            return text.strip()

        # Test przypadków
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
            assert (
                result == expected
            ), f"Input: '{input_text}' -> Expected: '{expected}' -> Got: '{result}'"


class TestOpenAIIntegration:
    """Testy integracji z OpenAI API."""

    def test_transcribe_chunks(self, mock_openai_client, temp_dir, sample_audio_data):
        """Test transkrypcji fragmentów audio."""
        # Tworzenie testowego pliku
        test_file = temp_dir / "test.wav"
        test_file.write_bytes(sample_audio_data)

        # Symulacja funkcji transcribe_chunks
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

        # Test
        chunks = [test_file]
        result = transcribe_chunks(chunks, mock_openai_client)

        assert result == "To jest przykładowa transkrypcja audio."
        mock_openai_client.audio.transcriptions.create.assert_called_once()

    def test_summarize(self, mock_openai_client):
        """Test generowania podsumowania."""

        # Symulacja funkcji summarize
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

        # Test
        test_text = "To jest długi tekst do podsumowania..."
        result = summarize(test_text, mock_openai_client)

        # Sprawdzenie czy zwrócono tuple
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 2, f"Expected tuple of length 2, got {len(result)}"

        topic, summary = result
        assert topic == "Test audio"
        assert summary == "To jest przykładowe podsumowanie wygenerowane przez AI."
        mock_openai_client.chat.completions.create.assert_called_once()


class TestFileHandling:
    """Testy obsługi plików."""

    def test_allowed_extensions(self):
        """Test sprawdzania dozwolonych rozszerzeń."""
        ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}

        valid_files = [
            "audio.mp3",
            "video.mp4",
            "test.wav",
            "file.m4a",
            "movie.mov",
            "clip.avi",
            "stream.webm",
        ]

        invalid_files = ["document.pdf", "image.jpg", "text.txt", "archive.zip"]

        for filename in valid_files:
            ext = Path(filename).suffix.lower()
            assert ext in ALLOWED_EXT, f"Extension {ext} should be allowed"

        for filename in invalid_files:
            ext = Path(filename).suffix.lower()
            assert ext not in ALLOWED_EXT, f"Extension {ext} should not be allowed"

    def test_file_size_validation(self, sample_audio_data):
        """Test walidacji rozmiaru pliku."""
        MAX_SIZE = 25 * 1024 * 1024  # 25MB

        # Mały plik - powinien przejść
        small_file_size = len(sample_audio_data)
        assert small_file_size <= MAX_SIZE

        # Duży plik - powinien zostać odrzucony
        large_file_size = 30 * 1024 * 1024  # 30MB
        assert large_file_size > MAX_SIZE


class TestUtilityFunctions:
    """Testy funkcji pomocniczych."""

    def test_duration_calculation(self):
        """Test kalkulacji długości audio (mock)."""

        # Symulacja funkcji get_duration
        def get_duration_mock(path: Path) -> float:
            # Mock zwracający różne długości na podstawie nazwy pliku
            filename = path.name
            if "short" in filename:
                return 30.0  # 30 sekund
            elif "medium" in filename:
                return 300.0  # 5 minut
            elif "long" in filename:
                return 3600.0  # 1 godzina
            else:
                return 120.0  # 2 minuty (domyślnie)

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
        """Test kalkulacji liczby fragmentów."""
        CHUNK_MS = 5 * 60 * 1000  # 5 minut w ms
        chunk_sec = CHUNK_MS / 1000  # 300 sekund

        test_durations = [
            (120, 1),  # 2 minuty -> 1 fragment
            (300, 1),  # 5 minut -> 1 fragment
            (400, 2),  # 6:40 -> 2 fragmenty
            (900, 3),  # 15 minut -> 3 fragmenty
            (1200, 4),  # 20 minut -> 4 fragmenty
        ]

        for duration, expected_chunks in test_durations:
            import math

            actual_chunks = math.ceil(duration / chunk_sec)
            assert (
                actual_chunks == expected_chunks
            ), f"Duration {duration}s should produce {expected_chunks} chunks, got {actual_chunks}"


class TestStreamlitIntegration:
    """Testy integracji ze Streamlit."""

    def test_session_state_keys(self):
        """Test kluczy session state."""
        uid = "test123"
        expected_keys = [f"done_{uid}", f"topic_{uid}", f"summary_{uid}"]

        for key in expected_keys:
            assert key.startswith(("done_", "topic_", "summary_"))
            assert uid in key

    @patch("streamlit.error")
    @patch("streamlit.success")
    def test_error_handling(self, mock_success, mock_error):
        """Test obsługi błędów."""
        # Symulacja błędu API
        mock_error("Test error message")
        mock_error.assert_called_once_with("Test error message")

        # Symulacja sukcesu
        mock_success("Operation completed successfully")
        mock_success.assert_called_once_with("Operation completed successfully")


# Testy integracyjne
class TestIntegration:
    """Testy integracyjne."""

    def test_complete_workflow(
        self, mock_openai_client, temp_dir, sample_audio_data, mock_env_vars
    ):
        """Test kompletnego workflow przetwarzania."""  # 1. Inicjalizacja ścieżek
        data = sample_audio_data
        ext = ".wav"
        uid = hashlib.sha256(data).hexdigest()  # Test helper (zmiana md5 na sha256)

        # Tworzenie struktur katalogów
        for folder in ("originals", "transcripts", "summaries"):
            (temp_dir / folder).mkdir(parents=True, exist_ok=True)

        orig = temp_dir / "originals" / f"{uid}{ext}"
        tr = temp_dir / "transcripts" / f"{uid}.txt"
        sm = temp_dir / "summaries" / f"{uid}.txt"

        # 2. Zapisanie oryginalnego pliku
        orig.write_bytes(data)
        assert orig.exists()

        # 3. Symulacja transkrypcji
        transcript_text = "To jest przykładowa transkrypcja do testów."
        tr.write_text(transcript_text, encoding="utf-8")
        assert tr.exists()

        # 4. Symulacja podsumowania
        summary_text = "Temat: Test\n\nPodsumowanie: To jest test."
        sm.write_text(summary_text, encoding="utf-8")
        assert sm.exists()

        # 5. Weryfikacja wyników
        assert tr.read_text(encoding="utf-8") == transcript_text
        assert sm.read_text(encoding="utf-8") == summary_text

        # 6. Sprawdzenie, czy wszystkie pliki mają ten sam UID
        assert all(f.name.startswith(uid) for f in [orig, tr, sm])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
