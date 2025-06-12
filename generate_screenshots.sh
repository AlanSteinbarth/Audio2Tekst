#!/bin/bash
# Generator demo screenshots dla Audio2Tekst
# Tworzy profesjonalnie wyglądające przykładowe screenshots

set -e

SCREENSHOTS_DIR="assets/screenshots"
mkdir -p "$SCREENSHOTS_DIR"

echo "🚀 Generuję demo screenshots dla Audio2Tekst..."

# Kolory i style
MAIN_COLOR="#3498DB"
SECONDARY_COLOR="#2ECC71"
ACCENT_COLOR="#E74C3C"
DARK_COLOR="#2C3E50"
LIGHT_COLOR="#ECF0F1"

# 1. Panel wyboru źródła (500x350)
echo "📱 Tworzę panel-wyboru.png..."
magick -size 500x350 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 18 -annotate +20+40 "Audio2Tekst - Panel wyboru" \
    -fill "$MAIN_COLOR" -pointsize 14 -annotate +20+80 "📁 Plik lokalny" \
    -fill "gray" -pointsize 12 -annotate +20+110 "🌐 YouTube URL" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +20+150 "ℹ️ Informacje o systemie:" \
    -fill "$SECONDARY_COLOR" -pointsize 10 -annotate +30+180 "✅ FFmpeg: Dostępny" \
    -fill "$SECONDARY_COLOR" -pointsize 10 -annotate +30+200 "✅ OpenAI API: Skonfigurowane" \
    -fill "$SECONDARY_COLOR" -pointsize 10 -annotate +30+220 "✅ Python: 3.11.11" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +20+260 "Status: Gotowy do transkrypcji" \
    -stroke "$MAIN_COLOR" -strokewidth 2 -fill none \
    -draw "rectangle 15,60 480,330" \
    "$SCREENSHOTS_DIR/panel-wyboru.png"

# 2. Główny obszar roboczy (500x350)
echo "🖥️ Tworzę obszar-glowny.png..."
magick -size 500x350 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 16 -annotate +20+40 "Obszar roboczy - Upload pliku" \
    -fill "$MAIN_COLOR" -pointsize 12 -annotate +20+80 "📤 Przeciągnij plik audio lub kliknij 'Browse files'" \
    -stroke "$MAIN_COLOR" -strokewidth 2 -fill "$LIGHT_COLOR" \
    -draw "rectangle 20,100 480,200" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+150 "Obsługiwane formaty: MP3, WAV, M4A, FLAC" \
    -fill "$SECONDARY_COLOR" -pointsize 12 -annotate +20+240 "🎵 demo-audio.aiff (396 KB)" \
    -fill "$ACCENT_COLOR" -pointsize 10 -annotate +20+270 "▶️ Odtwarzacz audio" \
    -stroke "$SECONDARY_COLOR" -strokewidth 1 -fill "$SECONDARY_COLOR" \
    -draw "rectangle 20,290 150,320" \
    -fill "white" -pointsize 10 -annotate +30+310 "🚀 Transkrybuj" \
    "$SCREENSHOTS_DIR/obszar-glowny.png"

# 3-6. Proces transkrypcji (200x150 każdy)
echo "⚙️ Tworzę screenshots procesu..."

# Proces 1: Upload
magick -size 200x150 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +10+25 "1. Upload" \
    -fill "$MAIN_COLOR" -pointsize 9 -annotate +10+50 "📤 Plik wybrany" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+70 "demo-audio.aiff" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+85 "Rozmiar: 396 KB" \
    -fill "$SECONDARY_COLOR" -pointsize 8 -annotate +10+100 "✅ Gotowy" \
    -stroke "$MAIN_COLOR" -strokewidth 1 -fill none \
    -draw "rectangle 5,5 195,145" \
    "$SCREENSHOTS_DIR/proces-1-upload.png"

# Proces 2: Analiza
magick -size 200x150 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +10+25 "2. Analiza" \
    -fill "$MAIN_COLOR" -pointsize 9 -annotate +10+50 "🔍 Analizuję plik" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+70 "Fragmenty: 2" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+85 "Czas: 00:15" \
    -fill "$SECONDARY_COLOR" -pointsize 8 -annotate +10+100 "⚡ W toku..." \
    -stroke "$MAIN_COLOR" -strokewidth 1 -fill none \
    -draw "rectangle 5,5 195,145" \
    "$SCREENSHOTS_DIR/proces-2-analiza.png"

# Proces 3: Transkrypcja
magick -size 200x150 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +10+25 "3. Transkrypcja" \
    -fill "$MAIN_COLOR" -pointsize 9 -annotate +10+50 "🤖 OpenAI API" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+70 "Fragment 1/2" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+85 "Postęp: 50%" \
    -fill "$ACCENT_COLOR" -pointsize 8 -annotate +10+100 "⏳ Przetwarzam..." \
    -stroke "$ACCENT_COLOR" -strokewidth 1 -fill none \
    -draw "rectangle 5,5 195,145" \
    "$SCREENSHOTS_DIR/proces-3-transkrypcja.png"

# Proces 4: Wyniki
magick -size 200x150 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +10+25 "4. Wyniki" \
    -fill "$MAIN_COLOR" -pointsize 9 -annotate +10+50 "✅ Ukończono" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+70 "Transkrypt gotowy" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +10+85 "Długość: 45 słów" \
    -fill "$SECONDARY_COLOR" -pointsize 8 -annotate +10+100 "📄 Pobierz" \
    -stroke "$SECONDARY_COLOR" -strokewidth 1 -fill none \
    -draw "rectangle 5,5 195,145" \
    "$SCREENSHOTS_DIR/proces-4-wyniki.png"

# 7. Obszar transkrypcji (500x300)
echo "📝 Tworzę obszar-transkrypcji.png..."
magick -size 500x300 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 14 -annotate +20+30 "📝 Wynik transkrypcji" \
    -stroke "$DARK_COLOR" -strokewidth 1 -fill "white" \
    -draw "rectangle 20,50 480,220" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+75 "To jest przykładowy plik audio dla aplikacji Audio2Tekst." \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+95 "Dzięki tej aplikacji możesz łatwo transkrybować" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+115 "audio na tekst. Aplikacja obsługuje różne formaty" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+135 "i wykorzystuje zaawansowane AI do precyzyjnej" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+155 "transkrypcji mowy na tekst." \
    -stroke "$MAIN_COLOR" -strokewidth 1 -fill "$MAIN_COLOR" \
    -draw "rectangle 20,240 140,270" \
    -fill "white" -pointsize 10 -annotate +30,260 "📄 Pobierz transkrypt" \
    -stroke "$SECONDARY_COLOR" -strokewidth 1 -fill "$SECONDARY_COLOR" \
    -draw "rectangle 160,240 250,270" \
    -fill "white" -pointsize 10 -annotate +170,260 "🤖 Podsumuj" \
    "$SCREENSHOTS_DIR/obszar-transkrypcji.png"

# 8. Podsumowanie AI (500x300)
echo "🤖 Tworzę podsumowanie-ai.png..."
magick -size 500x300 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 14 -annotate +20+30 "🤖 Podsumowanie AI" \
    -fill "$MAIN_COLOR" -pointsize 12 -annotate +20+60 "Temat:" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +30+80 "Prezentacja aplikacji Audio2Tekst" \
    -fill "$MAIN_COLOR" -pointsize 12 -annotate +20+110 "Podsumowanie:" \
    -stroke "$DARK_COLOR" -strokewidth 1 -fill "white" \
    -draw "rectangle 20,130 480,220" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +30+150 "Nagranie przedstawia możliwości aplikacji Audio2Tekst," \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +30+165 "która umożliwia automatyczną transkrypcję plików audio" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +30+180 "na tekst. Aplikacja charakteryzuje się łatwością" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +30+195 "obsługi i wysoką precyzją transkrypcji." \
    -stroke "$SECONDARY_COLOR" -strokewidth 1 -fill "$SECONDARY_COLOR" \
    -draw "rectangle 20,240 160,270" \
    -fill "white" -pointsize 10 -annotate +30,260 "📄 Pobierz podsumowanie" \
    "$SCREENSHOTS_DIR/podsumowanie-ai.png"

# 9. YouTube Integration (300x200)
echo "🌐 Tworzę youtube-integration.png..."
magick -size 300x200 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +15+25 "🌐 YouTube Integration" \
    -fill "$MAIN_COLOR" -pointsize 10 -annotate +15+50 "Wklej URL YouTube:" \
    -stroke "$DARK_COLOR" -strokewidth 1 -fill "white" \
    -draw "rectangle 15,60 285,90" \
    -fill "gray" -pointsize 9 -annotate +20,80 "https://youtube.com/watch?v=..." \
    -fill "$SECONDARY_COLOR" -pointsize 9 -annotate +15+115 "✅ Pomyślnie pobrano audio z YouTube!" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +15+135 "Tytuł: Przykładowy film" \
    -fill "$DARK_COLOR" -pointsize 8 -annotate +15+150 "Czas: 05:32" \
    -stroke "$MAIN_COLOR" -strokewidth 1 -fill "$MAIN_COLOR" \
    -draw "rectangle 15,165 100,185" \
    -fill "white" -pointsize 8 -annotate +20,180 "🚀 Transkrybuj" \
    "$SCREENSHOTS_DIR/youtube-integration.png"

# 10. System Diagnostics (300x200)
echo "🔧 Tworzę system-diagnostics.png..."
magick -size 300x200 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +15+25 "🔧 Diagnostyka systemu" \
    -fill "$SECONDARY_COLOR" -pointsize 9 -annotate +15+50 "✅ FFmpeg: v6.0 (dostępny)" \
    -fill "$SECONDARY_COLOR" -pointsize 9 -annotate +15+70 "✅ FFprobe: v6.0 (dostępny)" \
    -fill "$SECONDARY_COLOR" -pointsize 9 -annotate +15+90 "✅ OpenAI API: Skonfigurowane" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+110 "🖥️ System: macOS 15.0" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+130 "🐍 Python: 3.11.11" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+150 "📦 Streamlit: 1.45.1" \
    -fill "$MAIN_COLOR" -pointsize 9 -annotate +15+175 "Status: Wszystko działa poprawnie!" \
    "$SCREENSHOTS_DIR/system-diagnostics.png"

# 11. Progress Tracking (300x200)
echo "📊 Tworzę progress-tracking.png..."
magick -size 300x200 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +15+25 "📊 Śledzenie postępu" \
    -fill "$MAIN_COLOR" -pointsize 10 -annotate +15+50 "Transkrypcja w toku..." \
    -stroke "$DARK_COLOR" -strokewidth 1 -fill "$LIGHT_COLOR" \
    -draw "rectangle 15,65 285,85" \
    -fill "$SECONDARY_COLOR" \
    -draw "rectangle 15,65 185,85" \
    -fill "white" -pointsize 8 -annotate +20,80 "Fragment 2/3 (67%)" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+105 "⏱️ Czas trwania: 00:02:15" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+125 "📂 Fragment: audio_chunk_2.wav" \
    -fill "$DARK_COLOR" -pointsize 9 -annotate +15+145 "🤖 Przetwarzanie przez OpenAI..." \
    -fill "$ACCENT_COLOR" -pointsize 8 -annotate +15+170 "🔄 Oszacowany czas: 30 sekund" \
    "$SCREENSHOTS_DIR/progress-tracking.png"

# 12. Zakładka O aplikacji (800x600)
echo "ℹ️ Tworzę o-aplikacji.png..."
magick -size 800x600 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 20 -annotate +50+50 "ℹ️ O aplikacji Audio2Tekst" \
    -fill "$MAIN_COLOR" -pointsize 16 -annotate +50+100 "🚀 WERSJA 2.3.0 - CROSS-PLATFORM EDITION" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+140 "Zaawansowana aplikacja do transkrypcji audio i video na tekst" \
    -fill "$DARK_COLOR" -pointsize 14 -annotate +50+180 "🌟 Główne funkcje:" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+210 "• Transkrypcja plików lokalnych (MP3, WAV, M4A, FLAC)" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+235 "• Pobieranie i transkrypcja z YouTube" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+260 "• Podsumowania AI za pomocą OpenAI GPT" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+285 "• Cross-platform: Windows, macOS, Linux" \
    -fill "$DARK_COLOR" -pointsize 14 -annotate +50+325 "🔧 Technologie:" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+355 "Python 3.11+ • Streamlit • OpenAI API • FFmpeg" \
    -fill "$DARK_COLOR" -pointsize 14 -annotate +50+395 "📊 Wydajność:" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+425 "• Precyzja transkrypcji: >95%" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+450 "• Obsługa plików do 25MB" \
    -fill "$DARK_COLOR" -pointsize 11 -annotate +70+475 "• Automatyczne dzielenie na fragmenty" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+520 "👨‍💻 Autor: Alan Steinbarth" \
    -fill "$MAIN_COLOR" -pointsize 10 -annotate +50+545 "📧 alan.steinbarth@gmail.com" \
    -fill "$MAIN_COLOR" -pointsize 10 -annotate +50+565 "🔗 GitHub: https://github.com/AlanSteinbarth" \
    "$SCREENSHOTS_DIR/o-aplikacji.png"

# 13. Zakładka Ustawienia (800x600)
echo "⚙️ Tworzę ustawienia.png..."
magick -size 800x600 xc:"$LIGHT_COLOR" \
    -fill "$DARK_COLOR" -pointsize 20 -annotate +50+50 "⚙️ Ustawienia i diagnostyka" \
    -fill "$MAIN_COLOR" -pointsize 16 -annotate +50+100 "🔧 Informacje o systemie" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+140 "System operacyjny:" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+165 "✅ macOS 15.0 (Sequoia)" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+200 "Środowisko Python:" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+225 "✅ Python 3.11.11" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+250 "✅ Streamlit 1.45.1" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+285 "Narzędzia multimedialne:" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+310 "✅ FFmpeg v6.0 - dostępny" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+335 "✅ FFprobe v6.0 - dostępny" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+370 "Konfiguracja API:" \
    -fill "$SECONDARY_COLOR" -pointsize 11 -annotate +70+395 "✅ OpenAI API Key - skonfigurowany" \
    -fill "$DARK_COLOR" -pointsize 12 -annotate +50+430 "Katalogi robocze:" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +70+455 "📁 uploads/originals/ - pliki źródłowe" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +70+475 "📁 uploads/transcripts/ - transkrypty" \
    -fill "$DARK_COLOR" -pointsize 10 -annotate +70+495 "📁 uploads/summaries/ - podsumowania" \
    -fill "$MAIN_COLOR" -pointsize 14 -annotate +50+530 "Status: System gotowy do pracy!" \
    -stroke "$SECONDARY_COLOR" -strokewidth 2 -fill none \
    -draw "rectangle 45,480 755,575" \
    "$SCREENSHOTS_DIR/ustawienia.png"

echo ""
echo "🎉 SUKCES! Wygenerowano 13 screenshots:"
echo "   📁 Panel wyboru źródła (500x350)"
echo "   🖥️ Główny obszar roboczy (500x350)"
echo "   ⚙️ Proces 1-4: Upload, Analiza, Transkrypcja, Wyniki (200x150)"
echo "   📝 Obszar transkrypcji (500x300)"
echo "   🤖 Podsumowanie AI (500x300)"
echo "   🌐 YouTube Integration (300x200)"
echo "   🔧 System Diagnostics (300x200)"
echo "   📊 Progress Tracking (300x200)"
echo "   ℹ️ Zakładka O aplikacji (800x600)"
echo "   ⚙️ Zakładka Ustawienia (800x600)"
echo ""
echo "📸 Wszystkie pliki zapisane w: $SCREENSHOTS_DIR/"
echo "🚀 Następny krok: Aktualizacja URLs w app.py"
