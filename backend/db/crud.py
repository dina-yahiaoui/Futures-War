from sqlalchemy.orm import Session
from .models import Generation

def create_generation(db: Session, prompt: str, image_path: str, is_sfw: bool = True, flagged_reason: str = None):
    gen = Generation(
        prompt=prompt, 
        image_path=image_path,
        is_sfw=is_sfw,
        flagged_reason=flagged_reason
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)
    return gen