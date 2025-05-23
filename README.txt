# Audio2Tekst

Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
GitHub: https://github.com/AlanSteinbarth

Aplikacja webowa stworzona przy użyciu Streamlit, która umożliwia:
- Transkrypcję plików audio i video na tekst
- Transkrypcję audio z filmów z YouTube
- Automatyczne podsumowanie transkrypcji
- Eksport transkrypcji i podsumowań do plików tekstowych

## Funkcje

- Obsługa wielu formatów audio/video (.mp3, .wav, .m4a, .mp4, .mov, .avi, .webm)
- Pobieranie i przetwarzanie audio z YouTube
- Automatyczna transkrypcja z wykorzystaniem OpenAI Whisper
- Generowanie podsumowań przy użyciu GPT-3.5
- Interfejs użytkownika przyjazny dla użytkownika
- Możliwość edycji transkrypcji przed podsumowaniem
- Eksport wyników do plików tekstowych

## Wymagania

- Python 3.10.12 lub nowszy
- Klucz API OpenAI
- ffmpeg (do przetwarzania plików audio/video)
- Pozostałe zależności znajdują się w pliku requirements.txt

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Upewnij się, że masz zainstalowany ffmpeg w systemie.

## Uruchomienie

```bash
streamlit run app.py
```

Po uruchomieniu, aplikacja będzie dostępna w przeglądarce pod adresem `http://localhost:8501`

## Autor

Alan Steinbarth
- GitHub: https://github.com/AlanSteinbarth
- Email: alan.steinbarth@gmail.com

## Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) aby uzyskać więcej informacji.
