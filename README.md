# 📼 Audio2Tekst 📝

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.0-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross-Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)](https://github.com/AlanSteinbarth/Audio2Tekst)
[![Code Quality](https://github.com/AlanSteinbarth/Audio2Tekst/workflows/Code%20Quality/badge.svg)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)
[![Security](https://github.com/AlanSteinbarth/Audio2Tekst/workflows/Security/badge.svg)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)

> **Profesjonalne narzędzie do transkrypcji audio i video na tekst z automatycznym podsumowaniem**  
> **🌍 Uniwersalna kompatybilność z Windows, macOS i Linux**

Aplikacja webowa stworzona przy użyciu Streamlit, która umożliwia transkrypcję plików audio/video oraz filmów z YouTube na tekst, a następnie generuje ich inteligentne podsumowania przy użyciu OpenAI API.

## 🚀 Funkcjonalności

- ✅ **Transkrypcja plików lokalnych** - obsługa formatów: MP3, WAV, M4A, MP4, MOV, AVI, WEBM
- ✅ **Transkrypcja z YouTube** - bezpośrednia transkrypcja audio z filmów YouTube
- ✅ **Automatyczne podsumowanie** - generowanie tematu i podsumowania przy użyciu GPT-3.5
- ✅ **Inteligentne dzielenie długich tekstów** - automatyczny podział tekstów >8000 znaków na fragmenty
- ✅ **Hierarchiczne podsumowywanie** - fragmenty→podsumowania cząstkowe→finalne podsumowanie całości
- ✅ **Obsługa ograniczeń OpenAI** - rozwiązanie problemów z długością promptu i limitem tokenów
- ✅ **Czyszczenie transkrypcji** - usuwanie artefaktów mowy (um, uh, em, itp.)
- ✅ **Podział długich plików** - automatyczny podział na 5-minutowe segmenty
- ✅ **Eksport wyników** - pobieranie transkrypcji i podsumowań jako pliki tekstowe
- ✅ **Inteligentna konwersja audio** - automatyczne przekształcanie plików video (MP4, WEBM, MOV, AVI) do MP3 podczas pobierania
- ✅ **Ulepszony UI** - przycisk pobierania audio umieszczony bezpośrednio pod odtwarzaczem dla lepszego UX
- ✅ **Cache'owanie** - optymalizacja wydajności dzięki Streamlit cache
- ✅ **Wielojęzyczność** - domyślnie polski, z możliwością rozszerzenia
- 🌍 **Cross-Platform** - pełna kompatybilność z Windows, macOS i Linux
- 🔍 **Automatyczne wykrywanie systemu** - inteligentne dostosowanie do platformy
- ⚡ **Sprawdzanie zależności** - automatyczna weryfikacja FFmpeg/FFprobe

## 🖥️ Kompatybilność systemów

### Obsługiwane platformy
- **🪟 Windows** - Windows 10/11 (x64, ARM64)
- **🍎 macOS** - macOS 10.15+ (Intel, Apple Silicon)
- **🐧 Linux** - Ubuntu, Debian, CentOS, Fedora, Arch Linux

### Automatyczne wykrywanie
Aplikacja automatycznie wykrywa system operacyjny i dostosowuje:
- Ścieżki do plików wykonywalnych (FFmpeg/FFprobe)
- Kodowanie plików tekstowych
- Obsługę plików tymczasowych
- Komendy systemowe

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

#### 🪟 Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### 🍎 macOS / 🐧 Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalacja zależności Python
```bash
pip install -r requirements.txt
```

### 4. Instalacja FFmpeg

#### 🪟 Windows

**Opcja A: Chocolatey (zalecane)**
```cmd
choco install ffmpeg
```

**Opcja B: Winget**
```cmd
winget install Gyan.FFmpeg
```

**Opcja C: Ręcznie**
1. Pobierz FFmpeg z [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Rozpakuj do `C:\ffmpeg`
3. Dodaj `C:\ffmpeg\bin` do PATH

#### 🍎 macOS

**Opcja A: Homebrew (zalecane)**
```bash
brew install ffmpeg
```

**Opcja B: MacPorts**
```bash
sudo port install ffmpeg
```

#### 🐧 Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel

# Fedora
sudo dnf install ffmpeg ffmpeg-devel
```

**Arch Linux:**
```bash
sudo pacman -S ffmpeg
```

**Snap (uniwersalne):**
```bash
sudo snap install ffmpeg
```

### 5. Weryfikacja instalacji

Po uruchomieniu aplikacji sprawdź panel "ℹ️ Informacje o systemie" aby upewnić się, że wszystkie zależności zostały poprawnie wykryte.

### 6. Konfiguracja (opcjonalne)
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
- **Pobieranie audio**: Dla plików video (MP4, WEBM, MOV, AVI) dostępne jest automatyczne pobieranie w formacie MP3
- **Pobieranie audio**: Dla plików audio (MP3, WAV, M4A) dostępne jest pobieranie w oryginalnym formacie

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

### 🔧 Rozwiązywanie problemów

#### Problemy z FFmpeg

**Problem**: FFmpeg nie zostało wykryte
**Rozwiązanie**:
1. Sprawdź czy FFmpeg jest zainstalowane: `ffmpeg -version`
2. Na Windows dodaj FFmpeg do PATH
3. Na macOS upewnij się że Homebrew jest prawidłowo skonfigurowane
4. Na Linux spróbuj zainstalować przez snap: `sudo snap install ffmpeg`

#### Problemy z kodowaniem

**Problem**: Błędne kodowanie znaków w transkrypcji
**Rozwiązanie**: Aplikacja automatycznie wykrywa odpowiednie kodowanie dla systemu (UTF-8 dla Unix, UTF-8-sig dla Windows)

#### Problemy z YouTube

**Problem**: Nie można pobrać audio z YouTube
**Rozwiązanie**: 
1. Sprawdź połączenie internetowe
2. Upewnij się że link jest prawidłowy
3. yt-dlp może wymagać aktualizacji: `pip install --upgrade yt-dlp`

### FAQ

**Q: Aplikacja nie rozpoznaje mojego pliku audio**
A: Sprawdź czy format jest obsługiwany i czy plik nie jest uszkodzony.

**Q: Transkrypcja trwa bardzo długo**
A: Długie pliki są dzielone na segmenty. Czas zależy od długości i jakości audio.

**Q: Błąd "API key not found"**
A: Wprowadź poprawny OpenAI API key w panelu bocznym aplikacji.

**Q: FFmpeg nie zostało wykryte na moim systemie**
A: Sprawdź panel "Informacje o systemie" w aplikacji i zainstaluj FFmpeg zgodnie z instrukcjami dla Twojego systemu operacyjnego.

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
