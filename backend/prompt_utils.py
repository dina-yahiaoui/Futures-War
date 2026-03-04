"""
Prompt Engineering Module - Futures-War Project

Transforms raw Whisper transcription into optimized AI image generation prompt
with Safe For Work filtering and Marseille context enrichment.

Pipeline: Raw Text → Clean → Validate (SFW) → Enrich → JSON Output
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
# STEP 3: ENRICHMENT (STATIC FOR V1)
# ============================================================================

def enrich_prompt(text: str) -> str:
    """
    Enrich user text with Marseille context and style.
    
    V1: Static enrichment - just add base style
    V2 (TODO): Dynamic enrichment based on keywords
        - if "écologique" → add green/sustainable keywords
        - if "transport" → add mobility keywords
        - if "2050" → add futuristic keywords
    
    Args:
        text: Cleaned user prompt
        
    Returns:
        Enriched prompt ready for image generation
    """
    if not text:
        return BASE_STYLE
    
    # V1: Simple concatenation with base style
    enriched = f"{text}, {BASE_STYLE}"
    
    # TODO V2: Dynamic keyword expansion
    # Example:
    # if "transport" in text.lower():
    #     enriched += ", futuristic mobility, smart transportation system"
    # if "vert" in text.lower() or "écolog" in text.lower():
    #     enriched += ", lush vegetation, rooftop gardens, urban forest"
    
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
    3. Enrich with context
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
    
    # Step 3: Enrich
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
        "Des transports solaires",
        "nude Marseille",  # Should fail SFW
        "violence at the beach",  # Should fail SFW
    ]
    
    print("=" * 80)
    print("PROMPT BUILDER TEST")
    print("=" * 80)
    
    for test_input in test_cases:
        print(f"\n📝 Input: {test_input}")
        result = build_final_prompt(test_input)
        
        if result["success"]:
            print(f"✅ SUCCESS")
            print(f"   Cleaned: {result['cleaned_text']}")
            print(f"   Prompt: {result['positive_prompt'][:100]}...")
        else:
            print(f"❌ BLOCKED: {result['error']}")
        print()


if __name__ == "__main__":
    test_prompt_builder()
