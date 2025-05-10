import hashlib
import logging
import re
import math
import tempfile
import os
import shutil
import subprocess
from pathlib import Path

import streamlit as st
import openai
from werkzeug.utils import secure_filename
import yt_dlp

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit setup
st.set_page_config(page_title="Transkrypcja i Podsumowanie", layout="wide")
st.title("Transkrypcja i Podsumowanie Audio/Video")

# API Key
openai.api_key = st.sidebar.text_input("OpenAI API Key", type="password") or st.stop()

# Settings
BASE_DIR = Path("uploads")
for folder in ("originals", "transcripts", "summaries"):
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".avi", ".webm"}
MAX_SIZE = 25 * 1024 * 1024  # 25MB
CHUNK_MS = 5 * 60 * 1000     # 5 minutes in ms

# Helpers
@st.cache_data
def init_paths(data: bytes, ext: str):
    uid = hashlib.md5(data).hexdigest()
    orig = BASE_DIR / "originals" / f"{uid}{ext}"
    tr = BASE_DIR / "transcripts" / f"{uid}.txt"
    sm = BASE_DIR / "summaries" / f"{uid}.txt"
    if not orig.exists():
        orig.write_bytes(data)
    return uid, orig, tr, sm

@st.cache_data
def download_youtube_audio(url: str):
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
    text = re.sub(r"\b(?:em|yhm|um|uh|a{2,}|y{2,})\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

@st.cache_data
def transcribe_chunks(chunks):
    texts = []
    for c in chunks:
        if c.stat().st_size <= MAX_SIZE:
            with open(c, 'rb') as f:
                # jawne ustawienie języka polskiego i formatu tekstowego
                res = openai.Audio.transcribe(
                    model='whisper-1',
                    file=f,
                    language='pl',
                    response_format='text'
                )
            texts.append(clean_transcript(res))
        c.unlink()
    return "\n".join(texts)

@st.cache_data
def summarize(text: str):
    prompt = "Podaj temat w jednym zdaniu i podsumowanie 3-5 zdaniami:\n" + text
    res = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=300
    )
    lines = res.choices[0].message.content.splitlines()
    topic = lines[0] if lines else ''
    summary = ' '.join(lines[1:])
    return topic, summary

# UI Selection
src = st.sidebar.radio('Źródło', ['Plik lokalny', 'YouTube'])
if src == 'YouTube':
    url = st.sidebar.text_input('URL YouTube') or st.stop()
    data, ext = download_youtube_audio(url)
else:
    up = st.sidebar.file_uploader('Wybierz plik', type=[e.strip('.') for e in ALLOWED_EXT]) or st.stop()
    data, ext = up.read(), Path(secure_filename(up.name)).suffix.lower()

# Initialize and playback
uid, orig, tr, sm = init_paths(data, ext)
st.audio(orig.read_bytes(), format=ext.lstrip('.'))

# Session state keys
done_key = f"done_{uid}"
topic_key = f"topic_{uid}"
sum_key = f"summary_{uid}"
for key, default in [(done_key, False), (topic_key, ''), (sum_key, '')]:
    if key not in st.session_state:
        st.session_state[key] = default

# Transcription block
if st.button('Transkrybuj') and not st.session_state[done_key]:
    # dzielenie i transkrypcja
    chunks = split_audio(orig)
    text = transcribe_chunks(chunks)
    tr.write_text(text, encoding='utf-8')
    st.session_state[done_key] = True

# Display transcript and download
if st.session_state[done_key]:
    transcript = tr.read_text(encoding='utf-8')
    st.text_area('Transkrypt', transcript, height=300)
    st.download_button('Pobierz transkrypt', transcript, file_name=tr.name)

    # Summary generation
    if st.button('Podsumuj') and not st.session_state[topic_key]:
        t, s = summarize(transcript)
        sm.write_text(f"{t}\n\n{s}", encoding='utf-8')
        st.session_state[topic_key] = t
        st.session_state[sum_key] = s

# Display summary and download
if st.session_state[topic_key]:
    st.subheader('Temat')
    st.write(st.session_state[topic_key])
    st.subheader('Podsumowanie')
    st.write(st.session_state[sum_key])
    st.download_button('Pobierz podsumowanie', f"{st.session_state[topic_key]}\n\n{st.session_state[sum_key]}", file_name=sm.name)
