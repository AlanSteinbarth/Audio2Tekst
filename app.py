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
Data: 29 maja 2025
Wersja: 2.3.0 (Cross-Platform Edition)
"""

# --- Importy systemowe ---
import hashlib
import logging
import re
import math
import tempfile
import os
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional
import time
import threading

# --- Importy zewnętrzne ---
import streamlit as st
import openai
from werkzeug.utils import secure_filename
import yt_dlp

# --- Konfiguracja logowania ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funkcje pomocnicze dla kompatybilności systemów ---
def get_system_info() -> dict:
    """Zwraca informacje o systemie operacyjnym."""
    return {
        'platform': platform.system().lower(),
        'architecture': platform.machine(),
        'python_version': platform.python_version(),
        'is_windows': platform.system().lower() == 'windows',
        'is_macos': platform.system().lower() == 'darwin',
        'is_linux': platform.system().lower() == 'linux'
    }

def find_executable(name: str) -> Optional[str]:
    """Znajduje ścieżkę do pliku wykonywalnego w systemie."""
    system_info = get_system_info()
    
    # Na Windows dodaj .exe jeśli nie ma rozszerzenia
    if system_info['is_windows'] and not name.endswith('.exe'):
        name += '.exe'
    
    # Sprawdź czy jest dostępny w PATH
    if shutil.which(name):
        return shutil.which(name)
    
    # Sprawdź typowe lokalizacje
    common_paths = []
    if system_info['is_windows']:
        common_paths = [
            'C:\\ffmpeg\\bin',
            'C:\\Program Files\\ffmpeg\\bin',
            'C:\\Program Files (x86)\\ffmpeg\\bin'
        ]
    elif system_info['is_macos']:
        common_paths = [
            '/usr/local/bin',
            '/opt/homebrew/bin',
            '/usr/bin'
        ]
    else:  # Linux
        common_paths = [
            '/usr/bin',
            '/usr/local/bin',
            '/snap/bin'
        ]
    
    for path in common_paths:
        full_path = Path(path) / name
        if full_path.exists() and full_path.is_file():
            return str(full_path)
    
    return None

def check_dependencies() -> dict:
    """Sprawdza dostępność wymaganych narzędzi systemowych."""
    dependencies = {
        'ffmpeg': find_executable('ffmpeg'),
        'ffprobe': find_executable('ffprobe')
    }
    
    return {
        name: {
            'available': path is not None,
            'path': path
        } for name, path in dependencies.items()
    }

def get_safe_encoding() -> str:
    """Zwraca bezpieczne kodowanie dla systemu."""
    system_info = get_system_info()
    
    if system_info['is_windows']:
        # Windows może używać różnych kodowań
        return 'utf-8-sig'  # BOM dla lepszej kompatybilności
    else:
        # Unix-like systemy standardowo używają UTF-8
        return 'utf-8'

# --- Konfiguracja Streamlit ---
st.set_page_config(page_title="Audio2Tekst", layout="wide")

# --- Sprawdzenie zależności systemowych ---
system_info = get_system_info()
dependencies = check_dependencies()

st.title('📼 Audio2Tekst 📝')
st.subheader("Przekształć swoje pliki audio i video (oraz z YouTube) na tekst, a następnie zrób z nich zwięzłe podsumowanie")

# Wyświetl informacje o systemie i zależnościach
with st.expander("ℹ️ Informacje o systemie", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**System:**")
        st.write(f"- Platform: {system_info['platform'].title()}")
        st.write(f"- Architecture: {system_info['architecture']}")
        st.write(f"- Python: {system_info['python_version']}")
    
    with col2:
        st.write("**Zależności:**")
        for dep_name, dep_info in dependencies.items():
            status = "✅" if dep_info['available'] else "❌"
            st.write(f"- {dep_name}: {status}")
            if dep_info['available']:
                st.write(f"  📁 {dep_info['path']}")
    
    st.write("---")
    st.write("**📋 Przetwarzanie długich tekstów:**")
    st.write("W przypadku bardzo długich transkrypcji (>8000 znaków) tekst jest automatycznie dzielony na fragmenty. Każdy fragment jest podsumowywany osobno a na końcu generowane jest finalne podsumowanie całości. Rozwiązuje to ograniczenia OpenAI związane z długością promptu.")

# Sprawdź czy wszystkie zależności są dostępne
missing_deps = [name for name, info in dependencies.items() if not info['available']]
if missing_deps:
    st.error(f"⚠️ Brakujące zależności: {', '.join(missing_deps)}")
    st.error("Zainstaluj FFmpeg aby kontynuować. Zobacz instrukcje instalacji w README.md")
    st.stop()

# --- Konfiguracja OpenAI ---
api_key = st.sidebar.text_input("Podaj swój OpenAI API Key", type="password")
if not api_key:
    st.stop()
client = openai.OpenAI(api_key=api_key)

# --- Stałe i konfiguracja ścieżek ---
BASE_DIR = Path("uploads")
for folder in ("originals", "transcripts", "summaries"):
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}
MAX_SIZE = 25 * 1024 * 1024  # 25MB
CHUNK_MS = 5 * 60 * 1000     # 5 minutes in ms

# --- Funkcje pomocnicze ---
# UWAGA: To jest ulepszona wersja programu Audio2Tekst
# Główne usprawnienia w wersji 2.3.0:
# ✅ Uniwersalna kompatybilność z Windows, macOS i Linux
# ✅ Automatyczne wykrywanie platformy i dostosowanie komend
# ✅ Poprawiona obsługa ścieżek plików i enkodowania
# ✅ Dodano sprawdzanie dostępności narzędzi systemowych
# ✅ Ulepszona obsługa plików tymczasowych
# ✅ Zwiększona stabilność na różnych środowiskach

@st.cache_data
def init_paths(file_data: bytes, file_ext: str):
    """Inicjalizuje ścieżki dla plików na podstawie zawartości."""
    file_uid = hashlib.md5(file_data, usedforsecurity=False).hexdigest()
    orig_path = BASE_DIR / "originals" / f"{file_uid}{file_ext}"
    transcript_path = BASE_DIR / "transcripts" / f"{file_uid}.txt"
    summary_path = BASE_DIR / "summaries" / f"{file_uid}.txt"
    if not orig_path.exists():
        orig_path.write_bytes(file_data)
    return file_uid, orig_path, transcript_path, summary_path

def validate_youtube_url(youtube_url: str) -> bool:
    """Sprawdza czy URL jest prawidłowym adresem YouTube."""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+'
    ]
    
    return any(re.match(pattern, youtube_url.strip()) for pattern in youtube_patterns)

def download_youtube_audio(youtube_url: str):
    """Pobiera audio z filmu YouTube i konwertuje do odpowiedniego formatu."""
    # Walidacja URL przed próbą pobrania
    if not validate_youtube_url(youtube_url):
        raise ValueError("Nieprawidłowy adres YouTube. Wklej prawidłowy link do filmu YouTube.")
    
    tmpdir = tempfile.mkdtemp(prefix='audio2tekst_yt_')
    
    try:
        # Użyj bezpiecznych ścieżek dla różnych systemów
        output_template = str(Path(tmpdir) / '%(id)s.%(ext)s')
        
        opts = {
            'format': 'bestaudio[ext=webm]/bestaudio',
            'outtmpl': output_template,
            'quiet': True,
            'noplaylist': True,
            'extractaudio': True,
            'audioformat': 'webm',
            'prefer_ffmpeg': True
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([youtube_url])
        
        # Znajdź pobrany plik
        for file_path in Path(tmpdir).iterdir():
            if file_path.suffix.lower() in ALLOWED_EXT and file_path.is_file():
                file_data = file_path.read_bytes()
                return file_data, file_path.suffix.lower()
        
        raise FileNotFoundError("Nie znaleziono pliku audio z YouTube")
    
    except ValueError:
        # Błędy walidacji URL - przekaż dalej bez modyfikacji
        raise
    except Exception as exc:
        error_msg = str(exc).lower()
        
        # Obsługa specyficznych błędów yt-dlp
        if "is not a valid url" in error_msg or "invalid url" in error_msg:
            raise ValueError("Nieprawidłowy adres YouTube. Wklej prawidłowy link do filmu YouTube.") from exc
        elif "video unavailable" in error_msg or "private video" in error_msg:
            raise RuntimeError("Film jest niedostępny lub prywatny. Spróbuj inny film YouTube.") from exc
        elif "sign in" in error_msg or "age restricted" in error_msg:
            raise RuntimeError("Film wymaga logowania lub jest ograniczony wiekowo. Spróbuj inny film YouTube.") from exc
        elif "copyright" in error_msg or "blocked" in error_msg:
            raise RuntimeError("Film jest zablokowany lub ma ograniczenia autorskie. Spróbuj inny film YouTube.") from exc
        elif "network" in error_msg or "connection" in error_msg:
            raise RuntimeError("Błąd połączenia z YouTube. Sprawdź połączenie internetowe i spróbuj ponownie.") from exc
        else:
            logger.error("Błąd podczas pobierania z YouTube: %s", str(exc))
            raise RuntimeError("Wystąpił błąd podczas pobierania z YouTube. Sprawdź link i spróbuj ponownie.") from exc
    
    finally:
        # Bezpieczne usunięcie tymczasowego katalogu
        try:
            shutil.rmtree(tmpdir)
        except Exception as cleanup_exc:
            logger.warning("Nie udało się usunąć tymczasowego katalogu: %s", cleanup_exc)

@st.cache_data
def get_duration(file_path: Path) -> float:
    """Zwraca długość pliku audio/video w sekundach."""
    # Sprawdź dostępność ffprobe
    dependencies_info = check_dependencies()
    if not dependencies_info['ffprobe']['available']:
        raise RuntimeError("FFprobe nie jest dostępne w systemie. Zainstaluj FFmpeg.")
    
    ffprobe_path = dependencies_info['ffprobe']['path']
    ffprobe_cmd = [
        ffprobe_path, '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(file_path)
    ]
    
    try:
        result = subprocess.run(
            ffprobe_cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # timeout dla bezpieczeństwa
            check=True
        )
        return float(result.stdout.strip())
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Przekroczono czas oczekiwania na analizę pliku") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Błąd podczas analizy pliku: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Nie można odczytać długości pliku: {exc}") from exc

@st.cache_data
def split_audio(file_path: Path):
    """Dzieli długie pliki audio na mniejsze części do przetworzenia."""    
    # Sprawdź dostępność ffmpeg
    dependencies_info = check_dependencies()
    if not dependencies_info['ffmpeg']['available']:
        raise RuntimeError("FFmpeg nie jest dostępne w systemie. Zainstaluj FFmpeg.")
    ffmpeg_exe_path = dependencies_info['ffmpeg']['path']
    duration = get_duration(file_path)
    seg_sec = CHUNK_MS / 1000
    parts = []
    
    for i in range(math.ceil(duration / seg_sec)):
        start = i * seg_sec
        length = seg_sec if (start + seg_sec) <= duration else (duration - start)
        
        # Utwórz tymczasowy plik w sposób bezpieczny dla wszystkich platform
        fd, tmp = tempfile.mkstemp(suffix=file_path.suffix, prefix='audio2tekst_')
        os.close(fd)
        tmp_path = Path(tmp)
        
        ffmpeg_cmd = [
            ffmpeg_exe_path, '-y', '-i', str(file_path),
            '-ss', str(start), '-t', str(length),
            '-c', 'copy', str(tmp_path)
        ]
        
        try:
            subprocess.run(
                ffmpeg_cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                timeout=300,  # 5 minut timeout
                check=True,
                text=True
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

@st.cache_data
def clean_transcript(transcript_text: str) -> str:
    """Czyści transkrypcję z typowych artefaktów mowy."""
    cleaned_text = re.sub(r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", transcript_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text.strip()

def transcribe_chunks(audio_chunks, openai_client):
    """Transkrybuje podzielone fragmenty audio na tekst używając OpenAI API."""
    texts = []
    long_transcription_msg = "Plik audio poddawany transkrypcji jest bardzo duży. Potrzebuję więcej czasu. Cierpliwości..."
    show_long_msg = [False]
    def delayed_info():
        time.sleep(10)
        show_long_msg[0] = True
        st.info(long_transcription_msg)
    thread = threading.Thread(target=delayed_info)
    thread.start()
    with st.spinner("Transkrypcja w toku..."):
        for chunk_file in audio_chunks:
            try:
                if chunk_file.stat().st_size <= MAX_SIZE:
                    with open(chunk_file, 'rb') as audio_file:
                        res = openai_client.audio.transcriptions.create(
                            model='whisper-1',
                            file=audio_file,
                            language='pl',
                            response_format='text'
                        )
                        texts.append(clean_transcript(str(res)))
                else:
                    logger.warning("Plik %s przekracza maksymalny rozmiar %s bajtów", chunk_file, MAX_SIZE)
            except Exception as exc:
                logger.error("Błąd podczas transkrypcji fragmentu %s: %s", chunk_file, str(exc))
            finally:
                # Bezpieczne usunięcie pliku tymczasowego
                try:
                    if chunk_file.exists():
                        chunk_file.unlink()
                except Exception as cleanup_exc:
                    logger.warning("Nie udało się usunąć pliku tymczasowego %s: %s", chunk_file, cleanup_exc)
    return "\n".join(texts)

def summarize(input_text: str, openai_client):
    """Generuje temat i podsumowanie z transkrypcji, dzieląc długi tekst na fragmenty."""
    log_path = Path("logs/summary_errors.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Usunięto komunikat o długim tekście
    logger.info("Rozpoczynam summarize() - długość tekstu: %s znaków", len(input_text))
    
    class OpenAIAPIError(Exception):
        """Własny wyjątek dla błędów OpenAI API."""
        pass
    
    try:
        MAX_CHUNK = 8000  # znaków na fragment (bezpieczny limit)
        if len(input_text) > MAX_CHUNK:
            logger.info("Tekst jest długi - dzielę na fragmenty")
            text_chunks = [input_text[i:i+MAX_CHUNK] for i in range(0, len(input_text), MAX_CHUNK)]
            logger.info("Podzielono na %s fragmentów", len(text_chunks))
            partial_summaries = []
            for idx, chunk in enumerate(text_chunks):
                logger.info("Przetwarzam fragment %s/%s", idx+1, len(text_chunks))
                with st.spinner(f"Podsumowywanie fragmentu {idx+1}/{len(text_chunks)}..."):
                    try:
                        prompt = f"Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami (fragment {idx+1}/{len(text_chunks)}):\n" + chunk
                        completion = openai_client.chat.completions.create(
                            model='gpt-3.5-turbo',
                            messages=[{'role': 'user', 'content': prompt}],
                            max_tokens=300
                        )
                        if completion and completion.choices and completion.choices[0].message:
                            content = completion.choices[0].message.content
                            partial_summaries.append(content)
                        else:
                            raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI")
                    except Exception as exc:
                        msg = f"Błąd fragmentu {idx+1}: {exc}\n"
                        logger.error(msg)
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                        st.error(f"Błąd podczas podsumowywania fragmentu {idx+1}: {exc}")
                        return "Błąd podczas podsumowywania fragmentu", str(exc)
            logger.info("Zebrałem %s częściowych podsumowań", len(partial_summaries))
            if not partial_summaries:
                st.error("Nie udało się wygenerować żadnego podsumowania fragmentów. Spróbuj ponownie lub sprawdź logi.")
                logger.error("Brak partial_summaries - nie można wygenerować końcowego podsumowania.")
                return "Nie udało się wygenerować podsumowania", "Brak podsumowań fragmentów."
            with st.spinner("Tworzenie końcowego podsumowania..."):
                try:
                    final_prompt = "Oto podsumowania fragmentów długiego tekstu. Na ich podstawie podaj jeden temat i jedno podsumowanie całości (3-5 zdań):\n" + "\n".join(partial_summaries)
                    logger.info("Prompt do modelu (final): %s...", final_prompt[:200])
                    completion = openai_client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': final_prompt}],
                        max_tokens=300
                    )
                    if completion and completion.choices and completion.choices[0].message:
                        content = completion.choices[0].message.content
                        logger.info("Odpowiedź modelu (final): %s...", content[:200])
                        lines = content.splitlines() if content else []
                        final_topic = lines[0] if lines else 'Nie udało się wygenerować tematu'
                        final_summary = ' '.join(lines[1:]) if len(lines) > 1 else 'Nie udało się wygenerować podsumowania'
                        logger.info("Zwracam: topic='%s...', summary='%s...'", final_topic[:50], final_summary[:50])
                        return final_topic, final_summary
                    else:
                        logger.error("Brak odpowiedzi z modelu OpenAI (final)")
                        raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI (final)")
                except Exception as exc:
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
                    prompt = "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + input_text
                    completion = openai_client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': prompt}],
                        max_tokens=300
                    )
                    if completion and completion.choices and completion.choices[0].message:
                        content = completion.choices[0].message.content
                        logger.info("Otrzymano krótkie podsumowanie: %s...", content[:100])
                        lines = content.splitlines() if content else []
                        short_topic = lines[0] if lines else 'Nie udało się wygenerować tematu'
                        short_summary = ' '.join(lines[1:]) if len(lines) > 1 else 'Nie udało się wygenerować podsumowania'
                        logger.info("Zwracam: topic='%s...', summary='%s...'", short_topic[:50], short_summary[:50])
                        return short_topic, short_summary
                    else:
                        raise OpenAIAPIError("Brak odpowiedzi z modelu OpenAI (krótki tekst)")
                except Exception as exc:
                    msg = f"Błąd podsumowania krótkiego tekstu: {exc}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    st.error(f"Błąd podczas podsumowywania tekstu: {exc}")
                    return "Błąd podczas podsumowywania tekstu", str(exc)
    except Exception as exc:
        # Obsługa błędu braku środków/quota w OpenAI
        if 'insufficient_quota' in str(exc).lower() or 'you exceeded your current quota' in str(exc).lower() or 'error code: 429' in str(exc).lower():
            st.error("Brak środków lub limitu na koncie OpenAI. Sprawdź swój plan i limity na https://platform.openai.com/account/billing.")
            logger.error("Błąd quota (429/insufficient_quota): %s", exc)
            return "Brak środków na koncie OpenAI", str(exc)
        msg = f"Błąd ogólny podsumowania: {exc}\n"
        logger.error(msg)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
        st.error(f"Błąd ogólny podczas podsumowywania: {exc}")
        return "Błąd ogólny podczas podsumowywania", str(exc)
    
    return "Nie udało się wygenerować podsumowania", "Spróbuj ponownie lub skontaktuj się z administratorem"

# --- Interfejs użytkownika ---
src = st.sidebar.radio('Wybierz źródło audio:', ['Plik lokalny', 'YouTube'])

# Inicjalizacja zmiennych
data, ext = None, None
error_message = None

# Flaga do komunikatu o pobraniu audio z YouTube
if 'yt_success' not in st.session_state:
    st.session_state['yt_success'] = False
if 'yt_data' not in st.session_state:
    st.session_state['yt_data'] = None
if 'yt_ext' not in st.session_state:
    st.session_state['yt_ext'] = None

if src == 'YouTube':
    url = st.sidebar.text_input('Wklej adres www z YouTube:')
    # --- RESET STANU PO ZMIANIE URL ---
    prev_url = st.session_state.get('yt_prev_url', None)
    if url and url != prev_url:
        # Usuń stare klucze sesji związane z poprzednią transkrypcją/podsumowaniem
        keys_to_remove = []
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and (
                k.startswith('done_') or k.startswith('topic_') or k.startswith('summary_')
                or k.startswith('yt_')
            ):
                keys_to_remove.append(k)
        for k in keys_to_remove:
            del st.session_state[k]        # Usuń pliki powiązane z poprzednim UID (jeśli istnieje)
        prev_uid = st.session_state.get('yt_prev_uid', None)
        if prev_uid:
            for folder in (BASE_DIR / 'originals', BASE_DIR / 'transcripts', BASE_DIR / 'summaries'):
                for file_ext in ('.mp3', '.wav', '.m4a', '.mp4', '.mov', '.avi', '.webm', '.txt'):
                    file_to_remove = folder / f"{prev_uid}{file_ext}"
                    if file_to_remove.exists():
                        try:
                            file_to_remove.unlink()
                        except Exception as cleanup_exc:
                            logger.warning('Nie udało się usunąć pliku %s: %s', file_to_remove, cleanup_exc)
        # Resetuj flagi yt
        st.session_state['yt_success'] = False
        st.session_state['yt_data'] = None
        st.session_state['yt_ext'] = None
        st.session_state['yt_prev_uid'] = None
        st.session_state['yt_prev_url'] = url
    # --- KONIEC RESETU ---
    # Jeśli już pobrano audio, przypisz z sesji
    if st.session_state.get('yt_success') and st.session_state.get('yt_data') and st.session_state.get('yt_ext'):
        data = st.session_state['yt_data']
        ext = st.session_state['yt_ext']
        st.success("Pomyślnie pobrano audio z YouTube!")
    elif url:
        try:
            with st.spinner("Pobieranie audio z YouTube..."):
                data, ext = download_youtube_audio(url)
                if not data or not isinstance(data, bytes):
                    raise RuntimeError("Nie udało się pobrać pliku audio z YouTube lub plik jest uszkodzony.")
                st.session_state['yt_success'] = True
                st.session_state['yt_data'] = data
                st.session_state['yt_ext'] = ext                # Zapisz UID do późniejszego czyszczenia
                uid, _, _, _ = init_paths(data, ext)
                st.session_state['yt_prev_uid'] = uid
                st.session_state['yt_prev_url'] = url
                st.success("Pomyślnie pobrano audio z YouTube!")
        except ValueError as e:
            st.warning(f"⚠️ {str(e)}")
            st.session_state['yt_success'] = False
            st.session_state['yt_data'] = None
            st.session_state['yt_ext'] = None
            st.stop()
        except RuntimeError as e:
            st.error(f"❌ {str(e)}")
            st.session_state['yt_success'] = False
            st.session_state['yt_data'] = None
            st.session_state['yt_ext'] = None
            st.stop()
        except Exception as e:
            st.error(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}")
            logger.error(f"Nieoczekiwany błąd podczas pobierania z YouTube: {str(e)}")
            st.session_state['yt_success'] = False
            st.session_state['yt_data'] = None
            st.session_state['yt_ext'] = None
            st.stop()
        # Po pobraniu przypisz do lokalnych zmiennych
        data = st.session_state['yt_data']
        ext = st.session_state['yt_ext']
    else:
        st.session_state['yt_success'] = False
        st.session_state['yt_data'] = None
        st.session_state['yt_ext'] = None
        st.stop()
else:
    up = st.sidebar.file_uploader('Wybierz plik', type=[e.strip('.') for e in ALLOWED_EXT])
    if up:
        data, ext = up.read(), Path(secure_filename(up.name)).suffix.lower()
    else:
        st.stop()

# Sprawdź czy mamy dane do przetworzenia
if data is None or ext is None:
    st.stop()

# --- Przetwarzanie pliku ---
uid, orig, tr, sm = init_paths(data, ext)
st.audio(orig.read_bytes(), format=ext.lstrip('.'))
# Przycisk pobierania audio (zawsze pod odtwarzaczem)
# Jeśli oryginalny plik to .mp4/.webm/.mov/.avi, zaproponuj pobranie jako mp3
if ext in ['.mp3', '.wav', '.m4a']:
    st.download_button('Pobierz audio', orig.read_bytes(), file_name=f'{uid}{ext}')
else:
    # Konwersja do mp3 na żądanie
    mp3_path = orig.with_suffix('.mp3')
    if not mp3_path.exists():
        dependencies_info = check_dependencies()
        if not dependencies_info['ffmpeg']['available']:
            st.warning('FFmpeg nie jest dostępny – nie można przekonwertować do MP3.')
        else:
            ffmpeg_exe_path = dependencies_info['ffmpeg']['path']
            ffmpeg_cmd = [ffmpeg_exe_path, '-y', '-i', str(orig), str(mp3_path)]
            try:
                subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception as conversion_exc:
                st.warning(f'Błąd konwersji do MP3: {conversion_exc}')
    if mp3_path.exists():
        st.download_button('Pobierz audio (MP3)', mp3_path.read_bytes(), file_name=f'{uid}.mp3')
    else:
        st.download_button('Pobierz audio (oryginał)', orig.read_bytes(), file_name=f'{uid}{ext}')

# --- Stan sesji ---
done_key = f"done_{uid}"
topic_key = f"topic_{uid}"
sum_key = f"summary_{uid}"
for key, default in [(done_key, False), (topic_key, ''), (sum_key, '')]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Transkrypcja ---
transcript_exists = tr.exists() and tr.stat().st_size > 0
if st.button('Transkrybuj') and not st.session_state[done_key]:
    # dzielenie i transkrypcja
    audio_chunks = split_audio(orig)
    transcription_text = transcribe_chunks(audio_chunks, client)
    encoding = get_safe_encoding()
    tr.write_text(transcription_text, encoding=encoding)
    st.session_state[done_key] = True
    st.session_state[topic_key] = ''
    st.session_state[sum_key] = ''
    # NIE używaj st.experimental_rerun() - po prostu UI przejdzie dalej w kolejnym renderze

# --- UI po transkrypcji ---
if st.session_state[done_key] or transcript_exists:
    encoding = get_safe_encoding()
    transcript = tr.read_text(encoding=encoding) if tr.exists() else ''
    st.subheader('Transkrypt:')
    st.text_area('Transkrypcja', transcript, height=300)
    # Najpierw przycisk pobierania transkryptu
    st.download_button('Pobierz transkrypt', transcript, file_name=f'{uid}_transkrypt.txt')
    # Następnie przycisk podsumowania
    if st.button('Podsumuj'):
        result_topic, result_summary = summarize(transcript, client)
        st.session_state[topic_key] = result_topic
        st.session_state[sum_key] = result_summary
    # Wyświetl podsumowanie jeśli istnieje
    if st.session_state[topic_key] or st.session_state[sum_key]:
        st.subheader('Temat:')
        st.write(st.session_state[topic_key])
        st.subheader('Podsumowanie:')
        st.write(st.session_state[sum_key])
        # Przycisk pobierania podsumowania
        st.download_button('Pobierz podsumowanie', st.session_state[sum_key], file_name=f'{uid}_podsumowanie.txt')
