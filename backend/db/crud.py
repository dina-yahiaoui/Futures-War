from sqlalchemy.orm import Session
from .models import Generation

def create_generation(db: Session, prompt: str, image_path: str):
    gen = Generation(prompt=prompt, image_path=image_path)
    db.add(gen)
    db.commit()
    db.refresh(gen)
    return gen