# =============================================================================
# Audio2Tekst - Test Configuration
# =============================================================================

import tempfile
from pathlib import Path

import pytest

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_AUDIO_FILES = {
    "mp3": TEST_DATA_DIR / "sample.mp3",
    "wav": TEST_DATA_DIR / "sample.wav",
    "m4a": TEST_DATA_DIR / "sample.m4a",
}


@pytest.fixture
def temp_dir():
    """Tworzy tymczasowy katalog dla testów."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_openai_client():
    """Mock klienta OpenAI do testów."""
    from unittest.mock import Mock

    client = Mock()

    # Mock transcription response
    mock_transcription = Mock()
    mock_transcription.text = "To jest przykładowa transkrypcja audio."
    client.audio.transcriptions.create.return_value = mock_transcription

    # Mock chat completion response
    mock_completion = Mock()
    mock_message = Mock()
    mock_message.content = "Temat: Test audio\n\nPodsumowanie: To jest przykładowe podsumowanie wygenerowane przez AI."
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    client.chat.completions.create.return_value = mock_completion

    return client


@pytest.fixture
def sample_audio_data():
    """Zwraca przykładowe dane audio do testów."""
    # Minimalne dane WAV (44 bajty header + cisza)
    wav_header = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00"
    return wav_header


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Ustawia zmienne środowiskowe dla testów."""
    test_env = {
        "OPENAI_API_KEY": "test-api-key-12345",
        "MAX_FILE_SIZE": "25",
        "CHUNK_DURATION": "5",
        "DEFAULT_LANGUAGE": "pl",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    return test_env
