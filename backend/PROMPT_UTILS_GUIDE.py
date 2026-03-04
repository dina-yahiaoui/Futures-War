"""
Quick reference guide for using prompt_utils module
"""

from prompt_utils import build_final_prompt
import json

# Example 1: Valid SFW prompt
print("=" * 80)
print("EXAMPLE 1: Valid SFW prompt")
print("=" * 80)
result = build_final_prompt("Marseille with more green spaces and solar transport")
print(json.dumps(result, indent=2))

# Example 2: Blocked prompt (contains forbidden word)
print("\n" + "=" * 80)
print("EXAMPLE 2: Blocked prompt (contains 'nude')")
print("=" * 80)
result = build_final_prompt("nude beaches of Marseille")
print(json.dumps(result, indent=2))

# Example 3: French prompt
print("\n" + "=" * 80)
print("EXAMPLE 3: French prompt with cleanup")
print("=" * 80)
result = build_final_prompt("Euh, Marseille écologique avec euh plus d'arbres")
print(json.dumps(result, indent=2))

# Example 4: How to use in app.py
print("\n" + "=" * 80)
print("HOW TO USE IN app.py")
print("=" * 80)
print("""
from prompt_utils import build_final_prompt

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json() or {}
    prompt_input = data.get("prompt", "")
    
    # Build and validate prompt with SFW filtering
    prompt_result = build_final_prompt(prompt_input)
    
    # Check if prompt passed SFW validation
    if not prompt_result["success"]:
        return jsonify({"error": prompt_result["error"]}), 400
    
    # Extract final prompt and negative prompt
    final_prompt = prompt_result["positive_prompt"]
    negative_prompt = prompt_result["negative_prompt"]
    
    # Call GPU with clean prompt
    image = gpu_client.generate(final_prompt, negative_prompt)
    
    # Save to database with SFW tracking
    db.create_generation(
        prompt=final_prompt,
        image_path=image,
        is_sfw=True,
        flagged_reason=None
    )
    
    return jsonify({"success": True, "image": image})
""")

print("\n" + "=" * 80)
print("OUTPUT SCHEMA")
print("=" * 80)
print("""
{
  "success": bool,              # True if prompt is SFW and valid
  "error": str | null,          # Error message if blocked, null if success
  "original_text": str,         # Raw user input
  "cleaned_text": str,          # After cleanup (filler words removed, etc)
  "positive_prompt": str,       # Final enriched prompt (send to GPU)
  "negative_prompt": str        # What NOT to generate (send to GPU)
}
""")
