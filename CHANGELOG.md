# 📝 Changelog

> **Wszystkie istotne zmiany w projekcie Audio2Tekst będą dokumentowane w tym pliku.**

Projekt przestrzega zasad [Semantic Versioning](https://semver.org/).

## [Unreleased]

### 🔄 W trakcie
- Refaktoryzacja kodu na moduły
- Dodanie opcji konfiguracji języka w UI
- Implementacja systemu powiadomień

---

## [2.4.0] - 2025-01-26

### ✨ Dodano
- **Inteligentna konwersja audio** - automatyczne przekształcanie plików video (MP4, WEBM, MOV, AVI) do formatu MP3 podczas pobierania
- **Ulepszony layout UI** - przycisk pobierania audio przeniesiony bezpośrednio pod odtwarzacz dla lepszego UX
- **Automatyczna detekcja formatu** - aplikacja rozpoznaje czy plik to audio czy video i odpowiednio dostosowuje opcje pobierania
- **Session state dla YouTube** - zapobiega wielokrotnemu pobieraniu tego samego video z YouTube
- **Ulepszone zarządzanie stanem** - lepsze cachowanie wyników dla poprawy wydajności

### 🔧 Zmieniono
- **Pozycja przycisku pobierania** - przycisk "Pobierz audio" teraz znajduje się bezpośrednio pod odtwarzaczem zamiast po sekcji transkrypcji
- **Logika pobierania audio** - dla plików video pokazuje "Pobierz audio (MP3)", dla plików audio "Pobierz audio"
- **Obsługa sesji YouTube** - lepsze zarządzanie stanem pobierania z YouTube, eliminuje dublowanie procesów
- **Komunikaty użytkownika** - bardziej precyzyjne informacje o dostępnych formatach do pobrania

### 🛠️ Poprawiono
- **User Experience** - intuicyjniejsze umieszczenie kontrolek w interfejsie
- **Wydajność konwersji** - optymalizacja procesu konwersji video do MP3
- **Stabilność YouTube** - lepsze zarządzanie sesją przy pobieraniu z YouTube
- **Error handling** - ulepszona obsługa błędów podczas konwersji formatów

### 📦 Zmiany techniczne
- Dodana logika wykrywania formatu pliku (audio vs video)
- Implementacja automatycznej konwersji z FFmpeg
- Ulepszone zarządzanie session state w Streamlit
- Optymalizacja kodu do obsługi różnych formatów plików

---

## [1.2.0] - 2025-06-04

### ✨ Dodano
- **Dokumentacja długich audio** - rozszerzona sekcja "System Information" o wyjaśnienie przetwarzania długich plików audio
- **Automatyczne dzielenie długich audio** - szczegółowe informacje o chunking'u plików >25MB z overlappingiem
- **Inteligentne łączenie tekstu** - opis procesu scalania fragmentów transkrypcji w spójny tekst
- **Ulepszona dokumentacja użytkownika** - kompletne wyjaśnienie funkcjonalności w interfejsie aplikacji

### 🔧 Zmieniono
- **Sekcja informacji systemowych** - dodano szczegółowy opis przetwarzania długich tekstów (>8000 znaków)
- **README.md** - zaktualizowano o trzy nowe bullet points opisujące możliwości aplikacji
- **Interface użytkownika** - lepsze informowanie o funkcjonalnościach long audio processing

### 📝 Dokumentacja
- **CHANGELOG.md** - dodano dokumentację nowych funkcjonalności
- **README.md** - rozszerzono opis o możliwości automatycznego dzielenia długich plików
- **System Information** - dodano wyjaśnienie hierarchicznego podsumowywania

---

## [2.3.0] - 2025-05-29

### ✨ Dodano
- **Uniwersalna kompatybilność** - pełna obsługa Windows, macOS i Linux
- **Automatyczne wykrywanie platformy** - inteligentne dostosowanie do systemu operacyjnego
- **Sprawdzanie zależności** - automatyczna weryfikacja dostępności FFmpeg/FFprobe
- **Panel informacji o systemie** - wyświetlanie szczegółów platformy i zależności
- **Bezpieczne ścieżki plików** - prawidłowa obsługa ścieżek na wszystkich systemach
- **Ulepszone kodowanie** - odpowiednie kodowanie plików tekstowych (UTF-8/UTF-8-sig)
- **Timeout i error handling** - lepsze zarządzanie błędami i timeoutami
- **Inteligentne dzielenie długich tekstów** - automatyczny podział tekstów >8000 znaków
- **Hierarchiczne podsumowywanie** - fragmenty→podsumowania→finalne podsumowanie
- **Obsługa ograniczeń OpenAI** - rozwiązanie problemów z długością promptu
- **Rozbudowane logowanie błędów** - szczegółowe logi w `logs/summary_errors.log`
- **Ulepszone komunikaty UI** - spinnery i informacje o długich operacjach
- **Threading dla UX** - asynchroniczne komunikaty o długotrwałych procesach

### 🔧 Zmieniono
- **Komendy systemowe** - używanie pełnych ścieżek do FFmpeg/FFprobe
- **Obsługa plików tymczasowych** - bezpieczniejsze tworzenie i usuwanie
- **YouTube download** - stabilniejsze pobieranie z różnymi konfiguracjami systemów
- **Transkrypcja** - ulepszona obsługa błędów podczas przetwarzania
- **Funkcja summarize()** - przepisana z obsługą długich tekstów
- **Komunikaty użytkownika** - bardziej opisowe i informacyjne
- **Struktura logów** - automatyczne tworzenie folderów i timestampy

### 🛠️ Poprawiono
- Kompatybilność między różnymi systemami operacyjnymi
- Stabilność na macOS (Homebrew, system paths)
- Obsługa Windows (ścieżki z .exe, kodowanie)
- Reliability na Linux (snap packages, różne dystrybucje)
- **Problem z długimi tekstami** - eliminacja błędów przekroczenia limitu tokenów
- **UX podczas długich operacji** - lepsze informowanie użytkownika
- **Obsługa błędów podsumowania** - szczegółowe logowanie i recovery

### 📦 Zmiany techniczne
- Aktualizacja wersji do 2.3.0 Cross-Platform Edition
- Dodane funkcje pomocnicze dla kompatybilności systemów
- Improved logging i error reporting
- Enhanced file handling dla różnych platform

---

## [2.2.0] - 2025-01-25

### ✨ Dodano
- **Finalna wersja enterprise** - kompletna infrastruktura enterprise-level
- **Kolejna poprawiona wersja** - pełna profesjonalna struktura projektu
- **Enhanced documentation** - rozszerzona dokumentacja z dodatkowymi szczegółami

### 🛠️ Poprawiono
- Finalizacja wszystkich komponentów enterprise
- Optymalizacja struktury plików i konfiguracji
- Udoskonalenie opisów i komentarzy w kodzie

### 📦 Zmiany techniczne
- Aktualizacja wersji do 2.2.0 Enterprise Edition Enhanced
- Finalne dostrojenie CI/CD pipeline
- Kompletne testing coverage

---

## [2.1.0] - 2025-01-25

### ✨ Dodano
- **Enterprise-level dokumentacja** - kompletna dokumentacja projektu
- **CI/CD Pipeline** - automatyczne testowanie i deployement
- **Security scanning** - bandit, safety, semgrep, dependency review
- **GitHub Templates** - templates dla issues i pull requests
- **Comprehensive testing** - unit tests, performance tests, integration tests
- **Professional project structure** - db/, logs/, tests/, .github/
- **Environment configuration** - szczegółowy .env.example z wszystkimi opcjami
- **Code quality tools** - flake8, black, isort, mypy, pre-commit hooks
- **Community guidelines** - CODE_OF_CONDUCT.md, CONTRIBUTING.md

### 🔧 Zmieniono
- **Requirements structure** - podział na production/development dependencies
- **Enhanced .gitignore** - kompletne reguły dla Python/Streamlit
- **Professional README** - badges, installation guide, architecture diagram
- **Semantic versioning** - proper changelog format with categories

### 🐛 Naprawiono
- **Function parameters** - dodano brakujący `_client` parameter do `transcribe_chunks()` i `summarize()`
- **Import statements** - uporządkowanie importów w app.py
- **Error handling** - lepsza obsługa błędów OpenAI API

### 🔒 Bezpieczeństwo
- **Security policies** - SECURITY.md z procedurami zgłaszania
- **Secrets management** - proper .env handling
- **Dependencies scanning** - automated vulnerability checks

### 📚 Dokumentacja
- **API documentation** - detailed function documentation
- **Installation guide** - step-by-step setup instructions
- **Usage examples** - comprehensive usage documentation
- **Contributing guide** - guidelines for contributors

---

## [2.0.0] - 2025-01-25

### 💥 Breaking Changes
- **Code structure** - major refactoring for maintainability
- **Function signatures** - added client parameter to cached functions
- **Environment variables** - standardized configuration approach

### ✨ Dodano
- **Professional project structure** - enterprise-level organization
- **Automated workflows** - CI/CD with GitHub Actions
- **Quality assurance** - comprehensive testing suite
- **Security measures** - multi-layer security scanning
- **Documentation overhaul** - professional documentation suite

### 🔧 Zmieniono
- **Dependency management** - proper requirements structure
- **Configuration system** - environment-based configuration
- **Error handling** - improved error messages and handling

### 🗑️ Usunięto
- **Legacy code patterns** - removed deprecated functionality
- **Redundant dependencies** - cleaned up requirements

---

## [1.0.0] - 2025-05-23

### ✨ Dodano
- **Podstawowa funkcjonalność transkrypcji** plików audio/video
- **Wsparcie dla YouTube** - bezpośrednia transkrypcja filmów
- **Automatyczne podsumowanie** - generowanie tematu i podsumowania
- **Interfejs Streamlit** - intuicyjny web interface
- **Obsługa formatów** - MP3, WAV, M4A, MP4, MOV, AVI, WEBM
- **Eksport funkcjonalność** - pobieranie transkrypcji i podsumowań

### 🔧 Techniczne
- **OpenAI Whisper API** - integracja do transkrypcji
- **GPT-3.5 integration** - automatyczne podsumowania
- **File chunking** - obsługa dużych plików przez podział
- **Caching system** - optymalizacja wydajności
- **Secure file handling** - bezpieczna obsługa plików
- **Logging system** - rejestrowanie operacji

### 📋 Formaty plików
- **Audio**: MP3, WAV, M4A
- **Video**: MP4, MOV, AVI, WEBM  
- **Źródła**: Pliki lokalne, YouTube URLs

---

## 📖 Legenda

- 💥 **Breaking Changes** - zmiany niekompatybilne wstecz
- ✨ **Added** - nowe funkcjonalności
- 🔧 **Changed** - zmiany w istniejących funkcjonalnościach
- 🗑️ **Removed** - usunięte funkcjonalności
- 🐛 **Fixed** - naprawione błędy
- 🔒 **Security** - poprawki bezpieczeństwa
- 📚 **Documentation** - zmiany w dokumentacji
- 🔄 **Work in Progress** - funkcjonalności w trakcie

---

## 🔗 Linki

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

*Projekt: Audio2Tekst*  
*Autor: [Alan Steinbarth](mailto:alan.steinbarth@gmail.com)*  
*GitHub: [@AlanSteinbarth](https://github.com/AlanSteinbarth)*
