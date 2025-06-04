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
def init_paths(data: bytes, ext: str):
    """Inicjalizuje ścieżki dla plików na podstawie zawartości."""
    uid = hashlib.md5(data).hexdigest()
    orig = BASE_DIR / "originals" / f"{uid}{ext}"
    tr = BASE_DIR / "transcripts" / f"{uid}.txt"
    sm = BASE_DIR / "summaries" / f"{uid}.txt"
    if not orig.exists():
        orig.write_bytes(data)
    return uid, orig, tr, sm

def validate_youtube_url(url: str) -> bool:
    """Sprawdza czy URL jest prawidłowym adresem YouTube."""
    import re
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=[\w-]+'
    ]
    
    return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)

def download_youtube_audio(url: str):
    """Pobiera audio z filmu YouTube i konwertuje do odpowiedniego formatu."""
    # Walidacja URL przed próbą pobrania
    if not validate_youtube_url(url):
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
            ydl.download([url])
        
        # Znajdź pobrany plik
        for f in Path(tmpdir).iterdir():
            if f.suffix.lower() in ALLOWED_EXT and f.is_file():
                data = f.read_bytes()
                return data, f.suffix.lower()
        
        raise FileNotFoundError("Nie znaleziono pliku audio z YouTube")
    
    except ValueError as e:
        # Błędy walidacji URL - przekaż dalej bez modyfikacji
        raise e
    except Exception as e:
        error_msg = str(e).lower()
        
        # Obsługa specyficznych błędów yt-dlp
        if "is not a valid url" in error_msg or "invalid url" in error_msg:
            raise ValueError("Nieprawidłowy adres YouTube. Wklej prawidłowy link do filmu YouTube.")
        elif "video unavailable" in error_msg or "private video" in error_msg:
            raise RuntimeError("Film jest niedostępny lub prywatny. Spróbuj inny film YouTube.")
        elif "sign in" in error_msg or "age restricted" in error_msg:
            raise RuntimeError("Film wymaga logowania lub jest ograniczony wiekowo. Spróbuj inny film YouTube.")
        elif "copyright" in error_msg or "blocked" in error_msg:
            raise RuntimeError("Film jest zablokowany lub ma ograniczenia autorskie. Spróbuj inny film YouTube.")
        elif "network" in error_msg or "connection" in error_msg:
            raise RuntimeError("Błąd połączenia z YouTube. Sprawdź połączenie internetowe i spróbuj ponownie.")
        else:
            logger.error(f"Błąd podczas pobierania z YouTube: {str(e)}")
            raise RuntimeError("Wystąpił błąd podczas pobierania z YouTube. Sprawdź link i spróbuj ponownie.")
    
    finally:
        # Bezpieczne usunięcie tymczasowego katalogu
        try:
            shutil.rmtree(tmpdir)
        except Exception as e:
            logger.warning(f"Nie udało się usunąć tymczasowego katalogu: {e}")

@st.cache_data
def get_duration(path: Path) -> float:
    """Zwraca długość pliku audio/video w sekundach."""
    # Sprawdź dostępność ffprobe
    deps = check_dependencies()
    if not deps['ffprobe']['available']:
        raise RuntimeError("FFprobe nie jest dostępne w systemie. Zainstaluj FFmpeg.")
    
    ffprobe_path = deps['ffprobe']['path']
    cmd = [
        ffprobe_path, '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(path)
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,  # timeout dla bezpieczeństwa
            check=True
        )
        return float(result.stdout.strip())
    except subprocess.TimeoutExpired:
        raise RuntimeError("Przekroczono czas oczekiwania na analizę pliku")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Błąd podczas analizy pliku: {e}")
    except ValueError as e:
        raise RuntimeError(f"Nie można odczytać długości pliku: {e}")

@st.cache_data
def split_audio(path: Path):
    """Dzieli długie pliki audio na mniejsze części do przetworzenia."""    # Sprawdź dostępność ffmpeg
    deps = check_dependencies()
    if not deps['ffmpeg']['available']:
        raise RuntimeError("FFmpeg nie jest dostępne w systemie. Zainstaluj FFmpeg.")
    ffmpeg_path = deps['ffmpeg']['path']
    duration = get_duration(path)
    seg_sec = CHUNK_MS / 1000
    parts = []
    
    for i in range(math.ceil(duration / seg_sec)):
        start = i * seg_sec
        length = seg_sec if (start + seg_sec) <= duration else (duration - start)
        
        # Utwórz tymczasowy plik w sposób bezpieczny dla wszystkich platform
        fd, tmp = tempfile.mkstemp(suffix=path.suffix, prefix='audio2tekst_')
        os.close(fd)
        tmp_path = Path(tmp)
        
        cmd = [
            ffmpeg_path, '-y', '-i', str(path),
            '-ss', str(start), '-t', str(length),
            '-c', 'copy', str(tmp_path)
        ]
        
        try:
            subprocess.run(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                timeout=300,  # 5 minut timeout
                check=True,
                text=True
            )
            parts.append(tmp_path)
        except subprocess.TimeoutExpired:
            if tmp_path.exists():
                tmp_path.unlink()
            raise RuntimeError(f"Przekroczono czas oczekiwania podczas dzielenia pliku (segment {i+1})")
        except subprocess.CalledProcessError as e:
            if tmp_path.exists():
                tmp_path.unlink()
            logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"Błąd podczas dzielenia pliku (segment {i+1}): {e}")
    
    return parts

@st.cache_data
def clean_transcript(text: str) -> str:
    """Czyści transkrypcję z typowych artefaktów mowy."""
    text = re.sub(r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def transcribe_chunks(chunks, _client):
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
        for c in chunks:
            try:
                if c.stat().st_size <= MAX_SIZE:
                    with open(c, 'rb') as f:
                        res = _client.audio.transcriptions.create(
                            model='whisper-1',
                            file=f,
                            language='pl',
                            response_format='text'
                        )
                        texts.append(clean_transcript(str(res)))
                else:
                    logger.warning(f"Plik {c} przekracza maksymalny rozmiar {MAX_SIZE} bajtów")
            except Exception as e:
                logger.error(f"Błąd podczas transkrypcji fragmentu {c}: {str(e)}")
            finally:
                # Bezpieczne usunięcie pliku tymczasowego
                try:
                    if c.exists():
                        c.unlink()
                except Exception as e:
                    logger.warning(f"Nie udało się usunąć pliku tymczasowego {c}: {e}")
    return "\n".join(texts)

def summarize(text: str, _client):
    """Generuje temat i podsumowanie z transkrypcji, dzieląc długi tekst na fragmenty."""
    log_path = Path("logs/summary_errors.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Usunięto komunikat o długim tekście
    logger.info(f"Rozpoczynam summarize() - długość tekstu: {len(text)} znaków")
    try:
        MAX_CHUNK = 8000  # znaków na fragment (bezpieczny limit)
        if len(text) > MAX_CHUNK:
            logger.info("Tekst jest długi - dzielę na fragmenty")
            chunks = [text[i:i+MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]
            logger.info(f"Podzielono na {len(chunks)} fragmentów")
            partial_summaries = []
            for idx, chunk in enumerate(chunks):
                logger.info(f"Przetwarzam fragment {idx+1}/{len(chunks)}")
                with st.spinner(f"Podsumowywanie fragmentu {idx+1}/{len(chunks)}..."):
                    try:
                        prompt = f"Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami (fragment {idx+1}/{len(chunks)}):\n" + chunk
                        completion = _client.chat.completions.create(
                            model='gpt-3.5-turbo',
                            messages=[{'role': 'user', 'content': prompt}],
                            max_tokens=300
                        )
                        if completion and completion.choices and completion.choices[0].message:
                            content = completion.choices[0].message.content
                            partial_summaries.append(content)
                        else:
                            raise Exception("Brak odpowiedzi z modelu OpenAI")
                    except Exception as e:
                        msg = f"Błąd fragmentu {idx+1}: {e}\n"
                        logger.error(msg)
                        with open(log_path, "a", encoding="utf-8") as f:
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                        st.error(f"Błąd podczas podsumowywania fragmentu {idx+1}: {e}")
                        return "Błąd podczas podsumowywania fragmentu", str(e)
            logger.info(f"Zebrałem {len(partial_summaries)} częściowych podsumowań")
            if not partial_summaries:
                st.error("Nie udało się wygenerować żadnego podsumowania fragmentów. Spróbuj ponownie lub sprawdź logi.")
                logger.error("Brak partial_summaries - nie można wygenerować końcowego podsumowania.")
                return "Nie udało się wygenerować podsumowania", "Brak podsumowań fragmentów."
            with st.spinner("Tworzenie końcowego podsumowania..."):
                try:
                    final_prompt = "Oto podsumowania fragmentów długiego tekstu. Na ich podstawie podaj jeden temat i jedno podsumowanie całości (3-5 zdań):\n" + "\n".join(partial_summaries)
                    logger.info(f"Prompt do modelu (final): {final_prompt[:200]}...")
                    completion = _client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': final_prompt}],
                        max_tokens=300
                    )
                    if completion and completion.choices and completion.choices[0].message:
                        content = completion.choices[0].message.content
                        logger.info(f"Odpowiedź modelu (final): {content[:200]}...")
                        lines = content.splitlines() if content else []
                        topic = lines[0] if lines else 'Nie udało się wygenerować tematu'
                        summary = ' '.join(lines[1:]) if len(lines) > 1 else 'Nie udało się wygenerować podsumowania'
                        logger.info(f"Zwracam: topic='{topic[:50]}...', summary='{summary[:50]}...'")
                        return topic, summary
                    else:
                        logger.error("Brak odpowiedzi z modelu OpenAI (final)")
                        raise Exception("Brak odpowiedzi z modelu OpenAI (final)")
                except Exception as e:
                    msg = f"Błąd końcowego podsumowania: {e}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    st.error(f"Błąd podczas generowania końcowego podsumowania: {e}")
                    return "Błąd podczas generowania końcowego podsumowania", str(e)
        else:
            logger.info("Tekst jest krótki - bezpośrednie podsumowanie")
            with st.spinner("Podsumowywanie tekstu..."):
                try:
                    prompt = "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + text
                    completion = _client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': prompt}],
                        max_tokens=300
                    )
                    if completion and completion.choices and completion.choices[0].message:
                        content = completion.choices[0].message.content
                        logger.info(f"Otrzymano krótkie podsumowanie: {content[:100]}...")
                        lines = content.splitlines() if content else []
                        topic = lines[0] if lines else 'Nie udało się wygenerować tematu'
                        summary = ' '.join(lines[1:]) if len(lines) > 1 else 'Nie udało się wygenerować podsumowania'
                        logger.info(f"Zwracam: topic='{topic[:50]}...', summary='{summary[:50]}...'")
                        return topic, summary
                    else:
                        raise Exception("Brak odpowiedzi z modelu OpenAI (krótki tekst)")
                except Exception as e:
                    msg = f"Błąd podsumowania krótkiego tekstu: {e}\n"
                    logger.error(msg)
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
                    st.error(f"Błąd podczas podsumowywania tekstu: {e}")
                    return "Błąd podczas podsumowywania tekstu", str(e)
    except Exception as e:
        # Obsługa błędu braku środków/quota w OpenAI
        if 'insufficient_quota' in str(e).lower() or 'you exceeded your current quota' in str(e).lower() or 'error code: 429' in str(e).lower():
            st.error("Brak środków lub limitu na koncie OpenAI. Sprawdź swój plan i limity na https://platform.openai.com/account/billing.")
            logger.error(f"Błąd quota (429/insufficient_quota): {e}")
            return "Brak środków na koncie OpenAI", str(e)
        msg = f"Błąd ogólny podsumowania: {e}\n"
        logger.error(msg)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}")
        st.error(f"Błąd ogólny podczas podsumowywania: {e}")
        return "Błąd ogólny podczas podsumowywania", str(e)
    
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
            del st.session_state[k]
        # Usuń pliki powiązane z poprzednim UID (jeśli istnieje)
        prev_uid = st.session_state.get('yt_prev_uid', None)
        if prev_uid:
            for folder in (BASE_DIR / 'originals', BASE_DIR / 'transcripts', BASE_DIR / 'summaries'):
                for ext in ('.mp3', '.wav', '.m4a', '.mp4', '.mov', '.avi', '.webm', '.txt'):
                    f = folder / f"{prev_uid}{ext}"
                    if f.exists():
                        try:
                            f.unlink()
                        except Exception as e:
                            logger.warning(f'Nie udało się usunąć pliku {f}: {e}')
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
                st.session_state['yt_ext'] = ext
                # Zapisz UID do późniejszego czyszczenia
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
        deps = check_dependencies()
        if not deps['ffmpeg']['available']:
            st.warning('FFmpeg nie jest dostępny – nie można przekonwertować do MP3.')
        else:
            ffmpeg_path = deps['ffmpeg']['path']
            cmd = [ffmpeg_path, '-y', '-i', str(orig), str(mp3_path)]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except Exception as e:
                st.warning(f'Błąd konwersji do MP3: {e}')
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
    chunks = split_audio(orig)
    text = transcribe_chunks(chunks, client)
    encoding = get_safe_encoding()
    tr.write_text(text, encoding=encoding)
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
        topic, summary = summarize(transcript, client)
        st.session_state[topic_key] = topic
        st.session_state[sum_key] = summary
    # Wyświetl podsumowanie jeśli istnieje
    if st.session_state[topic_key] or st.session_state[sum_key]:
        st.subheader('Temat:')
        st.write(st.session_state[topic_key])
        st.subheader('Podsumowanie:')
        st.write(st.session_state[sum_key])
        # Przycisk pobierania podsumowania
        st.download_button('Pobierz podsumowanie', st.session_state[sum_key], file_name=f'{uid}_podsumowanie.txt')
