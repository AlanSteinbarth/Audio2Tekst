# 🐳 Audio2Tekst Docker Guide

## Szybkie uruchomienie

### Wymagania
- Docker 20.10+
- Docker Compose 2.0+
- Klucz OpenAI API

### 1. Przygotowanie środowiska

```bash
# Klonuj repozytorium
git clone https://github.com/AlanSteinbarth/Audio2Tekst.git
cd Audio2Tekst

# Skopiuj i skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj swój OPENAI_API_KEY
```

### 2. Uruchomienie (Development)

```bash
# Zbuduj i uruchom
docker-compose up --build

# W tle
docker-compose up -d --build
```

### 3. Uruchomienie (Production)

```bash
# Produkcyjne ustawienia z optymalizacjami
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Zarządzanie

### Podstawowe komendy

```bash
# Status kontenerów
docker-compose ps

# Logi aplikacji
docker-compose logs -f

# Restart aplikacji
docker-compose restart

# Zatrzymanie
docker-compose down

# Usunięcie z wolumenami
docker-compose down -v
```

### Monitoring

```bash
# Zużycie zasobów
docker stats audio2tekst-app

# Health check
docker inspect --format='{{.State.Health.Status}}' audio2tekst-app

# Sprawdź porty
docker port audio2tekst-app
```

## Konfiguracja

### Zmienne środowiskowe

| Zmienna | Opis | Domyślna wartość |
|---------|------|------------------|
| `OPENAI_API_KEY` | Klucz API OpenAI (wymagany) | - |
| `MAX_FILE_SIZE` | Maksymalny rozmiar pliku (MB) | 25 |
| `CHUNK_DURATION` | Długość segmentu (minuty) | 5 |
| `DEFAULT_LANGUAGE` | Język transkrypcji | pl |
| `LOG_LEVEL` | Poziom logowania | INFO |

### Wolumeny

- `audio2tekst_uploads`: Przesłane pliki i wyniki
- `audio2tekst_logs`: Logi aplikacji
- `audio2tekst_db`: Baza danych (przyszłe użycie)

### Porty

- `8501`: Interfejs webowy Streamlit

## Rozwiązywanie problemów

### Błędy Docker

```bash
# Sprawdź status kontenera
docker-compose ps

# Sprawdź logi błędów
docker-compose logs audio2tekst

# Restart z pełną rekompilacją
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problemy z wolumenami

```bash
# Sprawdź uprawnienia
ls -la docker-volumes/

# Napraw uprawnienia (jeśli potrzeba)
sudo chown -R $USER:$USER docker-volumes/
```

### Performance Issues

```bash
# Sprawdź zużycie zasobów
docker stats

# Zwiększ limity w docker-compose.yml
# deploy.resources.limits.memory: "8G"
# deploy.resources.limits.cpus: "4.0"
```

## Security

### Best Practices

1. **Nigdy nie commituj .env z prawdziwymi kluczami**
2. **Używaj secrets w produkcji**
3. **Regularne aktualizacje obrazu bazowego**
4. **Monitoring logów bezpieczeństwa**

### Produkcyjna konfiguracja

```bash
# Użyj Docker secrets dla API keys
echo "your_openai_api_key" | docker secret create openai_api_key -

# Uruchom z ograniczonymi uprawnieniami
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Updates

### Aktualizacja aplikacji

```bash
# Pull najnowsze zmiany
git pull origin main

# Rebuild i restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup danych

```bash
# Backup wolumenów
docker run --rm -v audio2tekst_uploads:/source -v $(pwd)/backup:/backup alpine \
  tar czf /backup/uploads-$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
```
