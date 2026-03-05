"""
Prompt utilities - Futures War

Fusion Pierre + Nans:
- optimize_prompt() / get_negative_prompt() (compatibilité Pierre)
- build_final_prompt() (pipeline Nans : clean → SFW → enrich → negative → JSON)
"""

from __future__ import annotations
from typing import Optional, Tuple, Dict
import re


# =============================================================================
# PIERRE - Optimizer simple (Marseille + futur + style)
# =============================================================================

class PromptOptimizer:
    """Service simple pour enrichir les prompts utilisateur"""

    def __init__(self):
        self.marseille_keywords = [
            "Marseille", "Vieux-Port", "Notre-Dame de la Garde",
            "Méditerranée", "calanques", "architecture provençale"
        ]

        self.future_keywords = [
            "futuriste", "durable", "écologique", "innovant",
            "lumineux", "moderne", "harmonieux"
        ]

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
        parts = []
        if add_marseille:
            parts.append("Marseille en 2050")
        parts.append(user_prompt)

        if add_future:
            parts.extend(self.future_keywords[:2])

        if add_style:
            parts.extend(self.style_keywords[:2])

        return ", ".join([p for p in parts if p])

    def create_negative_prompt(self) -> str:
        negative = [
            "pollution", "sombre", "dystopique", "apocalyptique",
            "déchets", "destruction", "mauvaise qualité",
            "flou", "distordu"
        ]
        return ", ".join(negative)


_optimizer = PromptOptimizer()

def optimize_prompt(user_prompt: str) -> str:
    """Compat Pierre"""
    return _optimizer.optimize(user_prompt)

def get_negative_prompt() -> str:
    """Compat Pierre"""
    return _optimizer.create_negative_prompt()


# =============================================================================
# NANS - Pipeline SFW + enrichment + negative prompt
# =============================================================================

FORBIDDEN_WORDS = [
    "nude", "nudity", "naked", "sex", "porn", "pornographic",
    "gore", "blood", "bloody", "violence", "violent", "kill", "death",
    "explicit", "nsfw", "adult", "xxx", "erotic", "sexual",
    "weapon", "gun", "bomb", "terrorist", "rape", "assault"
]

NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, nsfw, nudity, pornographic, "
    "nude, naked, sex, gore, blood, violence, weapons, explicit content, "
    "extra limbs, missing limbs, malformed, deformed, ugly, bad anatomy, "
    "worst quality, low res, watermark, text"
)

BASE_STYLE = (
    "futuristic Mediterranean city, cinematic lighting, "
    "ultra detailed, high resolution, 4k, award-winning photography, "
    "professional quality, warm sunlight, architectural marvel"
)

KEYWORD_ENHANCEMENTS = {
    ("écologie", "écologique", "vert", "green", "environmental", "sustainable", "ecology"):
        ", lush vegetation, rooftop gardens, urban forest, green energy, "
        "renewable sources, solar panels, eco-friendly infrastructure, "
        "sustainable materials, living walls",

    ("transport", "mobility", "transit", "bus", "metro", "transports", "mobilité"):
        ", futuristic transportation system, autonomous vehicles, smart mobility, "
        "solar-powered transit, modern trams, intelligent traffic, "
        "pedestrian-friendly streets, cycling infrastructure, high-speed rail",

    ("eau", "water", "marine", "port", "harbor", "waterfront", "sea"):
        ", waterfront development, modern marina, clean waterways, "
        "sustainable fishing, maritime tourism, water taxis, "
        "scenic harbor views, vibrant quays",

    ("technologie", "technology", "innovation", "smart", "digital", "connected", "future"):
        ", cutting-edge technology, smart city infrastructure, IoT integration, "
        "holographic displays, connected systems, advanced robotics, "
        "5G networks, innovative design",

    ("2050", "futur", "future", "demain", "next generation", "tomorrow", "ahead"):
        ", advanced future cityscape, next-generation architecture, "
        "visionary design, transformative development, forward-thinking, "
        "progress, innovation hub, century ahead",

    ("culture", "culturelle", "heritage", "art", "artist", "museum", "historical"):
        ", vibrant cultural scene, artistic communities, creative districts, "
        "public art installations, cultural landmarks, heritage preservation, "
        "historic sites, museum district",

    ("tourisme", "touriste", "recreation", "loisir", "beach", "plage", "leisure"):
        ", tourist destination, recreational areas, leisure facilities, "
        "beach clubs, entertainment venues, vibrant nightlife, "
        "public spaces, promenades",

    ("qualité", "vie", "quality", "life", "vivre", "habitable", "livable"):
        ", high quality of life, comfortable living, well-being spaces, "
        "health-conscious design, happiness index, social cohesion, "
        "strong community bonds",

    ("commerce", "business", "économie", "economy", "startups", "entreprise", "economy"):
        ", vibrant business district, startup hub, economic powerhouse, "
        "corporate headquarters, innovation centers, job creation, "
        "commercial hubs, professional spaces",

    ("énergie", "energy", "solar", "renouvelable", "renewable", "wind", "clean"):
        ", renewable energy infrastructure, solar architecture, "
        "wind turbines, geothermal systems, energy-efficient buildings, "
        "clean power generation, carbon-neutral",

    ("architecture", "bâtiment", "building", "design", "structure", "façade", "moderne"):
        ", stunning architecture, modern structures, iconic buildings, "
        "award-winning design, contemporary facades, innovative structures, "
        "architectural excellence",

    ("parc", "park", "nature", "naturel", "arbre", "tree", "fleurs", "flowers"):
        ", abundant green spaces, nature reserves, botanical gardens, "
        "urban parks, landscaped areas, tree-lined streets, "
        "natural beauty, wildlife corridors",

    ("méditerranée", "mediterranean", "provence", "marseille", "côte", "coast"):
        ", Mediterranean architecture, coastal vibes, provençal charm, "
        "sun-drenched locations, warm Mediterranean climate, "
        "blue skies, seaside elegance",

    ("résidentiel", "residential", "housing", "maison", "apartment", "habitation", "dwell"):
        ", residential communities, modern housing, apartments, "
        "family neighborhoods, comfortable homes, safe communities, "
        "diverse housing options",

    ("place", "square", "plaza", "espace public", "public space", "gathering"):
        ", public squares, gathering spaces, community hubs, "
        "vibrant plazas, social spaces, outdoor venues, pedestrian areas, "
        "inclusive spaces",
}


def clean_transcription(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()

    fillers = ["euh", "hein", "ouais", "bah", "quoi", "genre"]
    for filler in fillers:
        text = re.sub(r"\b" + re.escape(filler) + r"\b", "", text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_prompt_safe(text: str) -> Tuple[bool, str]:
    if not text:
        return True, ""

    text_lower = text.lower()

    # simple check
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return False, f"Content contains inappropriate word: '{word}'"

    # count check (rarement utile mais ok)
    bad_word_count = sum(1 for word in FORBIDDEN_WORDS if word in text_lower)
    if bad_word_count >= 2:
        return False, "Multiple inappropriate terms detected"

    return True, ""


def enrich_with_keywords(text: str) -> str:
    if not text:
        return ""

    text_lower = text.lower()
    enhancements = []

    for keywords, enhancement in KEYWORD_ENHANCEMENTS.items():
        if any(keyword in text_lower for keyword in keywords):
            enhancements.append(enhancement)

    result = text
    if enhancements:
        combined = ", ".join(set(enhancements))
        result += combined

    return result


def enrich_prompt(text: str) -> str:
    if not text:
        return BASE_STYLE
    enriched = enrich_with_keywords(text)
    enriched = f"{enriched}, {BASE_STYLE}"
    return enriched


def build_negative_prompt() -> str:
    return NEGATIVE_PROMPT


def build_final_prompt(text: str) -> Dict[str, Optional[str]]:
    cleaned = clean_transcription(text)

    is_safe, reason = is_prompt_safe(cleaned)
    if not is_safe:
        return {
            "success": False,
            "error": f"Content policy violation: {reason}",
            "original_text": text,
            "cleaned_text": cleaned,
            "positive_prompt": None,
            "negative_prompt": None
        }

    enriched = enrich_prompt(cleaned)
    negative = build_negative_prompt()

    return {
        "success": True,
        "error": None,
        "original_text": text,
        "cleaned_text": cleaned,
        "positive_prompt": enriched,
        "negative_prompt": negative
    }


if __name__ == "__main__":
    # test rapide
    tests = [
        "Marseille avec plus d'arbres",
        "Marseille écologique en 2050",
        "Des transports solaires et verts",
        "Innovation technologique et culture",
        "nude Marseille",
    ]
    for t in tests:
        print(t, "->", build_final_prompt(t)["success"])