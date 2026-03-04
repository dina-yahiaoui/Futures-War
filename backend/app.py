from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import psutil
import torch

# Import des services
from whisper_utils import get_whisper_service
from prompt_utils import optimize_prompt, get_negative_prompt
from gpu_client import get_gpu_client

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()


# CONFIGURATION


API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "futures-war-secret-token-2026")

# Créer le dossier uploads
os.makedirs("uploads", exist_ok=True)


# APPLICATION FASTAPI


app = FastAPI(
    title="AI Orchestrator API",
    description="API d'orchestration IA : speech-to-text, prompt-to-image, chat completions",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SÉCURITÉ


security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie le token Bearer"""
    if credentials.credentials != API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou manquant"
        )
    return credentials.credentials


# MODÈLES DE DONNÉES


class SpeechToTextResponse(BaseModel):
    text: str

class PromptToImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = "Tongyi-MAI/Z-Image-Turbo"
    steps: Optional[int] = 9
    guidance_scale: Optional[float] = 0.0
    height: Optional[int] = 1024
    width: Optional[int] = 1024
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

class PromptToImageResponse(BaseModel):
    images: List[str]
    model: str


# ROUTES

@app.get("/", tags=["health"])
def root():
    """Page d'accueil"""
    return {
        "message": "🚀 Futures War API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "routes": {
            "speech_to_text": "/api/speech-to-text",
            "prompt_to_image": "/api/prompt-to-image",
            "system_stats": "/api/system-stats"
        }
    }


# SPEECH-TO-TEXT


@app.post(
    "/api/speech-to-text",
    response_model=SpeechToTextResponse,
    tags=["orchestrator"],
    dependencies=[Depends(verify_token)]
)
async def speech_to_text(file: UploadFile = File(...)):
    """
    Transcription audio → texte avec Whisper
    
    Requiert: Bearer Token
    """
    
    # Vérifier que c'est un fichier audio
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un fichier audio"
        )
    
    # Sauvegarder temporairement
    file_path = f"uploads/{file.filename}"
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Transcrire avec Whisper
        whisper_service = get_whisper_service()
        text = whisper_service.transcribe(file_path, language="fr")
        
        # Nettoyer
        os.remove(file_path)
        
        return SpeechToTextResponse(text=text)
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


# PROMPT-TO-IMAGE


@app.post(
    "/api/prompt-to-image",
    response_model=PromptToImageResponse,
    tags=["orchestrator"],
    dependencies=[Depends(verify_token)]
)
async def prompt_to_image(request: PromptToImageRequest):
    """
    Génération d'image à partir d'un prompt
    
    Requiert: Bearer Token
    """
    
    # Optimiser le prompt
    optimized_prompt = optimize_prompt(request.prompt)
    
    # Prompt négatif (si pas fourni)
    negative = request.negative_prompt or get_negative_prompt()
    
    # Générer l'image
    gpu_client = get_gpu_client()
    images = gpu_client.generate_image(
        prompt=optimized_prompt,
        negative_prompt=negative,
        width=request.width,
        height=request.height,
        steps=request.steps,
        guidance_scale=request.guidance_scale,
        seed=request.seed
    )
    
    return PromptToImageResponse(
        images=images,
        model=request.model
    )


# SYSTEM STATS


@app.get(
    "/api/system-stats",
    tags=["orchestrator"],
    dependencies=[Depends(verify_token)]
)
async def system_stats():
    """Statistiques système"""
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # RAM
    ram = psutil.virtual_memory()
    
    # GPU
    gpus = []
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpus.append({
                "index": i,
                "device_name": torch.cuda.get_device_name(i),
                "vram_total_mb": torch.cuda.get_device_properties(i).total_memory / 1024 / 1024,
                "vram_allocated_mb": torch.cuda.memory_allocated(i) / 1024 / 1024,
                "vram_reserved_mb": torch.cuda.memory_reserved(i) / 1024 / 1024
            })
    
    # Disque
    disk = psutil.disk_usage('/')
    
    # Services
    whisper_service = get_whisper_service()
    whisper_info = whisper_service.get_info()
    
    return {
        "cpu": {
            "count": cpu_count,
            "percent": cpu_percent
        },
        "ram": {
            "total_mb": ram.total / 1024 / 1024,
            "available_mb": ram.available / 1024 / 1024,
            "used_mb": ram.used / 1024 / 1024,
            "percent": ram.percent
        },
        "gpus": gpus,
        "disk": {
            "path": "/",
            "total_gb": disk.total / 1024 / 1024 / 1024,
            "used_gb": disk.used / 1024 / 1024 / 1024,
            "free_gb": disk.free / 1024 / 1024 / 1024,
            "percent": disk.percent
        },
        "uptime_seconds": None,
        "whisper": whisper_info,
        "zimage": {
            "model": "Tongyi-MAI/Z-Image-Turbo",
            "device": "cpu",
            "steps": 9,
            "guidance": 0.0,
            "height": 1024,
            "width": 1024
        }
    }


# LANCEMENT


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Démarrage de Futures War API")
    print("=" * 60)
    print(f"📝 Documentation: http://localhost:8000/docs")
    print(f"🔐 Token: {API_BEARER_TOKEN}")
    print("=" * 60)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

