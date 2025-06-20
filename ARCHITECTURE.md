# 🏗️ Architektura Audio2Tekst

## 📊 Diagram systemu

```mermaid
graph TD
    A[👤 Użytkownik] --> B[🌐 Streamlit UI]
    B --> C{📁 Źródło audio}
    C -->|Plik lokalny| D[📂 Upload pliku]
    C -->|YouTube| E[🎬 yt-dlp downloader]
    
    D --> F[🔧 FFmpeg Processing]
    E --> F
    F --> G[✂️ Audio Chunking]
    G --> H[🎧 OpenAI Whisper API]
    H --> I[📝 Transkrypcja]
    I --> J[🤖 GPT-3.5 Summarization]
    J --> K[💾 Export & Storage]
    K --> L[📤 Download Results]
```

## 🔄 Przepływ danych

1. **Input** → User uploads file lub podaje YouTube URL
2. **Processing** → FFmpeg konwertuje do MP3, dzieli na chunki
3. **Transcription** → Whisper API transkrybuje każdy chunk
4. **AI Summary** → GPT-3.5 generuje temat i podsumowanie
5. **Output** → Użytkownik pobiera transkrypcję i podsumowanie

## 🛡️ Bezpieczeństwo

- API keys przez environment variables
- Walidacja formatów plików
- Automatyczne czyszczenie plików tymczasowych
- Rate limiting dla API calls

## ⚡ Optymalizacje

- Chunking dla dużych plików (>25MB)
- Streamlit caching dla lepszej wydajności
- Asynchroniczne przetwarzanie UI
- Cross-platform compatibility layer
