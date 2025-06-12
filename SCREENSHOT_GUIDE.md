# 📸 Instrukcja tworzenia screenshots dla Audio2Tekst

## 🎯 Cel
Zastąpienie placeholder images prawdziwymi zrzutami ekranu aplikacji Audio2Tekst w zakładce "📸 Screenshots".

## 🚀 Przygotowanie

### 1. Uruchomienie aplikacji
```bash
cd /path/to/Audio2Tekst2
source venv/bin/activate  # Aktywacja środowiska wirtualnego
streamlit run app.py
```

Aplikacja uruchomi się pod adresem: `http://localhost:8501`

### 2. Przygotowanie przykładowych plików
- **Audio**: Przygotuj przykładowy plik MP3/WAV (do 5MB)
- **YouTube**: Znajdź krótki film YouTube (2-3 minuty)
- **API Key**: Upewnij się, że masz skonfigurowany OpenAI API Key

## 📸 Lista screenshots do zrobienia

### Zakładka 1: 🎵 Transkrypcja

#### A. Panel wyboru źródła (500x350)
**Plik docelowy**: `assets/screenshots/panel-wyboru.png`
**Co pokazać**:
- Panel boczny z opcjami "Plik lokalny" / "YouTube"
- Pole upload pliku lub input YouTube URL
- Panel "Informacje o systemie" rozwinięty
- Pokazanie statusu API Key

**Kroki**:
1. Otwórz aplikację
2. W panelu bocznym wybierz "Plik lokalny"
3. Rozwiń panel "ℹ️ Informacje o systemie"
4. Zrób screenshot panelu bocznego (crop do 500x350)

#### B. Główny obszar roboczy (500x350)
**Plik docelowy**: `assets/screenshots/obszar-glowny.png`
**Co pokazać**:
- Odtwarzacz audio z załadowanym plikiem
- Przycisk "Pobierz audio"
- Przycisk "Transkrybuj"
- Informacje o pliku (rozmiar, format)

**Kroki**:
1. Upload przykładowego pliku audio
2. Zrób screenshot głównego obszaru z odtwarzaczem
3. Crop do 500x350

#### C. Proces transkrypcji - 4 screenshots (200x150 każdy)

**1. Upload (200x150)**
Plik: `assets/screenshots/proces-1-upload.png`
- Moment po wybraniu pliku, przed transkrypcją

**2. Analiza (200x150)**
Plik: `assets/screenshots/proces-2-analiza.png`
- Komunikat o liczbie fragmentów audio
- Lista fragmentów z rozmiarami

**3. Transkrypcja (200x150)**
Plik: `assets/screenshots/proces-3-transkrypcja.png`
- Spinner "Transkrypcja w toku..."
- Komunikaty o postępie fragmentów

**4. Wyniki (200x150)**
Plik: `assets/screenshots/proces-4-wyniki.png`
- Pole tekstowe z transkrypcją
- Przycisk "Pobierz transkrypt"

#### D. Obszar transkrypcji (500x300)
**Plik docelowy**: `assets/screenshots/obszar-transkrypcji.png`
**Co pokazać**:
- Wypełnione pole tekstowe z przykładową transkrypcją
- Przycisk "Pobierz transkrypt"
- Przycisk "Podsumuj"

#### E. Podsumowanie AI (500x300)
**Plik docelowy**: `assets/screenshots/podsumowanie-ai.png`
**Co pokazać**:
- Sekcja "Temat:" z przykładowym tematem
- Sekcja "Podsumowanie:" z przykładowym podsumowaniem
- Przycisk "Pobierz podsumowanie"

#### F. Funkcje zaawansowane - 3 screenshots (300x200 każdy)

**1. YouTube Integration (300x200)**
Plik: `assets/screenshots/youtube-integration.png`
- Panel z wklejonym linkiem YouTube
- Komunikat "Pomyślnie pobrano audio z YouTube!"

**2. System Diagnostics (300x200)**
Plik: `assets/screenshots/system-diagnostics.png`
- Rozwinięty panel "Informacje o systemie"
- Status FFmpeg/FFprobe
- Informacje o platformie

**3. Progress Tracking (300x200)**
Plik: `assets/screenshots/progress-tracking.png`
- Komunikaty o postępie transkrypcji
- Informacje o fragmentach

### Zakładka 2: 📸 Screenshots
Ta zakładka już zawiera galerię - wystarczy prawdziwe screenshots.

### Zakładka 3: ℹ️ O aplikacji

#### G. Screenshot zakładki "O aplikacji" (800x600)
**Plik docelowy**: `assets/screenshots/o-aplikacji.png`
**Co pokazać**:
- Hero section z informacjami o wersji
- Główne funkcje i cross-platform support
- Technologie i performance metrics

### Zakładka 4: ⚙️ Ustawienia

#### H. Screenshot zakładki "Ustawienia" (800x600)
**Plik docelowy**: `assets/screenshots/ustawienia.png`
**Co pokazać**:
- Informacje o systemie
- Status zależności
- Wyniki testów diagnostycznych

## 🛠️ Narzędzia do screenshots

### macOS (zalecane)
```bash
# Zrzut wybranego obszaru
Cmd + Shift + 4

# Zrzut okna
Cmd + Shift + 4 + Spacja + klik na okno

# Screenshot z opóźnieniem (5 sekund)
Cmd + Shift + 5
```

### Alternatywne narzędzia
- **CleanShot X** - profesjonalne screenshots z adnotacjami
- **Kap** - do tworzenia GIF z demo
- **LICEcap** - darmowy do GIF

## 📐 Specyfikacje techniczne

### Rozmiary obrazów
- **Hero images**: 800x400 px
- **Interface screenshots**: 500x350 px
- **Process steps**: 200x150 px
- **Feature showcases**: 300x200 px
- **Full tab screenshots**: 800x600 px

### Format i jakość
- **Format**: PNG (dla przezroczystości) lub JPG
- **Jakość**: Wysoka rozdzielczość (Retina-ready)
- **DPI**: 144 DPI lub wyższe
- **Rozmiar pliku**: < 1MB per image

### Optymalizacja
```bash
# Kompresja PNG
pngquant --quality=65-90 input.png --output output.png

# Konwersja do WebP (opcjonalnie)
cwebp -q 85 input.png -o output.webp
```

## 🔄 Proces aktualizacji

### 1. Zastąpienie placeholder URLs
W pliku `app.py` znajdź i zastąp:
```python
# PRZED
st.image("https://via.placeholder.com/500x350/3498DB/FFFFFF?text=...", 
         caption="...")

# PO
st.image("assets/screenshots/nazwa-pliku.png", 
         caption="...")
```

### 2. Commit zmian
```bash
git add assets/screenshots/
git commit -m "📸 ADD: Real screenshots replacing placeholders"
git push
```

## 📋 Checklist

- [x] 📁 Panel wyboru źródła (500x350)
- [x] 🖥️ Główny obszar roboczy (500x350)
- [x] 📤 Proces 1: Upload (200x150)
- [x] 🔍 Proces 2: Analiza (200x150)
- [x] ⚙️ Proces 3: Transkrypcja (200x150)
- [x] ✅ Proces 4: Wyniki (200x150)
- [x] 📝 Obszar transkrypcji (500x300)
- [x] 🤖 Podsumowanie AI (500x300)
- [x] 🌐 YouTube Integration (300x200)
- [x] 🔧 System Diagnostics (300x200)
- [x] 📊 Progress Tracking (300x200)
- [x] ℹ️ Zakładka "O aplikacji" (800x600)
- [x] ⚙️ Zakładka "Ustawienia" (800x600)
- [x] 🔄 Aktualizacja URLs w kodzie
- [x] 📤 Commit i push zmian

✅ **WSZYSTKIE ZADANIA UKOŃCZONE!**

## 🎬 Bonus: Demo GIF

### Tworzenie demo GIF (opcjonalnie)
**Plik docelowy**: `assets/demo/demo.gif`
**Długość**: 30-60 sekund
**Rozmiar**: 800x400px, <5MB

**Scenariusz**:
1. Upload pliku audio (3s)
2. Kliknięcie "Transkrybuj" (2s)
3. Pokazanie postępu transkrypcji (10s)
4. Wyświetlenie wyników (5s)
5. Kliknięcie "Podsumuj" (2s)
6. Pokazanie podsumowania AI (5s)
7. Pobieranie plików (3s)

---

**Po wykonaniu**: Będziesz mieć kompletną galerię screenshots, która sprawi, że Twoje repozytorium będzie wyglądać bardzo profesjonalnie! 🚀
