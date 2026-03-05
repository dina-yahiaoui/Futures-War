"""
KEYWORD ENRICHMENT GUIDE - Futures-War Project

This document explains how dynamic keyword enrichment works.
"""

ENRICHMENT_CATEGORIES = {
    "Ecology & Environment": {
        "keywords": ["écologie", "écologique", "vert", "green", "environmental", "sustainable"],
        "enhancement": "lush vegetation, rooftop gardens, urban forest, green energy, renewable sources, solar panels, eco-friendly infrastructure"
    },
    
    "Transport & Mobility": {
        "keywords": ["transport", "mobility", "transit", "bus", "metro", "transports", "mobilité"],
        "enhancement": "futuristic transportation system, autonomous vehicles, smart mobility, solar-powered transit, modern trams, intelligent traffic"
    },
    
    "Water & Maritime": {
        "keywords": ["eau", "water", "marine", "port", "harbor", "waterfront", "sea"],
        "enhancement": "waterfront development, modern marina, clean waterways, sustainable fishing, maritime tourism, water taxis"
    },
    
    "Technology & Innovation": {
        "keywords": ["technologie", "technology", "innovation", "smart", "digital", "connected"],
        "enhancement": "cutting-edge technology, smart city infrastructure, IoT integration, holographic displays, connected systems, advanced robotics"
    },
    
    "Year 2050 / Futuristic": {
        "keywords": ["2050", "futur", "future", "demain", "next generation", "tomorrow"],
        "enhancement": "advanced future cityscape, next-generation architecture, visionary design, transformative development, forward-thinking"
    },
    
    "Cultural & Heritage": {
        "keywords": ["culture", "culturelle", "heritage", "art", "artist", "museum"],
        "enhancement": "vibrant cultural scene, artistic communities, creative districts, public art installations, cultural landmarks"
    },
    
    "Quality of Life": {
        "keywords": ["qualité", "vie", "quality", "life", "vivre", "habitable"],
        "enhancement": "high quality of life, comfortable living, well-being spaces, health-conscious design, happiness index"
    },
    
    "Nature & Parks": {
        "keywords": ["parc", "park", "nature", "naturel", "arbre", "tree", "fleurs"],
        "enhancement": "abundant green spaces, nature reserves, botanical gardens, urban parks, landscaped areas, tree-lined streets"
    },
}

EXAMPLE_TRANSFORMATIONS = [
    {
        "input": "Marseille écologique en 2050",
        "keywords_detected": ["écologique", "2050"],
        "categories": ["Ecology & Environment", "Year 2050 / Futuristic"],
        "output": "Marseille écologique en 2050, lush vegetation, rooftop gardens, urban forest, green energy, renewable sources, solar panels, eco-friendly infrastructure, sustainable materials, living walls, advanced future cityscape, next-generation architecture, visionary design, transformative development, forward-thinking, progress, innovation hub, century ahead, futuristic Mediterranean city, cinematic lighting, ultra detailed, high resolution, 4k, award-winning photography, professional quality, warm sunlight, architectural marvel"
    },
    
    {
        "input": "Marseille verte avec innovation technologique",
        "keywords_detected": ["vert", "technologie"],
        "categories": ["Ecology & Environment", "Technology & Innovation"],
        "output": "Marseille verte avec innovation technologique, lush vegetation, rooftop gardens, urban forest, green energy, renewable sources, solar panels, eco-friendly infrastructure, sustainable materials, living walls, cutting-edge technology, smart city infrastructure, IoT integration, holographic displays, connected systems, advanced robotics, 5G networks, innovative design, futuristic Mediterranean city, cinematic lighting, ultra detailed, high resolution, 4k, award-winning photography, professional quality, warm sunlight, architectural marvel"
    },
    
    {
        "input": "Des transports solaires",
        "keywords_detected": ["transports", "solaires"],
        "categories": ["Transport & Mobility", "Energy & Renewable"],
        "output": "Des transports solaires, futuristic transportation system, autonomous vehicles, smart mobility, solar-powered transit, modern trams, intelligent traffic, pedestrian-friendly streets, cycling infrastructure, high-speed rail, renewable energy infrastructure, solar architecture, wind turbines, geothermal systems, energy-efficient buildings, clean power generation, carbon-neutral, futuristic Mediterranean city, cinematic lighting, ultra detailed, high resolution, 4k, award-winning photography, professional quality, warm sunlight, architectural marvel"
    },
]

BENEFITS = [
    "✅ Contextually relevant prompts",
    "✅ Better image generation quality",
    "✅ Supports French and English keywords",
    "✅ Multiple keyword detection per prompt",
    "✅ Extensible keyword library",
    "✅ Maintains SFW filtering",
    "✅ Base style consistency"
]

HOW_IT_WORKS = """
1. User speaks: "Marseille écologique en 2050"
2. Whisper transcribes to text
3. prompt_utils.clean_transcription() - cleans text
4. prompt_utils.is_prompt_safe() - validates SFW
5. prompt_utils.enrich_with_keywords() - DETECTS:
   - "écologique" → Ecology & Environment keywords
   - "2050" → Year 2050 / Futuristic keywords
   - "Marseille" → Mediterranean context keywords
6. Each detected category adds its enhancement
7. All added + Base Style = Final Prompt
8. GPU receives enriched, contextualized prompt
"""

ADDING_NEW_KEYWORDS = """
To add new keyword category to KEYWORD_ENHANCEMENTS:

1. Edit backend/prompt_utils.py
2. Find KEYWORD_ENHANCEMENTS dictionary
3. Add new tuple entry:

    ("keyword1", "keyword2", "keyword3"):
        ", enhancement text here, more keywords, etc",

4. Test with:
    python prompt_utils.py

5. Commit changes
"""

CURRENT_KEYWORDS = [
    "French & English ecology/sustainability",
    "Transport & mobility (French & English)",
    "Water & maritime features",
    "Technology & innovation",
    "Future year 2050 context",
    "Cultural & heritage aspects",
    "Tourism & recreation",
    "Quality of life",
    "Business & economy",
    "Energy & renewable sources",
    "Architecture & design",
    "Nature & parks",
    "Mediterranean context",
    "Residential & housing",
    "Public spaces & gathering"
]
