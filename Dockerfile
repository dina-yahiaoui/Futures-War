FROM python:3.10-slim

# Dossier de travail dans le container
WORKDIR /app

# On copie les dépendances (requirements à la racine)
COPY requirements.txt .

# On installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# On copie le code backend dans /app/backend
COPY backend/ ./backend

# On se place dans le backend
WORKDIR /app/backend

# On expose le port Flask
EXPOSE 8000

# Commande de lancement
CMD ["python", "app.py"]