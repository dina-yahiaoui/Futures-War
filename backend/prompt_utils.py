"""
Prompt Engineering Module - Futures-War Project

Transforms raw Whisper transcription into optimized AI image generation prompt
with Safe For Work filtering and Marseille context enrichment.

Pipeline: Raw Text → Clean → Validate (SFW) → Enrich (Dynamic) → JSON Output
"""

import re


# ============================================================================
# CONFIGURATION - SFW SAFETY
# ============================================================================

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

# ============================================================================
# DYNAMIC KEYWORD ENRICHMENT LIBRARY
# ============================================================================

KEYWORD_ENHANCEMENTS = {
    # Ecology & Environment
    ("écologie", "écologique", "vert", "green", "environmental", "sustainable", "ecology"):
        ", lush vegetation, rooftop gardens, urban forest, green energy, "
        "renewable sources, solar panels, eco-friendly infrastructure, "
        "sustainable materials, living walls",
    
    # Transport & Mobility
    ("transport", "mobility", "transit", "bus", "metro", "transports", "mobilité"):
        ", futuristic transportation system, autonomous vehicles, smart mobility, "
        "solar-powered transit, modern trams, intelligent traffic, "
        "pedestrian-friendly streets, cycling infrastructure, high-speed rail",
    
    # Water & Maritime
    ("eau", "water", "marine", "port", "harbor", "waterfront", "sea"):
        ", waterfront development, modern marina, clean waterways, "
        "sustainable fishing, maritime tourism, water taxis, "
        "scenic harbor views, vibrant quays",
    
    # Technology & Innovation
    ("technologie", "technology", "innovation", "smart", "digital", "connected", "future"):
        ", cutting-edge technology, smart city infrastructure, IoT integration, "
        "holographic displays, connected systems, advanced robotics, "
        "5G networks, innovative design",
    
    # Year 2050 / Futuristic
    ("2050", "futur", "future", "demain", "next generation", "tomorrow", "ahead"):
        ", advanced future cityscape, next-generation architecture, "
        "visionary design, transformative development, forward-thinking, "
        "progress, innovation hub, century ahead",
    
    # Cultural & Heritage
    ("culture", "culturelle", "heritage", "art", "artist", "museum", "historical"):
        ", vibrant cultural scene, artistic communities, creative districts, "
        "public art installations, cultural landmarks, heritage preservation, "
        "historic sites, museum district",
    
    # Tourism & Recreation
    ("tourisme", "touriste", "recreation", "loisir", "beach", "plage", "leisure"):
        ", tourist destination, recreational areas, leisure facilities, "
        "beach clubs, entertainment venues, vibrant nightlife, "
        "public spaces, promenades",
    
    # Quality of Life
    ("qualité", "vie", "quality", "life", "vivre", "habitable", "livable"):
        ", high quality of life, comfortable living, well-being spaces, "
        "health-conscious design, happiness index, social cohesion, "
        "strong community bonds",
    
    # Business & Economy
    ("commerce", "business", "économie", "economy", "startups", "entreprise", "economy"):
        ", vibrant business district, startup hub, economic powerhouse, "
        "corporate headquarters, innovation centers, job creation, "
        "commercial hubs, professional spaces",
    
    # Energy & Renewable
    ("énergie", "energy", "solar", "renouvelable", "renewable", "wind", "clean"):
        ", renewable energy infrastructure, solar architecture, "
        "wind turbines, geothermal systems, energy-efficient buildings, "
        "clean power generation, carbon-neutral",
    
    # Architecture & Design
    ("architecture", "bâtiment", "building", "design", "structure", "façade", "moderne"):
        ", stunning architecture, modern structures, iconic buildings, "
        "award-winning design, contemporary facades, innovative structures, "
        "architectural excellence",
    
    # Nature & Parks
    ("parc", "park", "nature", "naturel", "arbre", "tree", "fleurs", "flowers"):
        ", abundant green spaces, nature reserves, botanical gardens, "
        "urban parks, landscaped areas, tree-lined streets, "
        "natural beauty, wildlife corridors",
    
    # Mediterranean Context
    ("méditerranée", "mediterranean", "provence", "marseille", "côte", "coast"):
        ", Mediterranean architecture, coastal vibes, provençal charm, "
        "sun-drenched locations, warm Mediterranean climate, "
        "blue skies, seaside elegance",
    
    # Residential & Housing
    ("résidentiel", "residential", "housing", "maison", "apartment", "habitation", "dwell"):
        ", residential communities, modern housing, apartments, "
        "family neighborhoods, comfortable homes, safe communities, "
        "diverse housing options",
    
    # Public Spaces & Gathering
    ("place", "square", "plaza", "espace public", "public space", "gathering"):
        ", public squares, gathering spaces, community hubs, "
        "vibrant plazas, social spaces, outdoor venues, pedestrian areas, "
        "inclusive spaces",
}


# ============================================================================
# STEP 1: CLEANING
# ============================================================================

def clean_transcription(text: str) -> str:
    """
    Basic text cleaning - ultra simple approach.
    
    - Strip whitespace
    - Remove common filler words (euh, hein, etc)
    - Remove double spaces
    - Convert to lowercase for processing
    
    Returns cleaned text (lowercase for validation, original case preserved in output)
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove common French filler words
    fillers = ["euh", "hein", "ouais", "bah", "quoi", "genre"]
    for filler in fillers:
        text = re.sub(r'\b' + filler + r'\b', '', text, flags=re.IGNORECASE)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# ============================================================================
# STEP 2: SFW VALIDATION
# ============================================================================

def is_prompt_safe(text: str) -> tuple[bool, str]:
    """
    Validate prompt against forbidden content.
    
    Args:
        text: Cleaned transcription text
        
    Returns:
        (is_safe: bool, reason: str)
        - (True, "") if safe
        - (False, reason) if unsafe with reason
    """
    if not text:
        return True, ""
    
    text_lower = text.lower()
    
    # Check for forbidden words
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return False, f"Content contains inappropriate word: '{word}'"
    
    # Check for suspicious patterns (multiple bad words combined)
    bad_word_count = sum(1 for word in FORBIDDEN_WORDS if word in text_lower)
    if bad_word_count >= 2:
        return False, "Multiple inappropriate terms detected"
    
    return True, ""


# ============================================================================
# STEP 3: DYNAMIC ENRICHMENT (V2 - KEYWORD BASED)
# ============================================================================

def enrich_with_keywords(text: str) -> str:
    """
    Dynamically enrich prompt based on detected keywords.
    
    Scans text for keywords and adds contextual enhancements.
    Supports French and English keywords.
    
    Args:
        text: Cleaned user prompt
        
    Returns:
        Enriched prompt text with relevant context added
    """
    if not text:
        return ""
    
    text_lower = text.lower()
    enhancements = []
    
    # Check each keyword group
    for keywords, enhancement in KEYWORD_ENHANCEMENTS.items():
        # Check if any keyword in the group is found
        if any(keyword in text_lower for keyword in keywords):
            enhancements.append(enhancement)
    
    # Build enriched text
    result = text
    if enhancements:
        # Combine all relevant enhancements (avoid duplication by using set)
        combined = ", ".join(set(enhancements))
        result += combined
    
    return result


def enrich_prompt(text: str) -> str:
    """
    Enrich user text with Marseille context and dynamic keywords.
    
    V2: Dynamic enrichment based on keywords + base style
    
    Args:
        text: Cleaned user prompt
        
    Returns:
        Enriched prompt ready for image generation
    """
    if not text:
        return BASE_STYLE
    
    # Step 1: Add dynamic keyword enhancements
    enriched = enrich_with_keywords(text)
    
    # Step 2: Add base style for consistency
    enriched = f"{enriched}, {BASE_STYLE}"
    
    return enriched


# ============================================================================
# STEP 4: BUILD NEGATIVE PROMPT
# ============================================================================

def build_negative_prompt() -> str:
    """
    Return the standard negative prompt for SFW guarantee.
    
    This is sent to the image model to prevent generation of:
    - NSFW content (nudity, sexual content)
    - Violence (gore, weapons, blood)
    - Low quality (blurry, distorted, extra limbs)
    
    Note: Open-source models may partially ignore negative prompts,
    so this is combined with blacklist validation.
    """
    return NEGATIVE_PROMPT


# ============================================================================
# STEP 5: ORCHESTRATOR - MAIN FUNCTION
# ============================================================================

def build_final_prompt(text: str) -> dict:
    """
    Main orchestrator - transforms raw transcription into structured prompt JSON.
    
    Pipeline:
    1. Clean the text
    2. Validate SFW
    3. Enrich with dynamic keywords
    4. Build negative prompt
    5. Return structured JSON
    
    Args:
        text: Raw transcription from Whisper
        
    Returns:
        dict with structure:
        {
            "success": bool,
            "error": str (if success=False),
            "original_text": str,
            "cleaned_text": str,
            "positive_prompt": str,
            "negative_prompt": str
        }
    """
    
    # Step 1: Clean
    cleaned = clean_transcription(text)
    
    # Step 2: Validate SFW
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
    
    # Step 3: Enrich with dynamic keywords
    enriched = enrich_prompt(cleaned)
    
    # Step 4: Build negative prompt
    negative = build_negative_prompt()
    
    # Step 5: Return success
    return {
        "success": True,
        "error": None,
        "original_text": text,
        "cleaned_text": cleaned,
        "positive_prompt": enriched,
        "negative_prompt": negative
    }


# ============================================================================
# SIMPLE TEST FUNCTION (for debugging)
# ============================================================================

def test_prompt_builder():
    """Quick test function - run with: python -m backend.prompt_utils"""
    
    test_cases = [
        "Marseille avec plus d'arbres",
        "Marseille écologique en 2050",
        "Des transports solaires et verts",
        "Innovation technologique et culture",
        "Qualité de vie et nature",
        "nude Marseille",  # Should fail SFW
        "violence at the beach",  # Should fail SFW
    ]
    
    print("=" * 80)
    print("PROMPT BUILDER TEST - WITH DYNAMIC ENRICHMENT")
    print("=" * 80)
    
    for test_input in test_cases:
        print(f"\n📝 Input: {test_input}")
        result = build_final_prompt(test_input)
        
        if result["success"]:
            print(f"✅ SUCCESS")
            print(f"   Original: {result['original_text']}")
            print(f"   Cleaned: {result['cleaned_text']}")
            print(f"   Enriched: {result['positive_prompt'][:150]}...")
        else:
            print(f"❌ BLOCKED: {result['error']}")
        print()


if __name__ == "__main__":
    test_prompt_builder()
