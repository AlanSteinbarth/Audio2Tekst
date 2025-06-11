# Współpraca przy projekcie Audio2Tekst

**Autor:** Alan Steinbarth (alan.steinbarth@gmail.com)  
**GitHub:** https://github.com/AlanSteinbarth  
**Projekt:** Audio2Tekst - Cross-Platform Transcription Tool

Dziękujemy za zainteresowanie współpracą przy projekcie! Ten dokument zawiera wszystkie informacje potrzebne do efektywnego współtworzenia projektu Audio2Tekst.

## 📋 Spis treści

- [Zgłaszanie błędów](#zgłaszanie-błędów)
- [Propozycje funkcji](#propozycje-funkcji)
- [Środowisko deweloperskie](#środowisko-deweloperskie)
- [Standardy kodu](#standardy-kodu)
- [Proces Pull Request](#proces-pull-request)
- [Testowanie](#testowanie)
- [Cross-Platform Development](#cross-platform-development)
- [Komunikacja](#komunikacja)

## 🐛 Zgłaszanie błędów

Przed zgłoszeniem błędu:

1. **Sprawdź istniejące Issues** - może błąd został już zgłoszony
2. **Sprawdź FAQ** w README.md - może istnieje znane rozwiązanie
3. **Przetestuj na różnych plikach** - upewnij się, że błąd jest reprodukowalny

### Format zgłoszenia błędu:

```markdown
**Opis błędu:**
Krótki, jasny opis problemu.

**Kroki do odtworzenia:**
1. Uruchom aplikację
2. Wczytaj plik [typ pliku]
3. Kliknij "Transkrybuj"
4. Błąd pojawia się w kroku...

**Oczekiwane zachowanie:**
Co powinno się stać?

**Faktyczne zachowanie:**
Co się faktycznie stało?

**Środowisko:**
- OS: [Windows 11 / macOS 14.0 / Ubuntu 22.04]
- Python: [wersja]
- FFmpeg: [wersja lub "nie zainstalowane"]
- Przeglądarka: [Chrome, Firefox, Safari]

**Dodatkowe informacje:**
- Logi z terminala
- Zrzuty ekranu
- Rozmiar i format pliku audio
```

## 💡 Propozycje funkcji

Chcesz zaproponować nową funkcję? Świetnie!

1. **Sprawdź roadmap** - może funkcja jest już planowana
2. **Otwórz Discussion** przed Issue - przedyskutuj pomysł
3. **Opisz use case** - dlaczego ta funkcja jest potrzebna?

### Template propozycji:

```markdown
**Problem do rozwiązania:**
Jaki problem ma rozwiązać ta funkcja?

**Proponowane rozwiązanie:**
Jak powinno to działać?

**Alternatywy:**
Czy rozważałeś inne podejścia?

**Dodatkowy kontekst:**
Mockupy, diagramy, przykłady użycia
```

## 🛠️ Środowisko deweloperskie

### Wymagania:
- Python 3.8+
- FFmpeg (system audio/video processing)
- Git
- IDE/Editor z wsparciem dla Python (VS Code, PyCharm)

### Setup krok po kroku:

```bash
# 1. Fork i klonowanie
git clone https://github.com/TwojNick/Audio2Tekst.git
cd Audio2Tekst

# 2. Środowisko wirtualne
python3 -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Zależności deweloperskie
pip install -r requirements-dev.txt
pip install -r requirements.txt

# 4. Pre-commit hooks (opcjonalne ale zalecane)
pre-commit install

# 5. Zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj OpenAI API key

# 6. Test instalacji
streamlit run app.py
```

### Narzędzia deweloperskie:

```bash
# Formatowanie kodu
black app.py
isort app.py

# Linting
flake8 app.py
pylint app.py

# Bezpieczeństwo
bandit -r app.py

# Testy
pytest tests/ -v
pytest --cov=app tests/
```

## Pytania

Jeśli masz pytania dotyczące projektu, możesz:
- Otworzyć Issue z tagiem "question"
- Wysłać email na adres alan.steinbarth@gmail.com

## 📝 Standardy kodu

### Python Code Style:
- **PEP 8** - oficjalny style guide dla Python
- **Line length:** maksymalnie 88 znaków (black formatter)
- **Import organization:** używaj `isort` do sortowania importów
- **Docstrings:** Google Style dla wszystkich funkcji publicznych

### Przykład dobrego docstring:
```python
def transcribe_audio(file_path: Path, client) -> str:
    """
    Transkrybuje plik audio używając OpenAI Whisper API.
    
    Args:
        file_path (Path): Ścieżka do pliku audio
        client: Klient OpenAI API
    
    Returns:
        str: Transkrypcja tekstu z pliku audio
    
    Raises:
        RuntimeError: Gdy plik nie może być przetworzony
        OpenAIError: Gdy API zwróci błąd
    """
```

### Konwencje nazewnictwa:
- **Funkcje i zmienne:** `snake_case`
- **Klasy:** `PascalCase` 
- **Stałe:** `UPPER_SNAKE_CASE`
- **Pliki prywatne:** `_private_function()`

### Obsługa błędów:
```python
# ✅ Dobrze - specific exceptions
try:
    result = openai_api_call()
except openai.OpenAIError as e:
    logger.error("OpenAI API error: %s", e)
    raise RuntimeError(f"Transcription failed: {e}") from e

# ❌ Źle - zbyt ogólne
try:
    result = openai_api_call()
except Exception as e:
    print("Something went wrong")
```

## 🔄 Proces Pull Request

### Przed utworzeniem PR:

1. **Synchronizuj z main:**
```bash
git checkout main
git pull upstream main
git checkout twoj-branch
git rebase main
```

2. **Uruchom testy:**
```bash
pytest tests/ -v
flake8 app.py
black --check app.py
```

3. **Przetestuj na różnych platformach** (jeśli możliwe):
   - Windows, macOS, Linux
   - Różne formaty plików audio/video
   - Różne rozmiary plików

### Struktura commita:

Używamy [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Nowe funkcje
git commit -m "feat: add YouTube playlist support"

# Poprawki błędów  
git commit -m "fix: resolve FFmpeg path detection on Windows"

# Dokumentacja
git commit -m "docs: update installation guide for Linux"

# Refaktoryzacja
git commit -m "refactor: extract audio processing to separate module"

# Testy
git commit -m "test: add unit tests for summarization function"

# Wydajność
git commit -m "perf: optimize chunking algorithm for large files"
```

### Checklist PR:

- [ ] Kod jest sformatowany (black, isort)
- [ ] Brak błędów lintingu (flake8, pylint)
- [ ] Testy przechodzą (pytest)
- [ ] Dodano testy dla nowych funkcji
- [ ] Dokumentacja jest zaktualizowana
- [ ] Przetestowano na docelowych platformach
- [ ] Commit messages są zgodne z konwencją
- [ ] PR ma jasny opis i screenshots (jeśli UI)

## 🧪 Testowanie

### Uruchamianie testów:

```bash
# Wszystkie testy
pytest

# Konkretny test
pytest tests/test_app.py::TestAudioProcessing::test_split_audio

# Z coverage
pytest --cov=app --cov-report=html tests/

# Testy wydajności
pytest tests/test_performance.py -v
```

### Typy testów:

1. **Unit Tests** - testują pojedyncze funkcje
2. **Integration Tests** - testują współpracę komponentów  
3. **End-to-End Tests** - testują cały workflow
4. **Performance Tests** - sprawdzają wydajność

### Struktura testów:
```python
def test_function_name():
    # Arrange - przygotuj dane
    test_data = "sample audio content"
    
    # Act - wykonaj akcję
    result = function_under_test(test_data)
    
    # Assert - sprawdź wynik
    assert result == expected_result
    assert len(result) > 0
```

### Testowanie cross-platform:

Jeśli modyfikujesz kod związany z:
- Ścieżkami plików → testuj na Windows i Unix
- Kodowaniem tekstu → testuj polskie znaki  
- Subprocess calls → testuj różne shelle
- FFmpeg integration → testuj różne instalacje

## 🌍 Cross-Platform Development

### Zasady kompatybilności:

1. **Ścieżki plików:**
```python
# ✅ Dobrze
from pathlib import Path
path = Path("uploads") / "audio.mp3"

# ❌ Źle  
path = "uploads/audio.mp3"  # Nie działa na Windows
```

2. **Subprocess calls:**
```python
# ✅ Dobrze - sprawdź dostępność narzędzia
ffmpeg_path = find_executable("ffmpeg")
subprocess.run([ffmpeg_path, "-i", input_file])

# ❌ Źle - zakładanie lokalizacji
subprocess.run(["ffmpeg", "-i", input_file])
```

3. **Kodowanie plików:**
```python
# ✅ Dobrze - użyj helper function
encoding = get_safe_encoding()  # UTF-8 lub UTF-8-sig
with open(file_path, 'w', encoding=encoding) as f:
    f.write(text)
```

### Testowanie platform:

- **Windows:** Testuj na Windows 10/11
- **macOS:** Testuj na Intel i Apple Silicon  
- **Linux:** Testuj na Ubuntu/Debian (głównie)
- **FFmpeg:** Różne sposoby instalacji per platform

## 📞 Komunikacja

### Kanały komunikacji:

1. **GitHub Issues** - błędy, propozycje funkcji
2. **GitHub Discussions** - ogólne pytania, pomysły
3. **Email** - alan.steinbarth@gmail.com (dla poważnych problemów)
4. **Pull Request Comments** - dyskusja o kodzie

### Response time:

- **Issues:** odpowiedź w ciągu 48h
- **Pull Requests:** review w ciągu 1 tygodnia
- **Critical bugs:** odpowiedź tego samego dnia

### Język komunikacji:

- **Polski** - preferowany dla Issues i PR
- **English** - także akceptowany
- **Code comments** - angielski (dla międzynarodowych deweloperów)

## 🎯 Priority Areas

Obszary gdzie szczególnie potrzebujemy pomocy:

### 🔥 High Priority:
- Wsparcie dla więcej języków transkrypcji
- Optymalizacja wydajności dla dużych plików
- Lepsza obsługa błędów YouTube
- Mobile-responsive UI

### 📈 Medium Priority:  
- Batch processing (wiele plików naraz)
- Plugin system dla custom processors
- Real-time transcription
- Cloud storage integration

### 💡 Nice to Have:
- Dark mode UI
- Keyboard shortcuts
- Export do więcej formatów
- AI voice detection/separation

## 🏆 Recognition

Wszyscy kontrybutorzy będą:
- Wymienieni w README.md
- Dodani do contributors na GitHub
- Otrzymają mentions w release notes

### Hall of Fame:
Znaczące wkłady mogą otrzymać:
- Specjalne badges w profilu
- Maintainer rights (po dłuższej współpracy)
- Co-author status w publikacjach

---

## 📚 Przydatne linki

- [Python PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

**Dziękujemy za chęć współpracy! Każdy wkład, bez względu na rozmiar, jest doceniany.** 🙏

**Happy coding!** 🚀
