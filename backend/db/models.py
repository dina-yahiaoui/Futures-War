from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .database import Base

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    is_sfw = Column(Boolean, default=True)
    flagged_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)