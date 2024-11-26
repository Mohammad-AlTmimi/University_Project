import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class ChatSession(Base):
    __tablename__ = 'chatSessions'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(8), ForeignKey('users.id'), nullable=False)  # Match length with User ID
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship to User (Make sure the 'sessions' field is in the User model)
    user = relationship('User', back_populates='sessions')

    def __init__(self, user_id):
        self.user_id = user_id
