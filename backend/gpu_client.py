"""
Client pour communiquer avec le serveur GPU distant
URL: http://37.26.187.4:8000
"""

import requests
import base64
import os
from typing import Optional, List


class GPUClient:
    """Client pour le serveur GPU distant"""
    
    def __init__(self):
        """Initialise le client GPU"""
        self.base_url = "http://37.26.187.4:8000"
        self.token = "tristanlovesia"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        print(f"🎨 GPU Client initialisé: {self.base_url}")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        steps: int = 9,
        guidance_scale: float = 0.0,
        seed: Optional[int] = None
    ) -> List[str]:
        """
        Génère une image à partir d'un prompt
        
        Args:
            prompt: Description de l'image
            negative_prompt: Ce qu'on ne veut pas voir
            width: Largeur de l'image
            height: Hauteur de l'image
            steps: Nombre d'étapes
            guidance_scale: Force du respect du prompt
            seed: Graine pour la reproductibilité
        
        Returns:
            Liste d'images en base64
        """
        print(f"🎨 Génération d'image sur serveur distant...")
        print(f"   Prompt: {prompt[:60]}...")
        
        # Préparer la requête
        payload = {
            "prompt": prompt,
            "model": "Tongyi-MAI/Z-Image-Turbo",
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        if seed is not None:
            payload["seed"] = seed
        
        try:
            # Appeler l'API distante
            response = requests.post(
                f"{self.base_url}/api/prompt-to-image",
                headers=self.headers,
                json=payload,
                timeout=120  # 120 secondes max
            )
            
            # Vérifier la réponse
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                print(f"✅ Image générée avec succès !")
                print(f"   Nombre d'images: {len(images)}")
                return images
            
            elif response.status_code == 401:
                print(f"❌ Erreur d'authentification (token invalide)")
                raise Exception("Token d'authentification invalide")
            
            else:
                print(f"❌ Erreur serveur: {response.status_code}")
                print(f"   Réponse: {response.text}")
                raise Exception(f"Erreur serveur: {response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: Le serveur met trop de temps à répondre")
            raise Exception("Timeout du serveur GPU")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Impossible de se connecter au serveur")
            raise Exception("Serveur GPU injoignable")
        
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            raise
    
    def check_connection(self) -> bool:
        """
        Vérifie que le serveur GPU est accessible
        
        Returns:
            True si accessible, False sinon
        """
        try:
            print(f"🔍 Test de connexion au serveur GPU...")
            response = requests.get(
                f"{self.base_url}/api/system-stats",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Connexion OK !")
                return True
            else:
                print(f"❌ Connexion échouée: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Erreur de connexion: {str(e)}")
            return False


# Instance globale
_gpu_client: Optional[GPUClient] = None

def get_gpu_client() -> GPUClient:
    """
    Récupère l'instance du GPU client
    
    Returns:
        Instance de GPUClient
    """
    global _gpu_client
    
    if _gpu_client is None:
        _gpu_client = GPUClient()
    
    return _gpu_client