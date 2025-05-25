# 📼 Audio2Tekst 📝

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.0-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://github.com/AlanSteinbarth/Audio2Tekst/workflows/Code%20Quality/badge.svg)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)
[![Security](https://github.com/AlanSteinbarth/Audio2Tekst/workflows/Security/badge.svg)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)

> **Profesjonalne narzędzie do transkrypcji audio i video na tekst z automatycznym podsumowaniem**

Aplikacja webowa stworzona przy użyciu Streamlit, która umożliwia transkrypcję plików audio/video oraz filmów z YouTube na tekst, a następnie generuje ich inteligentne podsumowania przy użyciu OpenAI API.

## 🚀 Funkcjonalności

- ✅ **Transkrypcja plików lokalnych** - obsługa formatów: MP3, WAV, M4A, MP4, MOV, AVI, WEBM
- ✅ **Transkrypcja z YouTube** - bezpośrednia transkrypcja audio z filmów YouTube
- ✅ **Automatyczne podsumowanie** - generowanie tematu i podsumowania przy użyciu GPT-3.5
- ✅ **Czyszczenie transkrypcji** - usuwanie artefaktów mowy (um, uh, em, itp.)
- ✅ **Podział długich plików** - automatyczny podział na 5-minutowe segmenty
- ✅ **Eksport wyników** - pobieranie transkrypcji i podsumowań jako pliki tekstowe
- ✅ **Cache'owanie** - optymalizacja wydajności dzięki Streamlit cache
- ✅ **Wielojęzyczność** - domyślnie polski, z możliwością rozszerzenia

## 📋 Wymagania

### Wymagania systemowe
- Python 3.8+
- FFmpeg (do przetwarzania audio/video)
- OpenAI API Key

### Obsługiwane formaty
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, MOV, AVI, WEBM
- **Źródła**: Pliki lokalne, YouTube

## 🛠️ Instalacja

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst
```

### 2. Tworzenie środowiska wirtualnego
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 4. Instalacja FFmpeg

#### Windows
```bash
# Przy użyciu Chocolatey
choco install ffmpeg

# Lub pobierz z https://ffmpeg.org/download.html
```

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### 5. Konfiguracja
```bash
# Skopiuj przykładowy plik konfiguracyjny
cp .env.example .env

# Edytuj .env i dodaj swój OpenAI API Key
```

## 🚀 Uruchamianie

```bash
streamlit run app.py
```

Aplikacja będzie dostępna pod adresem: `http://localhost:8501`

## 📖 Instrukcja użytkowania

### 1. Konfiguracja API Key
- Otwórz aplikację w przeglądarce
- W panelu bocznym wprowadź swój OpenAI API Key
- Key jest wymagany do funkcji transkrypcji i podsumowania

### 2. Wybór źródła audio
**Opcja A: Plik lokalny**
- Wybierz "Plik lokalny" w panelu bocznym
- Przeciągnij i upuść plik lub kliknij "Browse files"
- Obsługiwane formaty: MP3, WAV, M4A, MP4, MOV, AVI, WEBM

**Opcja B: YouTube**
- Wybierz "YouTube" w panelu bocznym
- Wklej link do filmu YouTube
- Aplikacja automatycznie wyodrębni audio

### 3. Transkrypcja
- Po załadowaniu pliku kliknij "Transkrybuj"
- Długie pliki są automatycznie dzielone na 5-minutowe segmenty
- Postęp jest wyświetlany w czasie rzeczywistym

### 4. Edycja i eksport
- Transkrypcja pojawi się w edytowalnym polu tekstowym
- Możesz ręcznie poprawić tekst przed podsumowaniem
- Kliknij "Pobierz transkrypt" aby zapisać plik .txt

### 5. Podsumowanie
- Kliknij "Podsumuj" aby wygenerować temat i podsumowanie
- AI wygeneruje jednoznaczny temat i 3-5 zdaniowe podsumowanie
- Kliknij "Pobierz podsumowanie" aby zapisać wyniki

## ⚙️ Konfiguracja

### Zmienne środowiskowe (.env)
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here

# Application Settings
MAX_FILE_SIZE=25  # MB
CHUNK_DURATION=5  # minutes
DEFAULT_LANGUAGE=pl

# Logging
LOG_LEVEL=INFO
```

### Ustawienia zaawansowane
- **MAX_FILE_SIZE**: Maksymalny rozmiar pliku (domyślnie 25MB)
- **CHUNK_DURATION**: Długość segmentów podziału (domyślnie 5 minut)
- **DEFAULT_LANGUAGE**: Język transkrypcji (domyślnie 'pl')

## 🏗️ Architektura

```
Audio2Tekst/
├── app.py                 # Główna aplikacja Streamlit
├── uploads/              # Folder przechowywania plików
│   ├── originals/        # Oryginalne pliki audio/video
│   ├── transcripts/      # Wygenerowane transkrypcje
│   └── summaries/        # Wygenerowane podsumowania
├── .streamlit/           # Konfiguracja Streamlit
├── requirements.txt      # Zależności Python
└── .env.example         # Przykład konfiguracji
```

## 🔒 Bezpieczeństwo

- **API Keys**: Nigdy nie commituj kluczy API do repozytorium
- **Pliki tymczasowe**: Automatyczne czyszczenie po przetworzeniu
- **Walidacja plików**: Sprawdzanie rozszerzeń i rozmiarów
- **Rate limiting**: Respektowanie limitów OpenAI API

## 🧪 Testowanie

```bash
# Uruchomienie testów
python -m pytest tests/

# Testy z pokryciem kodu
python -m pytest --cov=app tests/

# Linting kodu
flake8 app.py
bandit -r app.py
```

## 🤝 Wkład w rozwój

Zapraszamy do współpracy! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) po szczegółowe instrukcje.

### Szybki start dla deweloperów
1. Fork repozytorium
2. Stwórz branch funkcjonalności: `git checkout -b feature/amazing-feature`
3. Commituj zmiany: `git commit -m 'feat: add amazing feature'`
4. Push do brancha: `git push origin feature/amazing-feature`
5. Otwórz Pull Request

## 📝 Changelog

Zobacz [CHANGELOG.md](CHANGELOG.md) po pełną historię zmian.

## 🆘 Wsparcie

### FAQ

**Q: Aplikacja nie rozpoznaje mojego pliku audio**
A: Sprawdź czy format jest obsługiwany i czy plik nie jest uszkodzony.

**Q: Transkrypcja trwa bardzo długo**
A: Długie pliki są dzielone na segmenty. Czas zależy od długości i jakości audio.

**Q: Błąd "API key not found"**
A: Wprowadź poprawny OpenAI API key w panelu bocznym aplikacji.

### Zgłaszanie błędów
- [Issues na GitHub](https://github.com/AlanSteinbarth/Audio2Tekst/issues)
- [Security Policy](SECURITY.md) dla problemów bezpieczeństwa

### Kontakt
- **Autor**: Alan Steinbarth
- **Email**: alan.steinbarth@gmail.com
- **GitHub**: [@AlanSteinbarth](https://github.com/AlanSteinbarth)

## 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

## 🙏 Podziękowania

- [Streamlit](https://streamlit.io/) - za fantastyczny framework
- [OpenAI](https://openai.com/) - za Whisper API i GPT modele
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - za wsparcie YouTube
- Społeczność open source za inspirację i feedback

---

<div align="center">

**[⬆ Powrót do góry](#-audio2tekst-)**

Made with ❤️ by [Alan Steinbarth](https://github.com/AlanSteinbarth)

</div>
