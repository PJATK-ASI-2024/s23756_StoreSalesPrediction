# Wybierz obraz bazowy
FROM python:3.9-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki projektu
COPY app/ /app
COPY requirements.txt /app/requirements.txt

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Uruchom aplikację
CMD ["python", "main.py"]
