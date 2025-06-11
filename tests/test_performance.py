"""
Audio2Tekst - Performance Tests
===============================

Testy wydajności i obciążenia dla aplikacji Audio2Tekst.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import psutil
import pytest


class TestPerformance:
    """Testy wydajności aplikacji."""

    def test_file_processing_time(self, sample_audio_data):
        """Test czasu przetwarzania plików."""
        # Symulacja przetwarzania pliku
        start_time = time.time()

        # Operacje na pliku
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(sample_audio_data)
            tmp_path = Path(tmp.name)

        # Symulacja czytania i przetwarzania
        data = tmp_path.read_bytes()
        assert len(data) == len(sample_audio_data)

        end_time = time.time()
        processing_time = end_time - start_time

        # Oczekujemy, że operacje na małym pliku zajmą mniej niż sekundę
        assert (
            processing_time < 1.0
        ), f"File processing took {processing_time:.2f}s, expected < 1.0s"

        # Cleanup
        tmp_path.unlink()

    def test_memory_usage(self, sample_audio_data):
        """Test zużycia pamięci podczas przetwarzania."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Symulacja przetwarzania wielu plików
        files_data = []
        for i in range(10):
            files_data.append(sample_audio_data * (i + 1))  # Różne rozmiary

        # Przetwarzanie
        for data in files_data:
            # Symulacja operacji na danych
            processed = data[: len(data) // 2]  # Przykładowa operacja
            assert len(processed) > 0

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Oczekujemy, że wzrost pamięci będzie rozsądny (< 100MB dla testów)
        assert (
            memory_increase < 100
        ), f"Memory increased by {memory_increase:.2f}MB, expected < 100MB"

    def test_concurrent_processing(self, mock_openai_client):
        """Test współbieżnego przetwarzania."""
        import queue
        import threading

        results = queue.Queue()

        def mock_transcribe(file_id):
            # Symulacja transkrypcji
            time.sleep(0.1)  # Krótkie opóźnienie
            results.put(f"Transcription for file {file_id}")

        # Uruchomienie kilku wątków
        threads = []
        for i in range(5):
            thread = threading.Thread(target=mock_transcribe, args=(i,))
            threads.append(thread)
            thread.start()

        # Oczekiwanie na zakończenie
        start_time = time.time()
        for thread in threads:
            thread.join()
        end_time = time.time()

        # Sprawdzenie wyników
        assert results.qsize() == 5

        # Czas równoległy powinien być krótszy niż sekwencyjny
        total_time = end_time - start_time
        assert (
            total_time < 1.0
        ), f"Concurrent processing took {total_time:.2f}s, expected < 1.0s"


class TestScalability:
    """Testy skalowalności."""

    def test_large_file_handling(self):
        """Test obsługi dużych plików."""
        # Symulacja dużego pliku
        large_file_size = 20 * 1024 * 1024  # 20MB
        MAX_SIZE = 25 * 1024 * 1024  # 25MB limit

        # Test sprawdzenia rozmiaru
        assert large_file_size <= MAX_SIZE, "Large file should be within limits"

        # Symulacja podziału na fragmenty
        CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks
        expected_chunks = (large_file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

        assert (
            expected_chunks == 4
        ), f"Expected 4 chunks for {large_file_size}B file, got {expected_chunks}"

    def test_multiple_users_simulation(self, mock_openai_client):
        """Symulacja wielu użytkowników."""
        import queue
        import threading

        results = queue.Queue()
        errors = queue.Queue()

        def simulate_user(user_id):
            try:
                # Symulacja workflow użytkownika
                time.sleep(0.05)  # Upload time

                # Mock transcription
                mock_openai_client.audio.transcriptions.create.return_value.text = (
                    f"Transcription for user {user_id}"
                )

                # Mock summarization
                mock_openai_client.chat.completions.create.return_value.choices[
                    0
                ].message.content = f"Summary for user {user_id}"

                results.put(f"Success for user {user_id}")

            except Exception as e:
                errors.put(f"Error for user {user_id}: {str(e)}")

        # Symulacja 10 równoczesnych użytkowników
        threads = []
        for i in range(10):
            thread = threading.Thread(target=simulate_user, args=(i,))
            threads.append(thread)
            thread.start()

        # Oczekiwanie na zakończenie
        for thread in threads:
            thread.join()

        # Sprawdzenie wyników
        assert (
            results.qsize() == 10
        ), f"Expected 10 successful operations, got {results.qsize()}"
        assert errors.qsize() == 0, f"Expected 0 errors, got {errors.qsize()}"


class TestResourceLimits:
    """Testy limitów zasobów."""

    def test_api_rate_limiting(self, mock_openai_client):
        """Test symulacji limitów API."""
        import time
        from unittest.mock import Mock

        # Mock rate limiting
        call_times = []

        def mock_api_call(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) > 3:  # Limit 3 calls
                raise Exception("Rate limit exceeded")
            return Mock(text="Success")

        mock_openai_client.audio.transcriptions.create.side_effect = mock_api_call
        # Test calls within limit
        for _ in range(3):  # zmieniono 'i' na '_' ponieważ nie jest używane
            result = mock_openai_client.audio.transcriptions.create()
            assert result.text == "Success"

        # Test call exceeding limit
        with pytest.raises(Exception, match="Rate limit exceeded"):
            mock_openai_client.audio.transcriptions.create()

    def test_disk_space_monitoring(self, temp_dir):
        """Test monitorowania miejsca na dysku."""
        # Sprawdzenie dostępnego miejsca
        import shutil

        total, used, free = shutil.disk_usage(temp_dir)
        free_gb = free / (1024**3)

        # Oczekujemy przynajmniej 1GB wolnego miejsca dla testów
        assert free_gb > 1.0, f"Insufficient disk space: {free_gb:.2f}GB available"

        # Symulacja sprawdzenia przed zapisem dużego pliku
        large_file_size_gb = 0.5  # 500MB
        assert free_gb > large_file_size_gb, "Not enough space for large file"


class TestCachePerformance:
    """Testy wydajności cache."""

    def test_cache_hit_performance(self):
        """Test wydajności trafień cache."""
        # Symulacja cache z dictionary
        cache = {}

        # Pierwsze wywołanie (cache miss)
        start_time = time.time()
        key = "test_key"
        if key not in cache:
            # Symulacja expensive operation
            time.sleep(0.1)
            cache[key] = "expensive_result"
        result1 = cache[key]
        miss_time = time.time() - start_time

        # Drugie wywołanie (cache hit)
        start_time = time.time()
        result2 = cache[key]
        hit_time = time.time() - start_time

        assert result1 == result2 == "expensive_result"
        assert (
            hit_time < miss_time / 10
        ), f"Cache hit ({hit_time:.4f}s) should be much faster than miss ({miss_time:.4f}s)"

    def test_cache_size_limits(self):
        """Test limitów rozmiaru cache."""
        MAX_CACHE_SIZE = 100
        cache = {}

        # Wypełnienie cache
        for i in range(MAX_CACHE_SIZE + 50):
            cache[f"key_{i}"] = f"value_{i}"

            # Symulacja LRU eviction
            if len(cache) > MAX_CACHE_SIZE:
                # Usuń najstarszy element (symulacja)
                oldest_key = next(iter(cache))
                del cache[oldest_key]

        assert (
            len(cache) <= MAX_CACHE_SIZE
        ), f"Cache size {len(cache)} exceeds limit {MAX_CACHE_SIZE}"


class TestNetworkPerformance:
    """Testy wydajności sieciowej."""

    def test_youtube_download_timeout(self):
        """Test timeout dla pobierania z YouTube."""
        import time

        def mock_youtube_download(url, timeout=30):
            # Symulacja pobierania
            start_time = time.time()
            time.sleep(0.1)  # Symulacja czasu pobierania

            if time.time() - start_time > timeout:
                raise TimeoutError("Download timeout")

            return b"mock_audio_data"

        # Test successful download
        result = mock_youtube_download("https://youtube.com/watch?v=test", timeout=1)
        assert result == b"mock_audio_data"

        # Test timeout (w prawdziwej implementacji)
        # Tutaj nie testujemy timeout, bo to zajęłoby zbyt długo

    @patch("requests.post")
    def test_api_response_time(self, mock_post):
        """Test czasu odpowiedzi API."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {"text": "Mock transcription"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Test API call timing
        start_time = time.time()
        # Symulacja wywołania API
        import requests

        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            json={"model": "whisper-1"},
            timeout=30,
        )  # Dodano timeout

        end_time = time.time()
        api_time = end_time - start_time

        assert response.status_code == 200
        assert api_time < 1.0, f"API call took {api_time:.2f}s, expected < 1.0s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
