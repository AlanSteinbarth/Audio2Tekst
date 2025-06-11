"""
Audio2Tekst
=======================================

Ten moduł zawiera implementację aplikacji Streamlit do transkrypcji
plików audio i video na tekst oraz generowania ich podsumowań.

🚀 WERSJA 2.3.0 - CROSS-PLATFORM EDITION 🚀
- Uniwersalna kompatybilność z Windows, macOS i Linux
- Dodano automatyczne wykrywanie i obsługę różnych systemów operacyjnych
- Poprawiono ścieżki plików i komendy systemowe dla wszystkich platform
- Ulepszona obsługa enkodowania i plików tymczasowych
- Dodano sprawdzanie dostępności narzędzi systemowych (FFmpeg/FFprobe)
- Zwiększona stabilność i niezawodność na różnych środowiskach

Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
GitHub: https://github.com/AlanSteinbarth
Data: 11 czerwca 2025
Wersja: 2.3.0 (Cross-Platform Edition)

=======================================
SPIS TREŚCI (SEKCJE KODU)
=======================================
1. Importy i konfiguracja
2. Funkcje pomocnicze (system, ścieżki, walidacja)
3. Konfiguracja aplikacji i stałe
4. Przetwarzanie pliku (ścieżki, czyszczenie, walidacja)
5. Obsługa YouTube i plików lokalnych
6. Przygotowanie do transkrypcji
7. Odtwarzacz audio i pobieranie
8. Zarządzanie stanem sesji
9. Proces transkrypcji (split, transcribe, zapis)
10. Interfejs po transkrypcji (wyświetlanie, pobieranie)
11. Podsumowanie AI (generowanie, wyświetlanie, pobieranie)
12. Panel diagnostyczny (informacje o systemie)
13. Koniec aplikacji
=======================================
"""

# --- Importy systemowe ---
# Importujemy wszystkie niezbędne biblioteki do obsługi plików, systemu, logowania, przetwarzania audio i API
import hashlib  # Do generowania unikalnych identyfikatorów plików
import logging  # Do logowania zdarzeń i błędów
import math  # Do obliczeń matematycznych (np. dzielenie na fragmenty)
import os  # Do obsługi zmiennych środowiskowych
from pathlib import Path  # Do obsługi ścieżek plików
import platform  # Do wykrywania systemu operacyjnego
import re  # Do operacji na wyrażeniach regularnych
import shutil  # Do operacji na plikach i katalogach
import subprocess  # Do wywołań procesów zewnętrznych (ffmpeg, ffprobe)
import tempfile  # Do obsługi plików tymczasowych
import threading  # Do obsługi wątków (np. komunikaty o długich operacjach)
import time  # Do operacji na czasie
from typing import Optional  # Typowanie opcjonalne

from dotenv import load_dotenv  # Ładowanie zmiennych środowiskowych z pliku .env
import openai  # Klient OpenAI do transkrypcji i podsumowań

# --- Importy zewnętrzne ---
import streamlit as st  # Framework do budowy interfejsu webowego
from werkzeug.utils import secure_filename  # Bezpieczne operacje na nazwach plików
import yt_dlp  # Narzędzie do pobierania audio z YouTube

# --- Konfiguracja logowania ---
# Ustawiamy poziom logowania na INFO i tworzymy loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Funkcje pomocnicze dla kompatybilności systemów ---
def get_system_info() -> dict:
    """Zwraca informacje o systemie operacyjnym (platforma, architektura, wersja Pythona, itp.)."""
    return {
        "platform": platform.system().lower(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "is_windows": platform.system().lower() == "windows",
        "is_macos": platform.system().lower() == "darwin",
        "is_linux": platform.system().lower() == "linux",
    }


def find_executable(name: str) -> Optional[str]:
    """Znajduje ścieżkę do pliku wykonywalnego w systemie (np. ffmpeg, ffprobe)."""
    system_info = get_system_info()

    # Na Windows dodaj .exe jeśli nie ma rozszerzenia
    if system_info["is_windows"] and not name.endswith(".exe"):
        name += ".exe"

    # Sprawdź czy jest dostępny w PATH
    if shutil.which(name):
        return shutil.which(name)

    # Sprawdź typowe lokalizacje
    common_paths = []
    if system_info["is_windows"]:
        common_paths = [
            "C:\\ffmpeg\\bin",
            "C:\\Program Files\\ffmpeg\\bin",
            "C:\\Program Files (x86)\\ffmpeg\\bin",
        ]
    elif system_info["is_macos"]:
        common_paths = ["/usr/local/bin", "/opt/homebrew/bin", "/usr/bin"]
    else:  # Linux
        common_paths = ["/usr/bin", "/usr/local/bin", "/snap/bin"]

    for path in common_paths:
        full_path = Path(path) / name
        if full_path.exists() and full_path.is_file():
            return str(full_path)

    return None


def check_dependencies() -> dict:
    """Sprawdza dostępność wymaganych narzędzi systemowych (FFmpeg, FFprobe)."""
    dependencies = {
        "ffmpeg": find_executable("ffmpeg"),
        "ffprobe": find_executable("ffprobe"),
    }

    return {
        name: {"available": path is not None, "path": path}
        for name, path in dependencies.items()
    }


def get_safe_encoding() -> str:
    """Zwraca bezpieczne kodowanie dla systemu (UTF-8 lub UTF-8-sig dla Windows)."""
    system_info = get_system_info()

    if system_info["is_windows"]:
        # Windows może używać różnych kodowań
        return "utf-8-sig"  # BOM dla lepszej kompatybilności
    else:
        # Unix-like systemy standardowo używają UTF-8
        return "utf-8"


# --- Konfiguracja Streamlit ---
# Ustawienia strony i ładowanie zmiennych środowiskowych
st.set_page_config(page_title="Audio2Tekst", layout="wide")
# .env jest ładowany zawsze na starcie, przed pobraniem klucza API
load_dotenv()


# --- Konfiguracja OpenAI ---
def get_api_key():
    """Pobiera klucz OpenAI API: najpierw z .env/środowiska, potem (opcjonalnie) z inputu użytkownika."""
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        st.sidebar.success(
            "Wykryto klucz OpenAI API w .env lub środowisku. Używany jest ten klucz."
        )
        return env_key
    # Jeśli nie ma w środowisku, pokaż pole do wpisania
    return st.sidebar.text_input("Podaj swój OpenAI API Key", type="password")


api_key = get_api_key()
if not api_key:
    st.sidebar.warning(
        "Brak klucza OpenAI API. Dodaj go do pliku .env lub wpisz powyżej."
    )
    st.stop()
client = openai.OpenAI(api_key=api_key)

# --- Stałe i konfiguracja ścieżek ---
# Tworzymy katalogi na pliki oryginalne, transkrypcje i podsumowania
BASE_DIR = Path("uploads")
for folder in ("originals", "transcripts", "summaries"):
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}
MAX_SIZE = 25 * 1024 * 1024  # 25MB
CHUNK_MS = 5 * 60 * 1000  # 5 minut w ms

# --- Funkcje pomocnicze ---
# UWAGA: To jest ulepszona wersja programu Audio2Tekst
# Główne usprawnienia w wersji 2.3.0:
# ✅ Uniwersalna kompatybilność z Windows, macOS i Linux
# ✅ Automatyczne wykrywanie platformy i dostosowanie komend
# ✅ Poprawiona obsługa ścieżek plików i enkodowania
# ✅ Dodano sprawdzanie dostępności narzędzi systemowych
# ✅ Ulepszona obsługa plików tymczasowych
# ✅ Zwiększona stabilność na różnych środowiskach


def init_paths(file_data: bytes, file_ext: str):
    """
    Inicjalizuje ścieżki dla plików na podstawie zawartości (hash MD5 jako UID).

    Funkcja tworzy unikalny identyfikator pliku (UID) na podstawie jego zawartości używając MD5,
    następnie inicjalizuje ścieżki dla pliku oryginalnego, transkrypcji i podsumowania.
    Usuwa stare pliki o tym samym UID z innymi rozszerzeniami, aby uniknąć konfliktów.

    Args:
        file_data (bytes): Zawartość pliku audio/video
        file_ext (str): Rozszerzenie pliku (np. '.mp3', '.wav')

    Returns:
        tuple: (file_uid, orig_path, transcript_path, summary_path)
            - file_uid (str): Unikalny identyfikator pliku (MD5 hash)
            - orig_path (Path): Ścieżka do oryginalnego pliku
            - transcript_path (Path): Ścieżka do pliku transkrypcji
            - summary_path (Path): Ścieżka do pliku podsumowania
    """
    file_uid = hashlib.sha256(file_data).hexdigest()
    orig_path = BASE_DIR / "originals" / f"{file_uid}{file_ext}"
    transcript_path = BASE_DIR / "transcripts" / f"{file_uid}.txt"
    summary_path = BASE_DIR / "summaries" / f"{file_uid}.txt"
    # Usuń stare pliki o tym UID z innymi rozszerzeniami
    for audio_ext in [".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"]:
        old_path = BASE_DIR / "originals" / f"{file_uid}{audio_ext}"
        if old_path.exists() and old_path != orig_path:
            try:
                old_path.unlink()
            except OSError as cleanup_exc:
                logger.warning(
                    "Nie udało się usunąć starego pliku %s: %s", old_path, cleanup_exc
                )
    if not orig_path.exists():
        orig_path.write_bytes(file_data)
    return file_uid, orig_path, transcript_path, summary_path


# --- Automatyczne czyszczenie katalogu uploads/originals przy starcie aplikacji ---
def clean_uploads_originals():
    """Usuwa wszystkie pliki z katalogu uploads/originals przy starcie aplikacji."""
    originals_path = Path("uploads/originals")
    if originals_path.exists():
        for file in originals_path.iterdir():
            try:
                file.unlink()
            except OSError as e:
                logger.warning("Nie udało się usunąć pliku %s: %s", file, e)


clean_uploads_originals()


def validate_youtube_url(youtube_url: str) -> bool:
    """Sprawdza czy URL jest prawidłowym adresem YouTube (różne formaty linków)."""
    youtube_patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"(?:https?://)?(?:www\.)?youtu\.be/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+",
        r"(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+",
    ]

    return any(re.match(pattern, youtube_url.strip()) for pattern in youtube_patterns)


def download_youtube_audio(youtube_url: str):
    """
    Pobiera audio z filmu YouTube i konwertuje do formatu MP3, jeśli to konieczne.

    Funkcja waliduje URL YouTube, pobiera najlepszy dostępny format audio,
    a następnie konwertuje do MP3 jeśli plik nie jest już w obsługiwanym formacie audio.
    Obsługuje różne błędy pobierania i zapewnia szczegółowe komunikaty o błędach.

    Args:
        youtube_url (str): URL filmu YouTube do pobrania

    Returns:
        tuple: (file_data, file_extension)
            - file_data (bytes): Zawartość pliku audio
            - file_extension (str): Rozszerzenie pliku (np. '.mp3', '.wav')

    Raises:
        ValueError: Gdy URL jest nieprawidłowy
        RuntimeError: Gdy wystąpi błąd podczas pobierania lub konwersji
        FileNotFoundError: Gdy nie znaleziono pliku audio
    """
    if not validate_youtube_url(youtube_url):
        raise ValueError(
            "Nieprawidłowy adres YouTube. Wklej prawidłowy link do filmu YouTube."
        )

    tmpdir = tempfile.mkdtemp(prefix="audio2tekst_yt_")
    try:
        output_template = str(Path(tmpdir) / "%(id)s.%(ext)s")
        ydl_opts = {
            "format": "bestaudio[ext=webm]/bestaudio",
            "outtmpl": output_template,
            "quiet": True,
            "noplaylist": True,
            "extractaudio": True,
            "audioformat": "webm",
            "prefer_ffmpeg": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        for yt_file in Path(tmpdir).iterdir():
            if yt_file.suffix.lower() in ALLOWED_EXT and yt_file.is_file():
                # Jeśli plik jest już mp3 lub wav, zwróć bez konwersji
                if yt_file.suffix.lower() in [".mp3", ".wav"]:
                    file_data = yt_file.read_bytes()
                    return file_data, yt_file.suffix.lower()
                # W przeciwnym razie konwertuj do mp3
                ffmpeg_deps = check_dependencies()
                if not ffmpeg_deps["ffmpeg"]["available"]:
                    raise RuntimeError(
                        "FFmpeg nie jest dostępny – nie można przekonwertować do MP3."
                    )
                ffmpeg_bin = ffmpeg_deps["ffmpeg"]["path"]
                yt_mp3_path = yt_file.with_suffix(".mp3")
                ffmpeg_cmd = [ffmpeg_bin, "-y", "-i", str(yt_file), str(yt_mp3_path)]
                try:
                    subprocess.run(
                        ffmpeg_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                except subprocess.CalledProcessError as conversion_exc:
                    raise RuntimeError(
                        f"Błąd konwersji do MP3: {conversion_exc}"
                    ) from conversion_exc
                if yt_mp3_path.exists():
                    file_data = yt_mp3_path.read_bytes()
                    return file_data, ".mp3"
                else:
                    raise RuntimeError("Konwersja do MP3 nie powiodła się.")
        raise FileNotFoundError("Nie znaleziono pliku audio z YouTube")

    except (OSError, FileNotFoundError, RuntimeError, KeyError) as exc:
        error_msg = str(exc).lower()
        if "is not a valid url" in error_msg or "invalid url" in error_msg:
            raise ValueError(
                "Nieprawidłowy adres YouTube. Wklej prawidłowy link do filmu YouTube."
            ) from exc
        elif "video unavailable" in error_msg or "private video" in error_msg:
            raise RuntimeError(
                "Film jest niedostępny lub prywatny. Spróbuj inny film YouTube."
            ) from exc
        elif "sign in" in error_msg or "age restricted" in error_msg:
            raise RuntimeError(
                "Film wymaga logowania lub jest ograniczony wiekowo. Spróbuj inny film YouTube."
            ) from exc
        elif "copyright" in error_msg or "blocked" in error_msg:
            raise RuntimeError(
                "Film jest zablokowany lub ma ograniczenia autorskie. Spróbuj inny film YouTube."
            ) from exc
        elif "network" in error_msg or "connection" in error_msg:
            raise RuntimeError(
                "Błąd połączenia z YouTube. Sprawdź połączenie internetowe i spróbuj ponownie."
            ) from exc
        else:
            logger.error("Błąd podczas pobierania z YouTube: %s", str(exc))
            raise RuntimeError(
                "Wystąpił błąd podczas pobierania z YouTube. Sprawdź link i spróbuj ponownie."
            ) from exc
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError as cleanup_exc:
            logger.warning(
                "Nie udało się usunąć tymczasowego katalogu: %s", cleanup_exc
            )


def get_duration(file_path: Path) -> float:
    """
    Zwraca długość pliku audio/video w sekundach przy użyciu ffprobe.

    Funkcja wykorzystuje narzędzie ffprobe do analizy metadanych pliku
    i wyciągnięcia informacji o długości trwania w sekundach.

    Args:
        file_path (Path): Ścieżka do pliku audio/video

    Returns:
        float: Długość pliku w sekundach

    Raises:
        RuntimeError: Gdy ffprobe nie jest dostępne lub wystąpi błąd podczas analizy
    """
    # Sprawdź dostępność ffprobe
    dependencies_info = check_dependencies()
    if not dependencies_info["ffprobe"]["available"]:
        raise RuntimeError("FFprobe nie jest dostępne w systemie. Zainstaluj FFmpeg.")

    ffprobe_path = dependencies_info["ffprobe"]["path"]
    ffprobe_cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]

    try:
        result = subprocess.run(  # nosec B603 # Bezpieczne wywołanie ffprobe z walidowanymi argumentami
            ffprobe_cmd,
            capture_output=True,
            text=True,
            timeout=30,  # timeout dla bezpieczeństwa
            check=True,
        )
        return float(result.stdout.strip())
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Przekroczono czas oczekiwania na analizę pliku") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Błąd podczas analizy pliku: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Nie można odczytać długości pliku: {exc}") from exc


def split_audio(file_path: Path):
    """
    Dzieli długie pliki audio na mniejsze części do przetworzenia (chunking).

    Funkcja analizuje długość pliku audio i dzieli go na fragmenty o długości
    określonej przez CHUNK_MS (domyślnie 5 minut). Każdy fragment jest zapisywany
    jako oddzielny plik tymczasowy do dalszego przetwarzania przez OpenAI API.

    Args:
        file_path (Path): Ścieżka do oryginalnego pliku audio/video

    Returns:
        list[Path]: Lista ścieżek do plików fragmentów

    Raises:
        RuntimeError: Gdy FFmpeg nie jest dostępne lub wystąpi błąd podczas dzielenia
    """
    # Sprawdź dostępność ffmpeg
    dependencies_info = check_dependencies()
    if not dependencies_info["ffmpeg"]["available"]:
        raise RuntimeError("FFmpeg nie jest dostępne w systemie. Zainstaluj FFmpeg.")
    ffmpeg_exe_path = dependencies_info["ffmpeg"]["path"]
    duration = get_duration(file_path)
    seg_sec = CHUNK_MS / 1000
    parts = []

    for i in range(math.ceil(duration / seg_sec)):
        start = i * seg_sec
        length = seg_sec if (start + seg_sec) <= duration else (duration - start)

        # Utwórz tymczasowy plik w sposób bezpieczny dla wszystkich platform
        fd, tmp = tempfile.mkstemp(suffix=file_path.suffix, prefix="audio2tekst_")
        os.close(fd)
        tmp_path = Path(tmp)

        ffmpeg_cmd = [
            ffmpeg_exe_path,
            "-y",
            "-i",
            str(file_path),
            "-ss",
            str(start),
            "-t",
            str(length),
            "-c",
            "copy",
            str(tmp_path),
        ]

        try:
            subprocess.run(  # nosec B603 # Bezpieczne wywołanie ffmpeg z walidowanymi argumentami
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=300,  # 5 minut timeout
                check=True,
                text=True,
            )
            parts.append(tmp_path)
        except subprocess.TimeoutExpired as exc:
            if tmp_path.exists():
                tmp_path.unlink()
            raise RuntimeError(
                f"Przekroczono czas oczekiwania podczas dzielenia pliku (segment {i+1})"
            ) from exc
        except subprocess.CalledProcessError as exc:
            if tmp_path.exists():
                tmp_path.unlink()
            logger.error("FFmpeg error: %s", exc.stderr)
            raise RuntimeError(
                f"Błąd podczas dzielenia pliku (segment {i+1}): {exc}"
            ) from exc

    return parts


def clean_transcript(transcript_text: str) -> str:
    """
    Czyści transkrypcję z typowych artefaktów mowy.

    Usuwa często występujące w transkrypcjach słowa wypełniające
    jak "um", "uh", "em", "yhm" oraz wielokrotnie powtarzające się litery.
    Normalizuje białe znaki i usuwa nadmiarowe spacje.

    Args:
        transcript_text (str): Surowa transkrypcja do wyczyszczenia

    Returns:
        str: Wyczyszczona transkrypcja
    """
    cleaned_text = re.sub(
        r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", transcript_text, flags=re.IGNORECASE
    )
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text.strip()


def transcribe_chunks(audio_chunks, openai_client):
    """
    Transkrybuje podzielone fragmenty audio na tekst używając OpenAI Whisper API.

    Funkcja przetwarza listę fragmentów audio, wysyłając każdy do OpenAI Whisper API
    w celu transkrypcji. Obsługuje długie pliki poprzez przetwarzanie fragmentów,
    zapewnia szczegółową diagnostykę i obsługę błędów. Wyświetla postęp przetwarzania
    i informuje o problemach z poszczególnymi fragmentami.

    Args:
        audio_chunks (list[Path]): Lista ścieżek do fragmentów audio
        openai_client: Klient OpenAI API

    Returns:
        str: Połączona transkrypcja wszystkich fragmentów

    Features:
        - Sprawdzanie rozmiaru fragmentów
        - Czyszczenie transkrypcji z artefaktów
        - Diagnostyka pustych/problematycznych fragmentów
        - Automatyczne czyszczenie plików tymczasowych
        - Komunikaty o postępie dla długich plików
    """
    texts = []
    long_transcription_msg = "Plik audio poddawany transkrypcji jest bardzo duży. Potrzebuję więcej czasu. Cierpliwości..."
    show_long_msg = [False]
    empty_audio_chunks = []
    failed_audio_chunks = []

    def delayed_info():
        time.sleep(10)
        show_long_msg[0] = True
        st.info(long_transcription_msg)

    thread = threading.Thread(target=delayed_info)
    thread.start()
    with st.spinner("Transkrypcja w toku..."):
        for audio_idx, audio_chunk_file in enumerate(audio_chunks):
            chunk_size = (
                audio_chunk_file.stat().st_size if audio_chunk_file.exists() else 0
            )
            st.info(
                f"Fragment {audio_idx+1}/{len(audio_chunks)}: {audio_chunk_file} | Rozmiar: {chunk_size/1024:.1f} KB"
            )
            logger.info(
                "Fragment %d: %s | Rozmiar: %d bajtów",
                audio_idx + 1,
                audio_chunk_file,
                chunk_size,
            )
            if chunk_size == 0:
                st.warning(f"Fragment {audio_idx+1} jest pusty i zostaje pominięty.")
                logger.warning(
                    "Fragment %d (%s) jest pusty!", audio_idx + 1, audio_chunk_file
                )
                empty_audio_chunks.append(audio_chunk_file)
                continue
            try:
                if chunk_size <= MAX_SIZE:
                    with open(audio_chunk_file, "rb") as audio_file:
                        transcript_text = openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="pl",
                            response_format="text",
                        )
                        cleaned_transcript = clean_transcript(str(transcript_text))
                        if not cleaned_transcript.strip():
                            st.warning(
                                f"Fragment {audio_idx+1} nie został rozpoznany przez API (pusta odpowiedź)."
                            )
                            logger.warning(
                                "Fragment %d (%s) – API zwróciło pustą odpowiedź.",
                                audio_idx + 1,
                                audio_chunk_file,
                            )
                            failed_audio_chunks.append(audio_chunk_file)
                        texts.append(cleaned_transcript)
                else:
                    st.warning(
                        f"Fragment {audio_idx+1} przekracza maksymalny rozmiar {MAX_SIZE/1024/1024:.1f} MB i zostaje pominięty."
                    )
                    logger.warning(
                        "Fragment %d (%s) przekracza maksymalny rozmiar.",
                        audio_idx + 1,
                        audio_chunk_file,
                    )
                    failed_audio_chunks.append(audio_chunk_file)
            except (OSError, openai.OpenAIError) as exc:
                logger.error(
                    "Błąd podczas transkrypcji fragmentu %s: %s",
                    audio_chunk_file,
                    str(exc),
                )
                st.error(f"Błąd podczas transkrypcji fragmentu {audio_idx+1}: {exc}")
                failed_audio_chunks.append(audio_chunk_file)
            finally:
                try:
                    if audio_chunk_file.exists():
                        audio_chunk_file.unlink()
                except OSError as cleanup_exc:
                    logger.warning(
                        "Nie udało się usunąć pliku tymczasowego %s: %s",
                        audio_chunk_file,
                        cleanup_exc,
                    )
    # Diagnostyka po zakończeniu transkrypcji
    if empty_audio_chunks:
        st.warning(
            f"Liczba pustych fragmentów: {len(empty_audio_chunks)}. Możesz pobrać problematyczne fragmenty do analizy poniżej."
        )
        for empty_idx, empty_chunk_file in enumerate(empty_audio_chunks):
            if empty_chunk_file.exists():
                st.download_button(
                    f"Pobierz pusty fragment {empty_idx+1}",
                    empty_chunk_file.read_bytes(),
                    file_name=f"pusty_fragment_{empty_idx+1}{empty_chunk_file.suffix}",
                )
    if failed_audio_chunks:
        st.warning(
            f"Liczba fragmentów z błędem/pustą odpowiedzią: {len(failed_audio_chunks)}. Możesz pobrać problematyczne fragmenty do analizy poniżej."
        )
        for fail_idx, fail_chunk_file in enumerate(failed_audio_chunks):
            if fail_chunk_file.exists():
                st.download_button(
                    f"Pobierz problematyczny fragment {fail_idx+1}",
                    fail_chunk_file.read_bytes(),
                    file_name=f"problem_fragment_{fail_idx+1}{fail_chunk_file.suffix}",
                )
    return "\n".join(texts)


def summarize(input_text: str, openai_client):
    """
    Generuje temat i podsumowanie z transkrypcji przy użyciu OpenAI GPT-3.5.

    Funkcja analizuje długość tekstu i automatycznie dzieli długie transkrypcje
    na fragmenty, aby zmieścić się w limitach OpenAI API. Dla każdego fragmentu
    generuje częściowe podsumowanie, a następnie tworzy finalne podsumowanie
    z wszystkich części. Obsługuje różne błędy API i zapewnia szczegółowe logowanie.

    Args:
        input_text (str): Tekst transkrypcji do podsumowania
        openai_client: Klient OpenAI API

    Returns:
        tuple: (topic, summary)
            - topic (str): Temat w jednym zdaniu
            - summary (str): Podsumowanie w 3-5 zdaniach

    Features:
        - Automatyczne dzielenie długich tekstów (>8000 znaków)
        - Hierarchiczne podsumowywanie (fragmenty → częściowe → finalne)
        - Obsługa błędów quota/billing OpenAI
        - Szczegółowe logowanie do pliku
        - Komunikaty o postępie dla użytkownika
    """
    log_path = Path("logs/summary_errors.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Usunięto komunikat o długim tekście
    logger.info("Rozpoczynam summarize() - długość tekstu: %s znaków", len(input_text))

    class OpenAIAPIError(Exception):
        """Własny wyjątek dla błędów OpenAI API."""

    try:
        MAX_CHUNK = 8000  # znaków na fragment (bezpieczny limit)
        if len(input_text) > MAX_CHUNK:
            logger.info("Tekst jest długi - dzielę na fragmenty")
            text_chunks = [
                input_text[i : i + MAX_CHUNK]
                for i in range(0, len(input_text), MAX_CHUNK)
            ]
            logger.info("Podzielono na %s fragmentów", len(text_chunks))
            partial_summaries = []
            for text_idx, text_chunk in enumerate(text_chunks):
                logger.info(
                    "Przetwarzam fragment %s/%s", text_idx + 1, len(text_chunks)
                )
                with st.spinner(
                    f"Podsumowywanie fragmentu {text_idx+1}/{len(text_chunks)}..."
                ):
                    try:
                        prompt = (
                            f"Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami (fragment {text_idx+1}/{len(text_chunks)}):\n"
                            + text_chunk
                        )
                        completion = openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=300,
                        )
                        if (
                            completion
                            and completion.choices
                            and completion.choices[0].message
                        ):
                            content = completion.choices[0].message.content
                            partial_summaries.append(content)
                        else:
                            raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI")
                    except (openai.OpenAIError, OpenAIAPIError) as exc:
                        msg = f"Błąd fragmentu {text_idx+1}: {exc}\n"
                        logger.error(msg)
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(
                                f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
                            )
                        st.error(
                            f"Błąd podczas podsumowywania fragmentu {text_idx+1}: {exc}"
                        )
                        return "Błąd podczas podsumowywania fragmentu", str(exc)
            logger.info("Zebrałem %s częściowych podsumowań", len(partial_summaries))
            if not partial_summaries:
                st.error(
                    "Nie udało się wygenerować żadnego podsumowania fragmentów. Spróbuj ponownie lub sprawdź logi."
                )
                logger.error(
                    "Brak partial_summaries - nie można wygenerować końcowego podsumowania."
                )
                return (
                    "Nie udało się wygenerować podsumowania",
                    "Brak podsumowań fragmentów.",
                )
            with st.spinner("Tworzenie końcowego podsumowania..."):
                try:
                    final_prompt = (
                        "Oto podsumowania fragmentów długiego tekstu. Na ich podstawie podaj jeden temat i jedno podsumowanie całości (3-5 zdań):\n"
                        + "\n".join(partial_summaries)
                    )
                    logger.info("Prompt do modelu (final): %s...", final_prompt[:200])
                    completion = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": final_prompt}],
                        max_tokens=300,
                    )
                    if (
                        completion
                        and completion.choices
                        and completion.choices[0].message
                    ):
                        content = completion.choices[0].message.content
                        logger.info("Odpowiedź modelu (final): %s...", content[:200])
                        lines = content.splitlines() if content else []
                        final_topic = (
                            lines[0] if lines else "Nie udało się wygenerować tematu"
                        )
                        final_summary = (
                            " ".join(lines[1:])
                            if len(lines) > 1
                            else "Nie udało się wygenerować podsumowania"
                        )
                        logger.info(
                            "Zwracam: topic='%s...', summary='%s...'",
                            final_topic[:50],
                            final_summary[:50],
                        )
                        return final_topic, final_summary
                    else:
                        logger.error("Brak odpowiedzi z modelu OpenAI (final)")
                        raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI (final)")
                except (openai.OpenAIError, OpenAIAPIError) as exc:
                    msg = f"Błąd końcowego podsumowania: {exc}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    st.error(f"Błąd podczas generowania końcowego podsumowania: {exc}")
                    return "Błąd podczas generowania końcowego podsumowania", str(exc)
        else:
            logger.info("Tekst jest krótki - bezpośrednie podsumowanie")
            with st.spinner("Podsumowywanie tekstu..."):
                try:
                    prompt = (
                        "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n"
                        + input_text
                    )
                    completion = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=300,
                    )
                    if (
                        completion
                        and completion.choices
                        and completion.choices[0].message
                    ):
                        content = completion.choices[0].message.content
                        logger.info(
                            "Otrzymano krótkie podsumowanie: %s...", content[:100]
                        )
                        lines = content.splitlines() if content else []
                        short_topic = (
                            lines[0] if lines else "Nie udało się wygenerować tematu"
                        )
                        short_summary = (
                            " ".join(lines[1:])
                            if len(lines) > 1
                            else "Nie udało się wygenerować podsumowania"
                        )
                        logger.info(
                            "Zwracam: topic='%s...', summary='%s...'",
                            short_topic[:50],
                            short_summary[:50],
                        )
                        return short_topic, short_summary
                    else:
                        raise OpenAIAPIError(
                            "Brak odpowiedzi z modelu OpenAI (krótki tekst)"
                        )
                except (openai.OpenAIError, OpenAIAPIError) as exc:
                    msg = f"Błąd podsumowania krótkiego tekstu: {exc}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    st.error(f"Błąd podczas podsumowywania tekstu: {exc}")
                    return "Błąd podczas podsumowywania tekstu", str(exc)
    except (openai.OpenAIError, OpenAIAPIError) as exc:
        # Obsługa błędu braku środków/quota w OpenAI
        if (
            "insufficient_quota" in str(exc).lower()
            or "you exceeded your current quota" in str(exc).lower()
            or "error code: 429" in str(exc).lower()
        ):
            st.error(
                "Brak środków lub limitu na koncie OpenAI. Sprawdź swój plan i limity na https://platform.openai.com/account/billing."
            )
            logger.error("Błąd quota (429/insufficient_quota): %s", exc)
            return "Brak środków na koncie OpenAI", str(exc)
        msg = f"Błąd ogólny podsumowania: {exc}\n"
        logger.error(msg)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
        st.error(f"Błąd ogólny podczas podsumowywania: {exc}")
        return "Błąd ogólny podczas podsumowywania", str(exc)

    return (
        "Nie udało się wygenerować podsumowania",
        "Spróbuj ponownie lub skontaktuj się z administratorem",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFEJS UŻYTKOWNIKA - GŁÓWNA APLIKACJA STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════════

# --- Sekcja 1: Panel boczny - Wybór źródła audio ---
# Użytkownik może wybrać między plikiem lokalnym a linkiem YouTube
src = st.sidebar.radio("Wybierz źródło audio:", ["Plik lokalny", "YouTube"])

# --- Sekcja 2: Inicjalizacja zmiennych i stanu sesji ---
# Zmienne do przechowywania danych pliku i obsługi błędów
data, ext = None, None
error_message = None

# --- Sekcja 3: Zarządzanie stanem sesji dla YouTube ---
# Flagi zapobiegające dublowaniu pobierania i umożliwiające czyszczenie starych danych
if "yt_success" not in st.session_state:
    st.session_state["yt_success"] = False
if "yt_data" not in st.session_state:
    st.session_state["yt_data"] = None
if "yt_ext" not in st.session_state:
    st.session_state["yt_ext"] = None

if src == "YouTube":
    url = st.sidebar.text_input("Wklej adres www z YouTube:")
    # --- RESET STANU PO ZMIANIE URL ---
    prev_url = st.session_state.get("yt_prev_url", None)
    if url and url != prev_url:
        # Usuwanie starych kluczy sesji i plików powiązanych z poprzednim UID
        keys_to_remove = []
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and (
                k.startswith("done_")
                or k.startswith("topic_")
                or k.startswith("summary_")
                or k.startswith("yt_")
            ):
                keys_to_remove.append(k)
        for k in keys_to_remove:
            del st.session_state[
                k
            ]  # Usuń pliki powiązane z poprzednim UID (jeśli istnieje)
        prev_uid = st.session_state.get("yt_prev_uid", None)
        if prev_uid:
            for folder in (
                BASE_DIR / "originals",
                BASE_DIR / "transcripts",
                BASE_DIR / "summaries",
            ):
                for ext_suffix in (
                    ".mp3",
                    ".wav",
                    ".m4a",
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".webm",
                    ".txt",
                ):
                    file_to_remove = folder / f"{prev_uid}{ext_suffix}"
                    if file_to_remove.exists():
                        try:
                            file_to_remove.unlink()
                        except OSError as cleanup_exc:
                            logger.warning(
                                "Nie udało się usunąć pliku %s: %s",
                                file_to_remove,
                                cleanup_exc,
                            )
        # Resetuj flagi yt
        st.session_state["yt_success"] = False
        st.session_state["yt_data"] = None
        st.session_state["yt_ext"] = None
        st.session_state["yt_prev_uid"] = None
        st.session_state["yt_prev_url"] = url

    # --- Sekcja 4A: Pobieranie audio z YouTube ---
    # Sprawdzenie czy audio już zostało pobrane (cache w session_state)
    if (
        st.session_state.get("yt_success")
        and st.session_state.get("yt_data")
        and st.session_state.get("yt_ext")
    ):
        data = st.session_state["yt_data"]
        ext = st.session_state["yt_ext"]
        st.success("Pomyślnie pobrano audio z YouTube!")
    elif url:
        # Pobieranie nowego pliku z YouTube z obsługą błędów
        try:
            with st.spinner("Pobieranie audio z YouTube..."):
                data, ext = download_youtube_audio(url)
                if not data or not isinstance(data, bytes):
                    raise RuntimeError(
                        "Nie udało się pobrać pliku audio z YouTube lub plik jest uszkodzony."
                    )
                st.session_state["yt_success"] = True
                st.session_state["yt_data"] = data
                st.session_state["yt_ext"] = ext
                uid, _, _, _ = init_paths(data, ext)
                st.session_state["yt_prev_uid"] = uid
                st.session_state["yt_prev_url"] = url
                st.success("Pomyślnie pobrano audio z YouTube!")
        except ValueError as e:
            st.warning(f"⚠️ {str(e)}")
            st.session_state["yt_success"] = False
            st.session_state["yt_data"] = None
            st.session_state["yt_ext"] = None
            st.stop()
        except RuntimeError as e:
            st.error(f"❌ {str(e)}")
            st.session_state["yt_success"] = False
            st.session_state["yt_data"] = None
            st.session_state["yt_ext"] = None
            st.stop()
        except (OSError, KeyError, TypeError) as e:
            st.error(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}")
            logger.error("Nieoczekiwany błąd podczas pobierania z YouTube: %s", str(e))
            st.session_state["yt_success"] = False
            st.session_state["yt_data"] = None
            st.session_state["yt_ext"] = None
            st.stop()

        # Cache'owanie danych po pobraniu
        data = st.session_state["yt_data"]
        ext = st.session_state["yt_ext"]
    else:
        # Brak URL - wyczyść stan i zatrzymaj
        st.session_state["yt_success"] = False
        st.session_state["yt_data"] = None
        st.session_state["yt_ext"] = None
        st.stop()

# --- Sekcja 4B: Obsługa plików lokalnych ---
else:
    # Upload pliku przez użytkownika z ograniczeniem typów
    up = st.sidebar.file_uploader(
        "Wybierz plik", type=[e.strip(".") for e in ALLOWED_EXT]
    )
    if up:
        data, ext = up.read(), Path(secure_filename(up.name)).suffix.lower()
    else:
        st.stop()

# --- Sekcja 5: Walidacja danych ---
# Sprawdzenie czy mamy dane do przetworzenia
if data is None or ext is None:
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# PRZETWARZANIE PLIKU - PRZYGOTOWANIE DO TRANSKRYPCJI
# ═══════════════════════════════════════════════════════════════════════════════

# --- Sekcja 6: Inicjalizacja ścieżek i metadanych ---
# Tworzenie UID na podstawie zawartości pliku i przygotowanie ścieżek
uid, orig, tr, sm = init_paths(data, ext)

# Diagnostyka: informacje o pliku
file_size = orig.stat().st_size if orig.exists() else 0
st.info(
    f"Plik do transkrypcji: {orig} | Rozmiar: {file_size/1024:.1f} KB | Format: {ext}"
)
logger.info(
    "Plik do transkrypcji: %s | Rozmiar: %d bajtów | Format: %s", orig, file_size, ext
)

# --- Sekcja 7: Przygotowanie pliku do transkrypcji ---
# Whisper/OpenAI obsługuje bezpośrednio: mp3, wav, m4a, webm, mp4
# Konwersja do WAV tylko w przypadku problemów ze split_audio
split_input = orig

# --- Sekcja 8: Odtwarzacz audio i opcje pobierania ---
st.audio(orig.read_bytes(), format=ext.lstrip("."))

# Przycisk pobierania audio (umieszczony bezpośrednio pod odtwarzaczem)
if ext in [".mp3", ".wav", ".m4a"]:
    st.download_button("Pobierz audio", orig.read_bytes(), file_name=f"{uid}{ext}")
else:
    # Konwersja do MP3 na żądanie dla plików video (MP4, WEBM, MOV, AVI)
    mp3_path = orig.with_suffix(".mp3")
    if not mp3_path.exists():
        deps_info = check_dependencies()
        if not deps_info["ffmpeg"]["available"]:
            st.warning("FFmpeg nie jest dostępny – nie można przekonwertować do MP3.")
        else:
            ffmpeg_path = deps_info["ffmpeg"]["path"]
            ffmpeg_command = [ffmpeg_path, "-y", "-i", str(orig), str(mp3_path)]
            try:
                subprocess.run(
                    ffmpeg_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            except subprocess.CalledProcessError as conversion_exc:
                st.warning(f"Błąd konwersji do MP3: {conversion_exc}")
    if mp3_path.exists():
        st.download_button(
            "Pobierz audio (MP3)", mp3_path.read_bytes(), file_name=f"{uid}.mp3"
        )
    else:
        st.download_button(
            "Pobierz audio (oryginał)", orig.read_bytes(), file_name=f"{uid}{ext}"
        )

# --- Sekcja 9: Zarządzanie stanu sesji ---
# Tworzenie unikalnych kluczy sesji dla danego pliku (UID)
# Pozwala na obsługę wielu plików w jednej sesji Streamlit bez konfliktów
done_key = f"done_{uid}"  # Czy transkrypcja została wykonana
topic_key = f"topic_{uid}"  # Temat podsumowania
sum_key = f"summary_{uid}"  # Treść podsumowania

# Inicjalizacja kluczy sesji z wartościami domyślnymi
for key, default in [(done_key, False), (topic_key, ""), (sum_key, "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ═══════════════════════════════════════════════════════════════════════════════
# PROCES TRANSKRYPCJI - PRZETWARZANIE AUDIO NA TEKST
# ═══════════════════════════════════════════════════════════════════════════════

# --- Sekcja 10: Sprawdzenie stanu transkrypcji ---
# Sprawdzamy czy transkrypcja już istnieje w pliku
transcript_exists = tr.exists() and tr.stat().st_size > 0

# --- Sekcja 11: Proces transkrypcji ---
# Główny proces transkrypcji uruchamiany przyciskiem
if st.button("Transkrybuj") and not st.session_state[done_key]:
    try:
        # Krok 1: Podział pliku na fragmenty
        chunks = split_audio(split_input)
        st.info(f"Liczba fragmentów audio: {len(chunks)}")
        logger.info("Liczba fragmentów audio po split_audio: %d", len(chunks))

        # Krok 2: Diagnostyka fragmentów
        empty_audio_chunks_diag = []
        for diag_idx, diag_chunk in enumerate(chunks):
            size = diag_chunk.stat().st_size if diag_chunk.exists() else 0
            st.write(
                f"Fragment {diag_idx+1}: {diag_chunk} | Rozmiar: {size/1024:.1f} KB"
            )
            if size == 0:
                empty_audio_chunks_diag.append(diag_chunk)

        # Krok 3: Walidacja fragmentów
        if not chunks:
            st.error(
                "Nie udało się podzielić pliku na fragmenty. Sprawdź format pliku lub spróbuj ponownie."
            )
            st.stop()

        if empty_audio_chunks_diag:
            st.warning(
                f"UWAGA: {len(empty_audio_chunks_diag)} fragment(ów) ma rozmiar 0 bajtów i nie zostanie przetworzonych. Sprawdź źródłowy plik audio lub format."
            )
            logger.warning(
                "Fragmenty o rozmiarze 0 bajtów: %s",
                [str(c) for c in empty_audio_chunks_diag],
            )

        # Krok 4: Transkrypcja fragmentów
        transcription_text = transcribe_chunks(chunks, client)

        # Krok 5: Walidacja wyników transkrypcji
        if not transcription_text.strip():
            st.error(
                "Transkrypcja nie powiodła się lub plik jest pusty/nieobsługiwany. Sprawdź format pliku lub spróbuj ponownie."
            )
            logger.error(
                "Transkrypcja nie powiodła się – brak tekstu po transkrypcji. Liczba fragmentów: %d, puste fragmenty: %d",
                len(chunks),
                len(empty_audio_chunks_diag),
            )
            st.stop()

        # Krok 6: Zapis transkrypcji do pliku
        encoding = get_safe_encoding()
        tr.write_text(transcription_text, encoding=encoding)

        # Krok 7: Aktualizacja stanu sesji
        st.session_state[done_key] = True
        st.session_state[topic_key] = ""
        st.session_state[sum_key] = ""

    except (OSError, ValueError) as e:
        # Globalna obsługa błędów transkrypcji
        logger.error("Błąd podczas transkrypcji: %s", e)
        st.error(f"❌ Błąd podczas transkrypcji: {e}")
        st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFEJS PO TRANSKRYPCJI - WYŚWIETLANIE I PODSUMOWANIE
# ═══════════════════════════════════════════════════════════════════════════════

# --- Sekcja 12: Wyświetlanie transkrypcji ---
# Panel wyświetlania transkrypcji po zakończonym procesie lub wczytaniu istniejącego pliku
if st.session_state[done_key] or transcript_exists:
    encoding = get_safe_encoding()
    transcript = tr.read_text(encoding=encoding) if tr.exists() else ""

    st.subheader("Transkrypt:")
    st.text_area("Transkrypcja", transcript, height=300)

    # Przycisk pobierania transkrypcji
    st.download_button(
        "Pobierz transkrypt", transcript, file_name=f"{uid}_transkrypt.txt"
    )

    # --- Sekcja 13: Proces podsumowania ---
    # Generowanie tematu i podsumowania z transkrypcji
    if st.button("Podsumuj"):
        result_topic, result_summary = summarize(transcript, client)
        st.session_state[topic_key] = result_topic
        st.session_state[sum_key] = result_summary

    # --- Sekcja 14: Wyświetlanie podsumowania ---
    # Panel wyświetlania wygenerowanego tematu i podsumowania
    if st.session_state[topic_key] or st.session_state[sum_key]:
        st.subheader("Temat:")
        st.write(st.session_state[topic_key])

        st.subheader("Podsumowanie:")
        st.write(st.session_state[sum_key])

        # Przycisk pobierania podsumowania
        st.download_button(
            "Pobierz podsumowanie",
            st.session_state[sum_key],
            file_name=f"{uid}_podsumowanie.txt",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL INFORMACJI O SYSTEMIE - DIAGNOSTYKA I DEBUGGING
# ═══════════════════════════════════════════════════════════════════════════════

# --- Sekcja 15: Panel informacji o systemie ---
# Rozwijany panel z informacjami technicznymi o środowisku
with st.sidebar.expander("ℹ️ Informacje o systemie"):
    sys_info = get_system_info()
    deps_info = check_dependencies()

    st.write("**Platforma:**", sys_info["platform"].title())
    st.write("**Architektura:**", sys_info["architecture"])
    st.write("**Python:**", sys_info["python_version"])

    st.write("**Zależności:**")
    for tool, info in deps_info.items():
        status = "✅ Dostępne" if info["available"] else "❌ Niedostępne"
        st.write(f"- {tool.upper()}: {status}")
        if info["available"] and info["path"]:
            st.write(f"  📁 Ścieżka: `{info['path']}`")

    st.write("**Kodowanie:**", get_safe_encoding())
    st.write("**Obsługiwane formaty:**", ", ".join(ALLOWED_EXT))
    st.write("**Maksymalny rozmiar:**", f"{MAX_SIZE/1024/1024:.1f} MB")
    st.write("**Długość fragmentu:**", f"{CHUNK_MS/1000/60:.0f} minut")

# ═══════════════════════════════════════════════════════════════════════════════
# KONIEC APLIKACJI
# ═══════════════════════════════════════════════════════════════════════════════
