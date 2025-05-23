"""
Audio2Tekst
=======================================

Ten moduł zawiera implementację aplikacji Streamlit do transkrypcji
plików audio i video na tekst oraz generowania ich podsumowań.

Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
GitHub: https://github.com/AlanSteinbarth
Data: 23 maja 2025
Wersja: 1.0.0
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
from pathlib import Path

# --- Importy zewnętrzne ---
import streamlit as st
import openai
from werkzeug.utils import secure_filename
import yt_dlp

# --- Konfiguracja logowania ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Konfiguracja Streamlit ---
st.set_page_config(page_title="Audio2Tekst", layout="wide")
st.title('📼Audio2Tekst📝')
st.subheader("Przekształć swoje pliki audio i video (oraz z YouTube) na tekst, a następnie zrób z nich zwięzłe podsumowanie" )

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

@st.cache_data
def download_youtube_audio(url: str):
    """Pobiera audio z filmu YouTube i konwertuje do odpowiedniego formatu."""
    tmpdir = tempfile.mkdtemp()
    opts = {
        'format': 'bestaudio[ext=webm]/bestaudio',
        'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    for f in Path(tmpdir).iterdir():
        if f.suffix.lower() in ALLOWED_EXT:
            data = f.read_bytes()
            shutil.rmtree(tmpdir)
            return data, f.suffix.lower()
    shutil.rmtree(tmpdir)
    raise FileNotFoundError("Nie znaleziono pliku audio z YouTube")

@st.cache_data
def get_duration(path: Path) -> float:
    """Zwraca długość pliku audio/video w sekundach."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(path)
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return float(out.stdout.strip())

@st.cache_data
def split_audio(path: Path):
    """Dzieli długie pliki audio na mniejsze części do przetworzenia."""
    duration = get_duration(path)
    seg_sec = CHUNK_MS / 1000
    parts = []
    for i in range(math.ceil(duration / seg_sec)):
        start = i * seg_sec
        length = seg_sec if (start + seg_sec) <= duration else (duration - start)
        fd, tmp = tempfile.mkstemp(suffix=path.suffix)
        os.close(fd)
        tmp_path = Path(tmp)
        cmd = [
            'ffmpeg', '-y', '-i', str(path),
            '-ss', str(start), '-t', str(length),
            '-c', 'copy', str(tmp_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parts.append(tmp_path)
    return parts

@st.cache_data
def clean_transcript(text: str) -> str:
    """Czyści transkrypcję z typowych artefaktów mowy."""
    text = re.sub(r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

@st.cache_data
def transcribe_chunks(chunks):
    """Transkrybuje podzielone fragmenty audio na tekst używając OpenAI API."""
    texts = []
    for c in chunks:
        if c.stat().st_size <= MAX_SIZE:
            with open(c, 'rb') as f:
                res = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=f,
                    language='pl',
                    response_format='text'
                )
                texts.append(clean_transcript(str(res)))
        c.unlink()
    return "\n".join(texts)

@st.cache_data
def summarize(text: str):
    """Generuje temat i podsumowanie z transkrypcji."""
    try:
        prompt = "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + text
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=300
        )
        if completion and completion.choices and completion.choices[0].message:
            content = completion.choices[0].message.content
            lines = content.splitlines() if content else []
            topic = lines[0] if lines else 'Nie udało się wygenerować tematu'
            summary = ' '.join(lines[1:]) if len(lines) > 1 else 'Nie udało się wygenerować podsumowania'
            return topic, summary
    except Exception as e:
        logger.error(f"Błąd podczas generowania podsumowania: {str(e)}")
        return "Błąd podczas generowania podsumowania", str(e)
    return "Nie udało się wygenerować podsumowania", "Spróbuj ponownie lub skontaktuj się z administratorem"

# --- Interfejs użytkownika ---
src = st.sidebar.radio('Wybierz źródło audio:', ['Plik lokalny', 'YouTube'])
if src == 'YouTube':
    url = st.sidebar.text_input('Wklej adres www z YouTube:') or st.stop()
    data, ext = download_youtube_audio(url)
else:
    up = st.sidebar.file_uploader('Wybierz plik', type=[e.strip('.') for e in ALLOWED_EXT]) or st.stop()
    data, ext = up.read(), Path(secure_filename(up.name)).suffix.lower()

# --- Przetwarzanie pliku ---
uid, orig, tr, sm = init_paths(data, ext)
st.audio(orig.read_bytes(), format=ext.lstrip('.'))

# --- Stan sesji ---
done_key = f"done_{uid}"
topic_key = f"topic_{uid}"
sum_key = f"summary_{uid}"
for key, default in [(done_key, False), (topic_key, ''), (sum_key, '')]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Transkrypcja ---
if st.button('Transkrybuj') and not st.session_state[done_key]:
    # dzielenie i transkrypcja
    chunks = split_audio(orig)
    text = transcribe_chunks(chunks)
    tr.write_text(text, encoding='utf-8')
    st.session_state[done_key] = True

# --- Wyświetlanie wyników ---
if st.session_state[done_key]:
    transcript = tr.read_text(encoding='utf-8')
    st.text_area('Transkrypt (możesz edytować tekst i później go zapisać)', transcript, height=300)
    st.download_button('Pobierz transkrypt', transcript, file_name=tr.name)

    # Generowanie podsumowania
    if st.button('Podsumuj') and not st.session_state[topic_key]:
        t, s = summarize(transcript)
        sm.write_text(f"{t}\n\n{s}", encoding='utf-8')
        st.session_state[topic_key] = t
        st.session_state[sum_key] = s

# --- Wyświetlanie podsumowania ---
if st.session_state[topic_key]:
    st.subheader('Temat')
    st.write(st.session_state[topic_key])
    st.subheader('Podsumowanie')
    st.write(st.session_state[sum_key])
    st.download_button('Pobierz podsumowanie', f"{st.session_state[topic_key]}\n\n{st.session_state[sum_key]}", file_name=sm.name)
