FROM python:3.10-slim

WORKDIR /app

# Installer git + ffmpeg (whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Copier requirements à la racine
COPY requirements.txt .

# Installer dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier backend
COPY backend/ ./backend

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]