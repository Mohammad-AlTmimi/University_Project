import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone


class UserPortal(Base):
    __tablename__ = 'user_portal'
    
    id = Column(String , primary_key=True , default=lambda: str(uuid.uuid4()))
    portal_id = Column(String, unique=True, nullable=False)
    portal_password = Column(String, nullable=False)
    user_id = Column(String , ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    user = relationship('User', back_populates='portal')
    