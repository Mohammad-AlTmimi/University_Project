from __future__ import annotations
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.database import Base
from datetime import datetime

class UserPortal(Base):
    __tablename__ = 'user_portal'
    
    id = Column(String , primary_key=True , default=lambda: str(uuid.uuid4()))
    portal_id = Column(String, unique=True, nullable=False)
    portal_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="portal")
