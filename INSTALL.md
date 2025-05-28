# 🚀 Szczegółowa instrukcja instalacji

## 🌍 Instrukcje instalacji dla różnych platform

### 🪟 Windows

#### Krok 1: Instalacja Python
1. Pobierz Python z [python.org](https://python.org)
2. Podczas instalacji zaznacz "Add Python to PATH"
3. Sprawdź instalację: `python --version`

#### Krok 2: Instalacja Git (opcjonalne)
```cmd
winget install Git.Git
```

#### Krok 3: Klonowanie projektu
```cmd
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst
```

#### Krok 4: Środowisko wirtualne
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Krok 5: Instalacja zależności
```cmd
pip install -r requirements.txt
```

#### Krok 6: Instalacja FFmpeg
**Opcja A: Chocolatey (zalecane)**
```cmd
# Zainstaluj Chocolatey jeśli nie masz
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Zainstaluj FFmpeg
choco install ffmpeg
```

**Opcja B: Winget**
```cmd
winget install Gyan.FFmpeg
```

**Opcja C: Ręcznie**
1. Pobierz z [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Rozpakuj do `C:\ffmpeg`
3. Dodaj `C:\ffmpeg\bin` do zmiennej PATH

---

### 🍎 macOS

#### Krok 1: Instalacja Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Krok 2: Instalacja Python i Git
```bash
brew install python git
```

#### Krok 3: Klonowanie projektu
```bash
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst
```

#### Krok 4: Środowisko wirtualne
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Krok 5: Instalacja zależności
```bash
pip install -r requirements.txt
```

#### Krok 6: Instalacja FFmpeg
```bash
brew install ffmpeg
```

---

### 🐧 Linux

#### Ubuntu/Debian

```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Python, pip i Git
sudo apt install python3 python3-pip python3-venv git ffmpeg -y

# Klonowanie projektu
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst

# Środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

#### CentOS/RHEL/Rocky Linux

```bash
# Instalacja EPEL
sudo dnf install epel-release -y

# Instalacja zależności
sudo dnf install python3 python3-pip git ffmpeg -y

# Klonowanie projektu
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst

# Środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

#### Fedora

```bash
# Instalacja zależności
sudo dnf install python3 python3-pip git ffmpeg -y

# Klonowanie projektu
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst

# Środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

#### Arch Linux

```bash
# Instalacja zależności
sudo pacman -S python python-pip git ffmpeg

# Klonowanie projektu
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst

# Środowisko wirtualne
python -m venv venv
source venv/bin/activate

# Instalacja zależności
pip install -r requirements.txt
```

---

## 🚀 Uruchamianie

Po zakończeniu instalacji na dowolnym systemie:

```bash
# Aktywuj środowisko wirtualne (jeśli nie jest aktywne)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Uruchom aplikację
streamlit run app.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:8501

## 🔍 Weryfikacja instalacji

Po uruchomieniu aplikacji sprawdź:
1. Panel "ℹ️ Informacje o systemie" - powinien pokazać wykryte zależności
2. Wszystkie zależności (FFmpeg, FFprobe) powinny mieć status ✅

## 🆘 Rozwiązywanie problemów

### Problem: FFmpeg nie został wykrty
**Windows**: Sprawdź czy FFmpeg jest w PATH
**macOS**: Uruchom `brew doctor` i `brew install ffmpeg`
**Linux**: Spróbuj `sudo snap install ffmpeg`

### Problem: Błędy z pip
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problem: Błędy z prawami dostępu (Linux/macOS)
```bash
sudo chown -R $USER:$USER ~/.local
```
