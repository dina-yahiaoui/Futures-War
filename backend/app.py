from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import psutil
import torch
from dotenv import load_dotenv

# DB (Nans)
from db.database import init_db, get_db
from db import crud

# Services
from whisper_utils import get_whisper_service
from gpu_client import get_gpu_client

# Prompt pipeline (toi + Nans)
# - optimize_prompt / get_negative_prompt : version Pierre
# - build_final_prompt : version Nans (SFW + enrichissement + negative)
from prompt_utils import optimize_prompt, get_negative_prompt, build_final_prompt

# Charger les variables d'environnement
load_dotenv()

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "futures-war-secret-token-2026")

# Créer le dossier uploads
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Futures War API",
    description="API d'orchestration IA : speech-to-text, prompt-to-image, system-stats",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # à restreindre plus tard si besoin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou manquant"
        )
    return credentials.credentials


# Init DB au démarrage (Nans)
@app.on_event("startup")
def _startup():
    init_db()


# Modèles
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
    # Bonus : info prompt pour debug (tu peux retirer si tu veux)
    original_prompt: Optional[str] = None
    cleaned_prompt: Optional[str] = None
    final_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    saved_id: Optional[int] = None
    is_sfw: Optional[bool] = None


@app.get("/", tags=["health"])
def root():
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
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier audio")

    file_path = f"uploads/{file.filename}"
    try:
        # 1) Sauvegarde le fichier uploadé
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 2) Vérifie que ffmpeg est installé (sinon Whisper va planter)
        import shutil
        if shutil.which("ffmpeg") is None:
            # On supprime le fichier temporaire avant de répondre
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=400,
                detail="ffmpeg est requis pour la transcription audio. Installe ffmpeg (ou lance le backend dans un Docker qui contient ffmpeg)."
            )

        # 3) Transcription Whisper
        whisper_service = get_whisper_service()
        text = whisper_service.transcribe(file_path, language="fr")

        # 4) Nettoyage
        if os.path.exists(file_path):
            os.remove(file_path)

        return SpeechToTextResponse(text=text)

    except HTTPException:
        # On laisse passer les erreurs HTTP (comme celle du ffmpeg)
        raise
    except Exception as e:
        # Nettoyage en cas d'erreur
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
    Génération d'image à partir d'un prompt.
    - Filtrage SFW + enrichissement (Nans)
    - Fallback optimize_prompt + negative prompt (Pierre) si besoin
    - Sauvegarde en SQLite (Nans)
    """

    prompt_input = (request.prompt or "").strip()
    if not prompt_input:
        raise HTTPException(status_code=400, detail="Prompt vide")

    # 1) Pipeline Nans (SFW + enrichissement + negative)
    prompt_result = None
    try:
        prompt_result = build_final_prompt(prompt_input)
    except Exception:
        prompt_result = None

    # 2) Si build_final_prompt existe et renvoie un dict attendu
    if isinstance(prompt_result, dict) and "success" in prompt_result:
        if not prompt_result["success"]:
            # log tentative bloquée
            try:
                gen = crud.create_generation(
                    prompt=prompt_input,
                    image_path="",
                    is_sfw=False,
                    flagged_reason=prompt_result.get("error")
                )
                saved_id = gen.get("id")
            except Exception:
                saved_id = None

            raise HTTPException(
                status_code=400,
                detail=prompt_result.get("error", "Prompt refusé (SFW)")
            )

        final_prompt = prompt_result.get("positive_prompt") or prompt_input
        negative = prompt_result.get("negative_prompt") or (request.negative_prompt or get_negative_prompt())
        cleaned = prompt_result.get("cleaned_text")
        original = prompt_result.get("original_text", prompt_input)

    else:
        # 3) Fallback Pierre (si module Nans pas dispo)
        final_prompt = optimize_prompt(prompt_input)
        negative = request.negative_prompt or get_negative_prompt()
        cleaned = None
        original = prompt_input

    # 4) Génération image via GPU client
    gpu_client = get_gpu_client()
    images = gpu_client.generate_image(
        prompt=final_prompt,
        negative_prompt=negative,
        width=request.width,
        height=request.height,
        steps=request.steps,
        guidance_scale=request.guidance_scale,
        seed=request.seed
    )

    # 5) Sauvegarde DB (si au moins 1 image)
    saved_id = None
    try:
        image_path = images[0] if images else ""
        gen = crud.create_generation(
            prompt=final_prompt,
            image_path=image_path,
            is_sfw=True,
            flagged_reason=None
        )
        saved_id = gen.get("id")
    except Exception:
        saved_id = None

    return PromptToImageResponse(
        images=images,
        model=request.model,
        original_prompt=original,
        cleaned_prompt=cleaned,
        final_prompt=final_prompt,
        negative_prompt=negative,
        saved_id=saved_id,
        is_sfw=True
    )


# SYSTEM STATS
@app.get(
    "/api/system-stats",
    tags=["orchestrator"],
    dependencies=[Depends(verify_token)]
)
async def system_stats():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()

    ram = psutil.virtual_memory()

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

    disk = psutil.disk_usage('/')

    whisper_service = get_whisper_service()
    whisper_info = whisper_service.get_info()

    return {
        "cpu": {"count": cpu_count, "percent": cpu_percent},
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
        "whisper": whisper_info,
    }