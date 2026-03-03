from flask import Flask, request, jsonify
from db.database import Base, engine, SessionLocal
from db import crud

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
    prompt = data.get("prompt", "")

    # TODO : ici tu appelles ton GPU via gpu_client.py
    # pour l'instant on simule :
    image_path = "images/fake_image.png"

    # Sauvegarde en base
    db = next(get_db())
    gen = crud.create_generation(db, prompt=prompt, image_path=image_path)

    return jsonify({
        "id": gen.id,
        "prompt": gen.prompt,
        "image_path": gen.image_path,
        "created_at": gen.created_at.isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)