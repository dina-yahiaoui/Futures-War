"""
Service d'optimisation de prompts pour la génération d'images
"""

from typing import Optional

class PromptOptimizer:
    """Service pour enrichir les prompts utilisateur"""
    
    def __init__(self):
        """Initialise l'optimiseur avec des mots-clés"""
        
        # Mots-clés pour Marseille
        self.marseille_keywords = [
            "Marseille", "Vieux-Port", "Notre-Dame de la Garde",
            "Méditerranée", "calanques", "architecture provençale"
        ]
        
        # Mots-clés pour un futur positif
        self.future_keywords = [
            "futuriste", "durable", "écologique", "innovant",
            "lumineux", "moderne", "harmonieux"
        ]
        
        # Style visuel
        self.style_keywords = [
            "haute qualité", "réaliste", "détaillé",
            "lumière naturelle", "8k", "professionnel"
        ]
    
    def optimize(
        self,
        user_prompt: str,
        add_marseille: bool = True,
        add_future: bool = True,
        add_style: bool = True
    ) -> str:
        """
        Enrichit un prompt utilisateur
        
        Args:
            user_prompt: Le prompt de base de l'utilisateur
            add_marseille: Ajouter des mots-clés Marseille
            add_future: Ajouter des mots-clés futur
            add_style: Ajouter des mots-clés de style
        
        Returns:
            Le prompt optimisé
        
        Exemple:
            Input: "des arbres partout"
            Output: "Marseille en 2050, des arbres partout, futuriste, 
                     durable, haute qualité, réaliste"
        """
        parts = []
        
        # Base: toujours Marseille en 2050
        if add_marseille:
            parts.append("Marseille en 2050")
        
        # Prompt utilisateur
        parts.append(user_prompt)
        
        # Ajouter quelques mots-clés futur
        if add_future:
            parts.extend(self.future_keywords[:2])
        
        # Ajouter style
        if add_style:
            parts.extend(self.style_keywords[:2])
        
        # Joindre tout
        optimized = ", ".join(parts)
        
        return optimized
    
    def create_negative_prompt(self) -> str:
        """
        Crée un prompt négatif (ce qu'on ne veut PAS voir)
        
        Returns:
            Prompt négatif
        """
        negative = [
            "pollution", "sombre", "dystopique", "apocalyptique",
            "déchets", "destruction", "mauvaise qualité",
            "flou", "distordu"
        ]
        
        return ", ".join(negative)


# Instance globale
_optimizer = PromptOptimizer()

def optimize_prompt(user_prompt: str) -> str:
    """
    Fonction simple pour optimiser un prompt
    
    Args:
        user_prompt: Le prompt utilisateur
    
    Returns:
        Le prompt optimisé
    """
    return _optimizer.optimize(user_prompt)

def get_negative_prompt() -> str:
    """
    Récupère le prompt négatif
    
    Returns:
        Le prompt négatif
    """
    return _optimizer.create_negative_prompt()