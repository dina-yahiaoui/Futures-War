"""
Service de transcription audio avec Whisper
Conforme à la spec OpenAPI
"""

import whisper
import torch
import os
from typing import Optional

class WhisperService:
    """Service simple pour transcrire de l'audio en texte"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialise Whisper
        
        Args:
            model_size: Taille du modèle (tiny, base, small, medium, large)
        """
        print(f"📝 Chargement de Whisper (modèle: {model_size})...")
        
        # Détection du device (GPU ou CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"💻 Device utilisé: {self.device}")
        
        # Charger le modèle
        self.model = whisper.load_model(model_size, device=self.device)
        self.model_size = model_size
        
        print("✅ Whisper prêt!")
    
    def transcribe(self, audio_path: str, language: str = "fr") -> str:
        """
        Transcrit un fichier audio en texte
        
        Args:
            audio_path: Chemin vers le fichier audio
            language: Langue (fr, en, etc.)
        
        Returns:
            Le texte transcrit
        """
        print(f"🎤 Transcription de: {audio_path}")
        
        # Transcription
        result = self.model.transcribe(
            audio_path,
            language=language,
            fp16=(self.device == "cuda")  # Optimisation GPU
        )
        
        text = result["text"].strip()
        print(f"✅ Transcription terminée: {len(text)} caractères")
        
        return text
    
    def get_info(self) -> dict:
        """
        Retourne les infos du service (pour /api/system-stats)
        
        Returns:
            Dict avec model_size et device
        """
        return {
            "model_size": self.model_size,
            "device": self.device
        }


# Instance globale (singleton)
_whisper_service: Optional[WhisperService] = None

def get_whisper_service() -> WhisperService:
    """
    Récupère l'instance du service Whisper
    
    Returns:
        Instance de WhisperService
    """
    global _whisper_service
    
    if _whisper_service is None:
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        _whisper_service = WhisperService(model_size)
    
    return _whisper_service