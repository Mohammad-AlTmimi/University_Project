import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Chat(Base):
    __tablename__ = 'chat'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_interaction = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to User
    user = relationship('User', back_populates='chats')

    def update_last_interaction(self):
        """Updates the last interaction timestamp."""
        self.last_interaction = datetime.now(timezone.utc)
