# 🌆 Futures War - Backend API

> Application pour imaginer le futur de Marseille grâce à l'IA

**Challenge B2 - La Plateforme - Mars 2026**

---

## 📋 C'est quoi ce projet ?

Une API qui permet de :
1. 🎤 **Parler** → L'IA transcrit ta voix en texte
2. 🎨 **Générer** → L'IA crée une image du futur de Marseille
3. 📊 **Partager** → Les citoyens votent pour leurs futurs préférés

---

## ⚡ Installation rapide

### 1. Installer Python et ffmpeg

**Python 3.11+** : [Télécharger ici](https://www.python.org/downloads/)

**ffmpeg** (nécessaire pour Whisper) :
- **Windows** : [Télécharger](https://github.com/BtbN/FFmpeg-Builds/releases) → Extraire dans `C:\ffmpeg` → Ajouter `C:\ffmpeg\bin` au PATH
- **Mac** : `brew install ffmpeg`
- **Linux** : `sudo apt install ffmpeg`

---

### 2. Cloner le projet
```bash
git clone https://github.com/dina-yahiaoui/Futures-War.git
cd Futures-War/backend
```

---

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

⏱️ **Temps d'installation : 5-10 minutes**

---

### 4. Configurer le token

Créer un fichier `.env` dans `backend/` :
```bash
API_BEARER_TOKEN= Votre token ici 
WHISPER_MODEL_SIZE=base
```

---

### 5. Lancer le serveur
```bash
python app.py
```

✅ **L'API tourne sur** : `http://localhost:8000`

📖 **Documentation** : `http://localhost:8000/docs`

---

## 🎯 Comment ça marche ?

### Le pipeline complet
```
Utilisateur parle
      ↓
Audio → Whisper → Texte
      ↓
Texte → Optimisation → Prompt enrichi
      ↓
Prompt → Serveur GPU → Image IA
      ↓
Image affichée
```

---

## 🔌 Les 3 routes principales

### 1. Speech-to-Text (Audio → Texte)

**Route :** `POST /api/speech-to-text`

**Exemple :**
```bash
curl -X POST "http://localhost:8000/api/speech-to-text" \
  -H "Authorization: xxxxxxxxx" \
  -F "file=@mon_audio.m4a"
```

**Réponse :**
```json
{
  "text": "Marseille avec des arbres partout"
}
```

---

### 2. Prompt-to-Image (Texte → Image)

**Route :** `POST /api/prompt-to-image`

**Exemple :**
```bash
curl -X POST "http://localhost:8000/api/prompt-to-image" \
  -H "Authorization: xxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Marseille avec des arbres", "width": 512, "height": 512}'
```

**Réponse :**
```json
{
  "images": ["iVBORw0KGgo..."],
  "model": "Tongyi-MAI/Z-Image-Turbo"
}
```

L'image est en **base64**, à décoder pour l'afficher.

---

### 3. System Stats (Infos système)

**Route :** `GET /api/system-stats`

**Exemple :**
```bash
curl -X GET "http://localhost:8000/api/system-stats" \
  -H "Authorization: Bearer xxxxxxxxx"
```

**Réponse :** CPU, RAM, GPU, modèles chargés, etc.

---

## 🧪 Tester l'API

### Option 1 : Swagger (recommandé)

1. Lancer le serveur : `python app.py`
2. Ouvrir : `http://localhost:8000/docs`
3. Cliquer sur **Authorize** 🔒
4. Entrer le token : `xxxxxxxxx`
5. Tester les routes directement dans le navigateur !

---

### Option 2 : Scripts Python de test
```bash
# Test Whisper
python test_whisper.py

# Test optimisation de prompts
python test_prompt.py

# Test connexion GPU
python test_gpu_connection.py
```

---

## 📂 Structure du projet
```
backend/
├── app.py                  # API principale (FastAPI)
├── whisper_utils.py        # Service Whisper (audio → texte)
├── prompt_utils.py         # Optimisation des prompts
├── gpu_client.py           # Client serveur GPU (génération images)
├── requirements.txt        # Dépendances Python
├── .env                    # Configuration (TOKEN, etc.)
└── test_*.py              # Scripts de test
```

---

## 🔐 Authentification

**Toutes les routes nécessitent un Bearer Token.**

**Header à ajouter dans chaque requête :**
```
Authorization: xxxxxxxxx
```

**Sans ce header → Erreur 401 (Unauthorized)**

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|-------------|------|
| **FastAPI** | Framework API Python |
| **Whisper** | Transcription audio (OpenAI) |
| **PyTorch** | Deep Learning |
| **Z-Image** | Génération d'images (Tongyi-MAI) |
| **Pillow** | Manipulation d'images |
| **psutil** | Monitoring système |

---

## 🎨 Exemple complet (Python)
```python
import requests
import base64
from PIL import Image
from io import BytesIO

# Configuration
API_URL = "http://localhost:8000"
TOKEN = "xxxxxxxxx"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 1. Transcrire un audio
with open("audio.m4a", "rb") as f:
    response = requests.post(
        f"{API_URL}/api/speech-to-text",
        headers=HEADERS,
        files={"file": f}
    )
    texte = response.json()["text"]
    print(f"Texte: {texte}")

# 2. Générer une image
response = requests.post(
    f"{API_URL}/api/prompt-to-image",
    headers=HEADERS,
    json={"prompt": texte, "width": 512, "height": 512}
)
image_b64 = response.json()["images"][0]

# 3. Sauvegarder l'image
image_data = base64.b64decode(image_b64)
image = Image.open(BytesIO(image_data))
image.save("resultat.png")
image.show()
print("✅ Image sauvegardée !")
```

---

## ❓ FAQ

### Le serveur ne démarre pas

**Erreur "ffmpeg not found"** :
- Vérifier que ffmpeg est installé : `ffmpeg -version`
- Ajouter `C:\ffmpeg\bin` au PATH (Windows)
- Redémarrer le terminal

**Erreur "Port 8000 already in use"** :
- Un autre programme utilise le port 8000
- Arrêter l'autre programme ou changer le port dans `app.py`

---

### L'API retourne 401 (Unauthorized)

- Vérifier que le token est correct dans `.env`
- Vérifier que le header `Authorization` est bien envoyé
- Format : `Authorization: Bearer votre-token`

---

### La génération d'image timeout

- Le serveur GPU distant (`GROSGPU:8000`) est peut-être éteint
- Contacter le responsable du serveur GPU
- En attendant, l'API retournera une image placeholder

---

## 👥 Équipe

- **Pierre** - Backend & API
- **[Nom]** - Frontend
- **[Nom]** - Prompts & Optimisation
- **[Nom]** - Container & Déploiement

**Product Owner :** SuperMan  
**Email :** SuperMan@laplateforme.io

---

## 📄 Licence

Projet académique - La Plateforme (2026)

---

## 🙏 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Whisper](https://github.com/openai/whisper)
- [Cahier des charges PDF](./Futures_War_Cahier_des_Charges.pdf)

---

**Fait avec ❤️ pour imaginer le futur de Marseille**