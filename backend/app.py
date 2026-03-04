from flask import Flask, request, jsonify
from db.database import Base, engine, SessionLocal
from db import crud
from prompt_utils import build_final_prompt

app = Flask(__name__)

# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json() or {}
    prompt_input = data.get("prompt", "")
    
    # Build and validate prompt with SFW filtering
    prompt_result = build_final_prompt(prompt_input)
    
    db = next(get_db())
    
    # Check if prompt passed SFW validation
    if not prompt_result["success"]:
        # Log the blocked attempt
        gen = crud.create_generation(
            db, 
            prompt=prompt_input,
            image_path="",
            is_sfw=False,
            flagged_reason=prompt_result["error"]
        )
        return jsonify({
            "error": prompt_result["error"],
            "id": gen.id
        }), 400
    
    # Extract final prompt and negative prompt
    final_prompt = prompt_result["positive_prompt"]
    negative_prompt = prompt_result["negative_prompt"]
    
    # TODO: Call GPU via gpu_client.py with final_prompt and negative_prompt
    # For now simulating:
    image_path = "images/fake_image.png"
    
    # Save to database with SFW=True
    gen = crud.create_generation(
        db, 
        prompt=final_prompt, 
        image_path=image_path,
        is_sfw=True,
        flagged_reason=None
    )
    
    return jsonify({
        "id": gen.id,
        "prompt": gen.prompt,
        "original_prompt": prompt_result["original_text"],
        "cleaned_prompt": prompt_result["cleaned_text"],
        "image_path": gen.image_path,
        "is_sfw": gen.is_sfw,
        "created_at": gen.created_at.isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)