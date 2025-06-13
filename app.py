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
import platform  # Do wykrywania systemu operacyjnego
import re  # Do operacji na wyrażeniach regularnych
import shutil  # Do operacji na plikach i katalogach
import subprocess  # nosec B404 # Bezpieczne wywoływanie FFmpeg
import tempfile  # Do obsługi plików tymczasowych
import threading  # Do obsługi wątków (np. komunikaty o długich operacjach)
import time  # Do operacji na czasie
from pathlib import Path  # Do obsługi ścieżek plików
from typing import Optional  # Typowanie opcjonalne

import openai  # Klient OpenAI do transkrypcji i podsumowań

# --- Importy zewnętrzne ---
import streamlit as st  # Framework do budowy interfejsu webowego
import yt_dlp  # Narzędzie do pobierania audio z YouTube
from dotenv import load_dotenv  # Ładowanie zmiennych środowiskowych z pliku .env
import traceback  # Do logowania pełnych tracebacków

# --- Konfiguracja logowania ---
# Ustawiamy poziom logowania na INFO i tworzymy loggera
logging.basicConfig(level=logging.INFO, encoding="utf-8")
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


# Nowa funkcja do weryfikacji klucza
def verify_api_key(key_to_verify: str) -> bool:
    """Sprawdza poprawność klucza OpenAI API."""
    if not key_to_verify:
        st.session_state.api_key_error_message = "Klucz API nie może być pusty."
        return False
    try:
        temp_client = openai.OpenAI(api_key=key_to_verify)
        temp_client.models.list()  # Proste zapytanie testowe
        st.session_state.api_key_error_message = "" # Wyczyszczenie błędu po sukcesie
        return True
    except openai.AuthenticationError:
        st.session_state.api_key_error_message = "Nieprawidłowy klucz OpenAI API. Sprawdź, czy klucz jest poprawny i aktywny."
        return False
    except openai.RateLimitError:
        st.session_state.api_key_error_message = "Przekroczono limit zapytań dla tego klucza API lub problem z subskrypcją."
        return False
    except openai.APIConnectionError:
        st.session_state.api_key_error_message = "Błąd połączenia z serwerami OpenAI. Sprawdź swoje połączenie internetowe."
        return False
    except Exception as exc:
        logger.error("Nieoczekiwany błąd podczas weryfikacji klucza API: %s", exc)
        st.session_state.api_key_error_message = f"Wystąpił nieoczekiwany błąd podczas weryfikacji klucza: {str(exc)}"
        return False

# --- Konfiguracja Streamlit ---
st.set_page_config(page_title="Audio2Tekst", layout="wide")
load_dotenv()


# --- Inicjalizacja domyślnych wartości stanu sesji ---
if "api_key_verified" not in st.session_state:
    st.session_state.api_key_verified = False
if "api_key_error_message" not in st.session_state:
    st.session_state.api_key_error_message = ""
if "api_key_input_changed" not in st.session_state:
    st.session_state.api_key_input_changed = False
if "current_input_key" not in st.session_state:
    st.session_state.current_input_key = ""

# Sprawdzenie klucza z .env przy pierwszym uruchomieniu, jeśli nie został jeszcze zweryfikowany
# Ta logika zostanie uruchomiona tylko raz na sesję, chyba że api_key_verified zostanie zresetowane
if not st.session_state.get("initial_env_key_check_done", False):
    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        st.session_state.api_key = env_api_key # Zapisz klucz z .env do stanu sesji
        if verify_api_key(env_api_key):
            st.session_state.api_key_verified = True
            # Komunikat o sukcesie może być wyświetlony później, jeśli chcemy
        else:
            # Błąd jest już w st.session_state.api_key_error_message
            # Ustawiamy, że klucz z .env był, ale jest niepoprawny
            st.session_state.env_key_invalid = True 
    st.session_state.initial_env_key_check_done = True

if "env_key_invalid" not in st.session_state:
    st.session_state.env_key_invalid = False

# --- Główny interfejs aplikacji: Uporządkowany sidebar i UX ---
if not st.session_state.api_key_verified:
    st.sidebar.markdown("""
    <h2 style='margin-bottom:0.5em;'>🔑 Klucz OpenAI API</h2>
    <p style='font-size:0.95rem; color:#555;'>Aby korzystać z aplikacji, podaj swój klucz OpenAI API.<br>Nie jest on nigdzie zapisywany.</p>
    """, unsafe_allow_html=True)

    user_api_key_input = st.sidebar.text_input(
        "Podaj swój OpenAI API Key:",
        type="password",
        key="user_api_key_input",
        value=st.session_state.get("current_input_key", ""),
        on_change=lambda: setattr(st.session_state, 'api_key_input_changed', True)
    )
    st.session_state.current_input_key = user_api_key_input

    # Komunikaty pod polem input (zawsze pod inputem, nigdy nad)
    if st.session_state.api_key_error_message:
        st.sidebar.warning(st.session_state.api_key_error_message)
    else:
        st.sidebar.info("Klucz nie jest nigdzie zapisywany. Wymagany do działania aplikacji.")

    if st.session_state.env_key_invalid:
        st.sidebar.warning("Klucz API z pliku .env jest nieprawidłowy lub wystąpił problem z jego weryfikacją.")

    if st.session_state.api_key_input_changed:
        st.session_state.api_key_input_changed = False
        if user_api_key_input:
            if verify_api_key(user_api_key_input):
                st.session_state.api_key = user_api_key_input
                st.session_state.api_key_verified = True
                st.session_state.env_key_invalid = False
                st.sidebar.success("Klucz OpenAI API został pomyślnie zweryfikowany. Możesz korzystać z aplikacji.")
                st.rerun()
            else:
                st.rerun()
        elif not os.getenv("OPENAI_API_KEY"):
            st.sidebar.warning("Brak klucza OpenAI API. Wpisz go powyżej lub dodaj do pliku .env")
            st.session_state.api_key_error_message = "Brak klucza OpenAI API. Wpisz go powyżej lub dodaj do pliku .env"
            st.rerun()

    st.stop()  # Zatrzymujemy resztę aplikacji, jeśli klucz nie jest zweryfikowany

# --- Po weryfikacji klucza: wyczyść komunikaty i pokaż kolejne opcje ---
st.sidebar.success("Klucz OpenAI API zweryfikowany! Możesz korzystać z funkcji aplikacji.")

# Okno wyboru źródła audio: lokalny plik lub YouTube
source_option = st.sidebar.radio(
    label="Wybierz źródło:",
    options=["Plik lokalny", "YouTube"],
    index=0,
    horizontal=False,
)

# Inicjalizacja zmiennych
audio_file = None
youtube_url = ""

if source_option == "Plik lokalny":
    audio_file = st.sidebar.file_uploader(
        "Wybierz plik audio lub video do transkrypcji:",
        type=["mp3", "wav", "m4a", "mp4", "mov", "avi", "webm"],
        accept_multiple_files=False,
        help="Obsługiwane formaty: mp3, wav, m4a, mp4, mov, avi, webm. Maksymalny rozmiar: 25MB."
    )
    st.sidebar.markdown("---")

if source_option == "YouTube":
    youtube_url = st.sidebar.text_input(
        "Wklej adres www z YouTube:",
        value="",
        key="youtube_url_input",
        help="Wklej pełny adres filmu z YouTube."
    )
    st.sidebar.markdown("---")

# --- Klucz API zweryfikowany, inicjalizacja klienta i główna aplikacja ---
try:
    client = openai.OpenAI(api_key=st.session_state.api_key)
except openai.OpenAIError as e:
    st.error(f"Nie udało się zainicjować klienta OpenAI po weryfikacji klucza: {e}")
    logger.error("Błąd inicjalizacji klienta OpenAI po weryfikacji: %s", e)
    st.session_state.api_key_verified = False
    client = None
except Exception as e:
    logger.error("Nieoczekiwany błąd podczas inicjalizacji klienta OpenAI: %s", traceback.format_exc())
    st.error(f"Nieoczekiwany błąd podczas inicjalizacji klienta OpenAI: {e}")
    st.session_state.api_key_verified = False
    client = None

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


def init_paths(file_bytes: bytes, file_extension: str):
    """
    Inicjalizuje ścieżki dla plików na podstawie zawartości (hash MD5 jako UID).
    
    Funkcja tworzy unikalny identyfikator pliku (UID) na podstawie jego zawartości używając MD5,
    następnie inicjalizuje ścieżki dla pliku oryginalnego, transkrypcji i podsumowania.
    Usuwa stare pliki o tym samym UID z innymi rozszerzeniami, aby uniknąć konfliktów.
    
    Args:
        file_bytes (bytes): Zawartość pliku audio/video
        file_extension (str): Rozszerzenie pliku (np. '.mp3', '.wav')
    
    Returns:
        tuple: (file_uid, orig_path, transcript_path, summary_path)
            - file_uid (str): Unikalny identyfikator pliku (MD5 hash)
            - orig_path (Path): Ścieżka do oryginalnego pliku
            - transcript_path (Path): Ścieżka do pliku transkrypcji
            - summary_path (Path): Ścieżka do pliku podsumowania
    """
    file_uid_local = hashlib.md5(file_bytes, usedforsecurity=False).hexdigest()
    orig_path_local = BASE_DIR / "originals" / f"{file_uid_local}{file_extension}"
    transcript_path_local = BASE_DIR / "transcripts" / f"{file_uid_local}.txt"
    summary_path_local = BASE_DIR / "summaries" / f"{file_uid_local}.txt"
    for audio_ext in [".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"]:
        old_path_local = BASE_DIR / "originals" / f"{file_uid_local}{audio_ext}"
        if old_path_local.exists() and old_path_local != orig_path_local:
            try:
                old_path_local.unlink()
            except OSError as cleanup_exc:
                logger.warning(
                    "Nie udało się usunąć starego pliku %s: %s", old_path_local, cleanup_exc
                )
    if not orig_path_local.exists():
        orig_path_local.write_bytes(file_bytes)
    return file_uid_local, orig_path_local, transcript_path_local, summary_path_local


# --- Automatyczne czyszczenie katalogu uploads/originals przy starcie aplikacji ---
def clean_uploads_originals():
    """Usuwa wszystkie pliki z katalogu uploads/originals przy starcie aplikacji."""
    originals_path = Path("uploads/originals")
    if originals_path.exists():
        for orig_file in originals_path.iterdir():
            try:
                orig_file.unlink()
            except OSError as e:
                logger.warning("Nie udało się usunąć pliku %s: %s", orig_file, e)


clean_uploads_originals()


def validate_youtube_url(url: str) -> bool:
    """Sprawdza czy URL jest prawidłowym adresem YouTube (różne formaty linków)."""
    youtube_patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"(?:https?://)?(?:www\.)?youtu\.be/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+",
        r"(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+",
    ]
    return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)


def download_youtube_audio(url: str):
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
    if not validate_youtube_url(url):
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
            ydl.download([url])

        for yt_file in Path(tmpdir).iterdir():
            if yt_file.suffix.lower() in ALLOWED_EXT and yt_file.is_file():
                # Jeśli plik jest już mp3 lub wav, zwróć bez konwersji
                if yt_file.suffix.lower() in [".mp3", ".wav"]:
                    yt_file_bytes = yt_file.read_bytes()
                    return yt_file_bytes, yt_file.suffix.lower()
                # W przeciwnym razie konwertuj do mp3
                ffmpeg_deps = check_dependencies()
                if not ffmpeg_deps["ffmpeg"]["available"]:
                    raise RuntimeError("FFmpeg nie jest dostępne w systemie. Zainstaluj FFmpeg.")
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
    """
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
        fd, tmp = tempfile.mkstemp(suffix=file_path.suffix, prefix="audio2tekst_")
        os.close(fd)
        tmp_path = Path(tmp)
        ffmpeg_cmd = [
            ffmpeg_exe_path, "-y", "-i", str(file_path), "-ss", str(start), "-t", str(length), "-c", "copy", str(tmp_path)
        ]
        try:
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=300,
                check=True,
                text=True,
            )
            parts.append(tmp_path)
        except subprocess.TimeoutExpired as exc:
            if tmp_path.exists():
                tmp_path.unlink()
            raise RuntimeError(f"Przekroczono czas oczekiwania podczas dzielenia pliku (segment {i+1})") from exc
        except subprocess.CalledProcessError as exc:
            if tmp_path.exists():
                tmp_path.unlink()
            logger.error("FFmpeg error: %s", exc.stderr)
            raise RuntimeError(f"Błąd podczas dzielenia pliku (segment {i+1}): {exc}") from exc
    return parts


def clean_transcript(transcript_text: str) -> str:
    """
    Czyści transkrypcję z typowych artefaktów mowy.
    """
    cleaned_text = re.sub(r"\\b(?:em|yhm|um|uh|a{2,}|y{2,})\\b", "", transcript_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\\s+", " ", cleaned_text)
    return cleaned_text.strip()


def transcribe_chunks(audio_chunks, openai_client):
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
            chunk_size = audio_chunk_file.stat().st_size if audio_chunk_file.exists() else 0
            # Zamiast st.info, dodaj do audio_info_msgs
            st.session_state.setdefault('audio_info_msgs', []).append(
                f"Fragment {audio_idx+1}/{len(audio_chunks)}: {audio_chunk_file} | Rozmiar: {chunk_size/1024:.1f} KB"
            )
            logger.info(
                "Fragment %d: %s | Rozmiar: %d bajtów",
                audio_idx + 1,
                audio_chunk_file,
                chunk_size,
            )
            if chunk_size == 0:
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
                            failed_audio_chunks.append(audio_chunk_file)
                        texts.append(cleaned_transcript)
                else:
                    failed_audio_chunks.append(audio_chunk_file)
            except (OSError, openai.OpenAIError) as exc:
                logger.error(
                    "Błąd podczas transkrypcji fragmentu %s: %s",
                    audio_chunk_file,
                    str(exc),
                )
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
    return "\n".join(texts)


def summarize(input_text: str, openai_client):
    log_path = Path("logs/summary_errors.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Rozpoczynam summarize() - długość tekstu: %s znaków", len(input_text))
    class OpenAIAPIError(Exception):
        pass
    try:
        MAX_CHUNK = 8000
        if len(input_text) > MAX_CHUNK:
            text_chunks = [input_text[i : i + MAX_CHUNK] for i in range(0, len(input_text), MAX_CHUNK)]
            partial_summaries = []
            for text_idx, text_chunk in enumerate(text_chunks):
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
                    if completion and completion.choices and completion.choices[0].message:
                        content = completion.choices[0].message.content
                        partial_summaries.append(content)
                    else:
                        raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI")
                except (openai.OpenAIError, OpenAIAPIError) as exc:
                    msg = f"Błąd fragmentu {text_idx+1}: {exc}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    return "Błąd podczas podsumowywania fragmentu", str(exc)
            if not partial_summaries:
                return (
                    "Nie udało się wygenerować podsumowania",
                    "Brak podsumowań fragmentów.",
                )
            try:
                final_prompt = (
                    "Oto podsumowania fragmentów długiego tekstu. Na ich podstawie podaj jeden temat i jedno podsumowanie całości (3-5 zdań):\n"
                    + "\n".join(partial_summaries)
                )
                completion = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": final_prompt}],
                    max_tokens=300,
                )
                if completion and completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    lines = content.splitlines() if content else []
                    final_topic = lines[0] if lines else "Nie udało się wygenerować tematu"
                    final_summary = " ".join(lines[1:]) if len(lines) > 1 else "Nie udało się wygenerować podsumowania"
                    return final_topic, final_summary
                else:
                    raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI (final)")
            except (openai.OpenAIError, OpenAIAPIError) as exc:
                msg = f"Błąd końcowego podsumowania: {exc}\n"
                logger.error(msg)
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                return "Błąd podczas generowania końcowego podsumowania", str(exc)
        else:
            try:
                prompt = "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + input_text
                completion = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                )
                if completion and completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    lines = content.splitlines() if content else []
                    short_topic = lines[0] if lines else "Nie udało się wygenerować tematu"
                    short_summary = " ".join(lines[1:]) if len(lines) > 1 else "Nie udało się wygenerować podsumowania"
                    return short_topic, short_summary
                else:
                    raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI (krótki tekst)")
            except (openai.OpenAIError, OpenAIAPIError) as exc:
                msg = f"Błąd podsumowania krótkiego tekstu: {exc}\n"
                logger.error(msg)
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                return "Błąd podczas podsumowywania tekstu", str(exc)
    except (openai.OpenAIError, OpenAIAPIError) as exc:
        if (
            "insufficient_quota" in str(exc).lower()
            or "you exceeded your current quota" in str(exc).lower()
            or "error code: 429" in str(exc).lower()
        ):
            return "Brak środków na koncie OpenAI", str(exc)
        msg = f"Błąd ogólny podsumowania: {exc}\n"
        logger.error(msg)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
        return "Błąd ogólny podczas podsumowywania", str(exc)
    return (
        "Nie udało się wygenerować podsumowania",
        "Spróbuj ponownie lub skontaktuj się z administratorem",
    )


# --- Ekran powitalny i opis aplikacji na samej górze strony ---
st.markdown("""
<div style='display: flex; flex-direction: column; align-items: center; justify-content: flex-start; min-height: 0;'>
    <h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0.5em;'>📼 Audio2Tekst 📝</h1>
    <p style='text-align: center; font-size: 1.1rem; max-width: 600px; margin: 0 auto; color: #444;'>
        Szybka transkrypcja plików audio i YouTube na tekst.<br>
        Prosto. Bez zbędnych opcji.
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Panel boczny: Informacje o systemie i audio na samym dole sidebaru ---
# (PRZENIESIONO TĘ SEKCJĘ ZA DEFINICJE STAŁYCH)

# --- Stałe i konfiguracja ścieżek ---
BASE_DIR = Path("uploads")
for folder in ("originals", "transcripts", "summaries"):
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}
MAX_SIZE = 25 * 1024 * 1024  # 25MB
CHUNK_MS = 5 * 60 * 1000  # 5 minut w ms

# --- Panel boczny: Informacje o systemie i audio na samym dole sidebaru ---
with st.sidebar.expander("ℹ️ Informacje o systemie", expanded=False):
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
    # Przycisk czyszczenia pamięci aplikacji
    if st.button("Wyczyść pamięć aplikacji (audio, transkrypcje, logi)"):
        for folder in ("originals", "transcripts", "summaries"):
            folder_path = BASE_DIR / folder
            if folder_path.exists():
                for file in folder_path.iterdir():
                    try:
                        file.unlink()
                    except OSError as e:
                        st.warning(f"Nie udało się usunąć pliku: {file} ({e})")
        logs_path = Path("logs")
        if logs_path.exists():
            for file in logs_path.iterdir():
                try:
                    file.unlink()
                except OSError as e:
                    st.warning(f"Nie udało się usunąć logu: {file} ({e})")
        for key in list(st.session_state.keys()):
            if key not in ("api_key", "api_key_verified"):
                del st.session_state[key]
        st.success("Pamięć aplikacji, transkrypcje i logi zostały wyczyszczone!")
        time.sleep(1)
        st.rerun()

with st.sidebar.expander("🎵 Informacje o audio", expanded=False):
    if 'audio_info_msgs' in st.session_state:
        for msg in st.session_state['audio_info_msgs']:
            st.write(msg)
    else:
        st.write("Brak informacji o pliku audio.")

# --- Zbieranie komunikatów audio do sidebaru zamiast st.info ---
# Przed każdą operacją na pliku audio, zamiast st.info(...), dodaj do st.session_state['audio_info_msgs']
# Przykład:
# st.session_state.setdefault('audio_info_msgs', []).append("Plik do transkrypcji: ...")
# Przykład dla fragmentów:
# st.session_state['audio_info_msgs'].append(f"Fragment {audio_idx+1}/{len(audio_chunks)}: {audio_chunk_file} | Rozmiar: {chunk_size/1024:.1f} KB")

# --- Komunikat o błędnym YouTube URL pod polem w sidebarze ---
# W miejscu obsługi YouTube:
# url = st.sidebar.text_input("Wklej adres www z YouTube:")
# youtube_url_error_placeholder = st.sidebar.empty()
# ...
# except ValueError as e:
#     youtube_url_error_placeholder.warning(f"⚠️ {str(e)}")

# --- Główna logika aplikacji: obsługa plików lokalnych i YouTube ---

# Zmienna do przechowywania danych pliku i rozszerzenia
file_data = None
file_ext = None
file_source = None

# Obsługa pliku lokalnego
if source_option == "Plik lokalny":
    if audio_file is not None:
        if audio_file.size > MAX_SIZE:
            st.error(f"⚠️ Plik jest za duży! Maksymalny rozmiar to {MAX_SIZE/1024/1024:.1f} MB")
        else:
            file_ext = Path(audio_file.name).suffix.lower()
            if file_ext not in ALLOWED_EXT:
                st.error(f"⚠️ Nieobsługiwany format pliku: {file_ext}")
            else:
                file_data = audio_file.read()
                file_source = "lokalny"
                # Dodaj info do sidebaru
                st.session_state.setdefault('audio_info_msgs', []).clear()
                st.session_state['audio_info_msgs'].append("Źródło: Plik lokalny")
                st.session_state['audio_info_msgs'].append(f"Nazwa: {audio_file.name}")
                st.session_state['audio_info_msgs'].append(f"Rozmiar: {len(file_data)/1024:.1f} KB")
                st.session_state['audio_info_msgs'].append(f"Format: {file_ext.upper()}")

# Obsługa YouTube
elif source_option == "YouTube":
    if youtube_url and youtube_url.strip():
        if validate_youtube_url(youtube_url.strip()):
            # Inicjalizuj info przed pobraniem (czyści tylko jeśli zmieniono adres)
            if (
                'audio_info_msgs' not in st.session_state
                or not st.session_state['audio_info_msgs']
                or st.session_state['audio_info_msgs'][0] != f"YouTube: {youtube_url.strip()}"
            ):
                st.session_state['audio_info_msgs'] = []
            with st.spinner("Pobieranie audio z YouTube..."):
                try:
                    file_data, file_ext = download_youtube_audio(youtube_url.strip())
                    file_source = "YouTube"
                    st.session_state['audio_info_msgs'] = [
                        "Źródło: YouTube",
                        f"Rozmiar: {len(file_data)/1024:.1f} KB",
                        f"Format: {file_ext.upper()}"
                    ]
                except ValueError as e:
                    st.error(f"Błąd URL: {str(e)}")
                except RuntimeError as e:
                    st.error(f"Błąd pobierania: {str(e)}")
                except Exception as exc:
                    st.error(f"Nieoczekiwany błąd: {str(exc)}")
                    logger.error("Błąd pobierania z YouTube: %s", traceback.format_exc())
        else:
            st.sidebar.error("Wprowadź prawidłowy adres YouTube")

# Przetwarzanie pliku (jeśli mamy dane)
if file_data is not None and file_ext is not None:
    try:
        # Inicjalizacja ścieżek plików
        file_uid_local, orig_path_local, transcript_path_local, summary_path_local = init_paths(file_data, file_ext)
        # Odtwarzacz audio
        st.markdown("### Podgląd audio")
        st.audio(file_data, format=f"audio/{file_ext[1:]}")
        # Przycisk pobierania audio (bezpośrednio pod odtwarzaczem)
        if file_ext.lower() in [".mp4", ".mov", ".avi", ".webm"]:
            download_label = "Pobierz audio (MP3)"
            download_filename = f"{file_uid_local}.mp3"
        else:
            download_label = "Pobierz audio"
            download_filename = f"{file_uid_local}{file_ext}"
        st.download_button(
            label=download_label,
            data=file_data,
            file_name=download_filename,
            mime=f"audio/{file_ext[1:] if file_ext != '.mp4' else 'mp3'}"
        )
        # Sekcja transkrypcji
        st.markdown("---")
        st.markdown("### Transkrypcja")
        # Sprawdzenie czy transkrypcja już istnieje
        if transcript_path_local.exists():
            transcript_text_local = transcript_path_local.read_text(encoding=get_safe_encoding())
            st.success("Znaleziono istniejącą transkrypcję!")
        else:
            transcript_text_local = None
        # Przycisk transkrypcji
        if st.button("Transkrybuj audio", type="primary", disabled=(transcript_text_local is not None) or (client is None)):
            if client is None:
                st.error("Klient OpenAI nie został poprawnie zainicjowany. Sprawdź klucz API.")
            elif transcript_text_local is not None:
                st.info("Transkrypcja już została wykonana.")
            else:
                try:
                    with st.spinner("Transkrypcja w toku..."):
                        # Sprawdzenie długości pliku
                        duration_local = get_duration(orig_path_local)
                        st.session_state.setdefault('audio_info_msgs', [])
                        st.session_state['audio_info_msgs'].append(f"Długość pliku: {duration_local/60:.1f} minut")
                        if duration_local > CHUNK_MS / 1000:
                            st.session_state['audio_info_msgs'].append("Plik zostanie podzielony na fragmenty do przetworzenia...")
                            audio_chunks_local = split_audio(orig_path_local)
                            transcript_text_local = transcribe_chunks(audio_chunks_local, client)
                        else:
                            with open(orig_path_local, "rb") as audio_file_obj_local:
                                transcript_response_local = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_file_obj_local,
                                    language="pl",
                                    response_format="text"
                                )
                                transcript_text_local = clean_transcript(str(transcript_response_local))
                        if transcript_text_local and transcript_text_local.strip():
                            transcript_path_local.write_text(transcript_text_local, encoding=get_safe_encoding())
                            st.success("Transkrypcja została wykonana pomyślnie!")
                        else:
                            st.error("Nie udało się wygenerować transkrypcji.")
                            transcript_text_local = None
                except Exception as exc:
                    st.error(f"Błąd podczas transkrypcji: {str(exc)}")
                    logger.error("Błąd transkrypcji: %s", traceback.format_exc())
                    transcript_text_local = None
        # Wyświetlanie i edycja transkrypcji
        if transcript_text_local:
            st.markdown("#### Wynik transkrypcji")
            edited_transcript_local = st.text_area(
                "Edytuj transkrypcję (jeśli potrzeba):",
                value=transcript_text_local,
                height=200,
                help="Możesz poprawić transkrypcję przed wygenerowaniem podsumowania."
            )
            # Przycisk pobierania transkrypcji
            st.download_button(
                label="Pobierz transkrypcję",
                data=edited_transcript_local,
                file_name=f"transkrypcja_{file_uid_local}.txt",
                mime="text/plain"
            )
            # Sekcja podsumowania
            st.markdown("---")
            st.markdown("### Podsumowanie AI")
            # Sprawdzenie czy podsumowanie już istnieje
            if summary_path_local.exists():
                summary_content_local = summary_path_local.read_text(encoding=get_safe_encoding())
                st.success("Znaleziono istniejące podsumowanie!")
                st.markdown("#### Wynik podsumowania")
                st.markdown(summary_content_local)
                # Przycisk pobierania podsumowania
                st.download_button(
                    label="Pobierz podsumowanie",
                    data=summary_content_local,
                    file_name=f"podsumowanie_{file_uid_local}.txt",
                    mime="text/plain"
                )
            else:
                # Przycisk generowania podsumowania
                if st.button("Wygeneruj podsumowanie", type="secondary"):
                    if not edited_transcript_local.strip():
                        st.error("Brak tekstu do podsumowania.")
                    else:
                        try:
                            with st.spinner("Generowanie podsumowania..."):
                                topic_local, summary_local = summarize(edited_transcript_local, client)
                                if topic_local and summary_local:
                                    topic_clean_local = topic_local.replace('Temat:', '').strip()
                                    summary_content_local = f"**Temat:** {topic_clean_local}\n\n**Podsumowanie:** {summary_local}"
                                    summary_path_local.write_text(summary_content_local, encoding=get_safe_encoding())
                                    st.success("Podsumowanie zostało wygenerowane!")
                                    st.markdown("#### Wynik podsumowania")
                                    st.markdown(summary_content_local)
                                    st.download_button(
                                        label="Pobierz podsumowanie",
                                        data=summary_content_local,
                                        file_name=f"podsumowanie_{file_uid_local}.txt",
                                        mime="text/plain"
                                    )
                                else:
                                    st.error("Nie udało się wygenerować podsumowania.")
                        except Exception as exc:
                            st.error(f"Błąd podczas generowania podsumowania: {str(exc)}")
                            logger.error("Błąd podsumowania: %s", traceback.format_exc())
    except Exception as exc:
        st.error(f"Błąd podczas przetwarzania pliku: {str(exc)}")
        logger.error("Błąd przetwarzania pliku: %s", traceback.format_exc())
else:
    # Komunikat gdy nie ma pliku do przetworzenia
    if source_option == "Plik lokalny":
        st.info("Wybierz plik audio lub video z panelu bocznego, aby rozpocząć transkrypcję.")
    elif source_option == "YouTube":
        st.info("Wklej adres YouTube w panelu bocznym, aby pobrać i transkrybować audio.")

# --- Ekran powitalny i opis aplikacji na samej górze strony ---