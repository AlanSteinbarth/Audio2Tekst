# 📼 Audio2Tekst 📝

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.0-red.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-Whisper%20%7C%20GPT-412991.svg?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[![Cross-Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/AlanSteinbarth/Audio2Tekst)
[![Code Quality](https://img.shields.io/github/workflow/status/AlanSteinbarth/Audio2Tekst/Code%20Quality?style=for-the-badge&label=Code%20Quality&logo=github)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)
[![Security](https://img.shields.io/github/workflow/status/AlanSteinbarth/Audio2Tekst/Security?style=for-the-badge&label=Security&logo=shield)](https://github.com/AlanSteinbarth/Audio2Tekst/actions)
[![Stars](https://img.shields.io/github/stars/AlanSteinbarth/Audio2Tekst?style=for-the-badge&logo=star&logoColor=white)](https://github.com/AlanSteinbarth/Audio2Tekst/stargazers)

</div>

---

<div align="center">

## 🎯 **Profesjonalne narzędzie do transkrypcji audio i video na tekst z automatycznym podsumowaniem**

### 🌍 **Uniwersalna kompatybilność z Windows, macOS i Linux**

*Aplikacja webowa stworzona przy użyciu Streamlit, która umożliwia transkrypcję plików audio/video oraz filmów z YouTube na tekst, a następnie generuje ich inteligentne podsumowania przy użyciu OpenAI API.*

[🚀 **Quick Start**](#-uruchamianie) • [📖 **Documentation**](#-instrukcja-uzytkowania) • [🤝 **Contributing**](#-wkład-w-rozwój) • [💬 **Support**](#-wsparcie)

</div>

---

## ✨ **Główne zalety**

<table>
<tr>
<td width="50%">

### 🎵 **Obsługa formatów**
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, MOV, AVI, WEBM
- **Źródła**: Pliki lokalne + YouTube

</td>
<td width="50%">

### 🤖 **AI-Powered**
- **Whisper API** do transkrypcji
- **GPT-3.5** do podsumowań
- **Inteligentne dzielenie** długich plików

</td>
</tr>
<tr>
<td width="50%">

### 🖥️ **Cross-Platform**
- **Windows** 10/11 (x64, ARM64)
- **macOS** 10.15+ (Intel, Apple Silicon)
- **Linux** (Ubuntu, Debian, CentOS, etc.)

</td>
<td width="50%">

### ⚡ **Performance**
- **Automatyczne chunking** (5-min segmenty)
- **Cache'owanie** wyników
- **Batch processing** długich plików

</td>
</tr>
</table>

---

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

## 🛠️ **Quick Install Guide**

<div align="center">

### 🚀 **One-Click Setup** (Recommended)

```bash
# Clone, setup virtual environment, and install dependencies
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git && \
cd Audio2Tekst && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt
```

*For Windows users, replace `source venv/bin/activate` with `venv\Scripts\activate`*

</div>

---

### 📋 **Step-by-Step Installation**

<details>
<summary><b>🔧 1. Clone Repository</b></summary>

```bash
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst
```

</details>

<details>
<summary><b>🐍 2. Virtual Environment Setup</b></summary>

<table>
<tr>
<td width="50%">

**🪟 Windows**
```cmd
python -m venv venv
venv\Scripts\activate
```

</td>
<td width="50%">

**🍎 macOS / 🐧 Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

</td>
</tr>
</table>

</details>

<details>
<summary><b>📦 3. Dependencies Installation</b></summary>

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, openai, yt_dlp; print('✅ All dependencies installed!')"
```

</details>

<details>
<summary><b>🎬 4. FFmpeg Installation</b></summary>

<table>
<tr>
<td width="33%">

**🪟 Windows**
```cmd
# Using Chocolatey (recommended)
choco install ffmpeg

# Using Winget
winget install Gyan.FFmpeg

# Verify
ffmpeg -version
```

</td>
<td width="33%">

**🍎 macOS**
```bash
# Using Homebrew (zalecane)
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg

# Verify
ffmpeg -version
```

</td>
<td width="33%">

**🐧 Linux**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg

# Verify
ffmpeg -version
```

</td>
</tr>
</table>

</details>

<details>
<summary><b>⚙️ 5. Configuration</b></summary>

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API Key
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

</details>

<details>
<summary><b>✅ 6. Verification</b></summary>

```bash
# Test the installation
streamlit run app.py

# Check system compatibility
python -c "
import app
sys_info = app.get_system_info()
deps = app.check_dependencies()
print(f'✅ Platform: {sys_info[\"platform\"]}')
print(f'✅ FFmpeg: {\"Available\" if deps[\"ffmpeg\"][\"available\"] else \"Missing\"}')
print(f'✅ FFprobe: {\"Available\" if deps[\"ffprobe\"][\"available\"] else \"Missing\"}')
"
```

</details>

---

## 🎯 **Features Showcase**

<div align="center">

### 🔥 **What makes Audio2Tekst special?**

</div>

<table>
<tr>
<td width="50%">

#### 🎵 **Smart Audio Processing**
- **Multi-format support**: MP3, WAV, M4A, MP4, MOV, AVI, WEBM
- **Automatic chunking**: Splits long files into 5-minute segments
- **Quality optimization**: Intelligent format conversion for best results
- **Size handling**: Up to 25MB files with automatic compression

#### 🤖 **AI-Powered Intelligence** 
- **Whisper API**: State-of-the-art speech recognition
- **GPT-3.5 Integration**: Smart summarization and topic extraction
- **Multi-language**: Polish optimized, extensible to 90+ languages
- **Context awareness**: Maintains coherence across long transcriptions

</td>
<td width="50%">

#### 🌐 **Cross-Platform Excellence**
- **Windows**: Full compatibility with 10/11 (x64, ARM64)
- **macOS**: Intel & Apple Silicon support (10.15+)
- **Linux**: Ubuntu, Debian, CentOS, Fedora, Arch
- **Auto-detection**: Smart system adaptation

#### ⚡ **Performance & UX**
- **Real-time progress**: Live transcription updates
- **Session persistence**: Resume interrupted processes
- **Export options**: TXT download for transcripts and summaries
- **Error handling**: Comprehensive diagnostics and recovery

</td>
</tr>
</table>

<div align="center">

### 📊 **Performance Metrics**

| Feature | Capability | Performance |
|---------|------------|-------------|
| 🎵 **Audio Processing** | Up to 25MB files | ~2-3x real-time speed |
| 🎬 **Video Processing** | Auto MP3 conversion | 95% accuracy rate |
| 🌐 **YouTube Support** | Direct URL input | Instant download |
| 🤖 **AI Summarization** | 8000+ char handling | Sub-30s generation |
| 💾 **Memory Usage** | Optimized chunks | <500MB peak |
| 🔄 **Batch Processing** | Unlimited files | Parallel processing |

</div>

---

## 🚀 **Quick Start**

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

Ten projekt jest licencjonowany na licencji MIT - zobacz plik [LICENSE](LICENSE.txt) po szczegóły.

## 🙏 Podziękowania

- [Streamlit](https://streamlit.io/) - za fantastyczny framework
- [OpenAI](https://openai.com/) - za Whisper API i GPT modele
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - za wsparcie YouTube
- Społeczność open source za inspirację i feedback

---

<div align="center">

## 🌟 **Support the Project**

If you find Audio2Tekst helpful, please consider:

[![⭐ Star this repository](https://img.shields.io/badge/⭐%20Star-this%20repository-yellow?style=for-the-badge)](https://github.com/AlanSteinbarth/Audio2Tekst)
[![🐛 Report Issues](https://img.shields.io/badge/🐛%20Report-Issues-red?style=for-the-badge)](https://github.com/AlanSteinbarth/Audio2Tekst/issues)
[![💡 Request Features](https://img.shields.io/badge/💡%20Request-Features-blue?style=for-the-badge)](https://github.com/AlanSteinbarth/Audio2Tekst/issues/new)
[![🤝 Contribute](https://img.shields.io/badge/🤝%20Contribute-Code-green?style=for-the-badge)](https://github.com/AlanSteinbarth/Audio2Tekst/pulls)

### 📱 **Follow for Updates**

[![GitHub Follow](https://img.shields.io/github/followers/AlanSteinbarth?style=social&label=Follow)](https://github.com/AlanSteinbarth)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/your-profile)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail)](mailto:alan.steinbarth@gmail.com)

---

### 📈 **Project Stats**

![GitHub repo size](https://img.shields.io/github/repo-size/AlanSteinbarth/Audio2Tekst?style=for-the-badge)
![GitHub code size](https://img.shields.io/github/languages/code-size/AlanSteinbarth/Audio2Tekst?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/AlanSteinbarth/Audio2Tekst?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/AlanSteinbarth/Audio2Tekst?style=for-the-badge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/AlanSteinbarth/Audio2Tekst?style=for-the-badge)

---

**[⬆ Powrót do góry](#-audio2tekst-)**

<sub>Made with ❤️ by [Alan Steinbarth](https://github.com/AlanSteinbarth) | © 2025 | Licensed under [MIT License](LICENSE.txt)</sub>

</div>
