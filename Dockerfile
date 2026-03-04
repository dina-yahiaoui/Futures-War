FROM python:3.10-slim

# Dossier de travail dans le container
WORKDIR /app

# Copie les dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code backend
COPY backend/ ./backend

# On se place dans le dossier backend
WORKDIR /app/backend

# On expose le port utilisé par Flask
EXPOSE 8000

# 👉 Commande qui lance réellement Flask dans le container
CMD ["python", "app.py"]