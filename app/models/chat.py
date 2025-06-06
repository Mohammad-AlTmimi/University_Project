import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_number = Column(Integer, nullable = False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    messages_number = Column(Integer, nullable = False, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    title = Column(String)
    last_interaction = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    user = relationship('User', back_populates='chats')

    def update_last_interaction(self):
        self.last_interaction = datetime.now(timezone.utc).replace(tzinfo=None) # Remove tzinfo to match `TIMESTAMP WITHOUT TIME ZONE`
    def update_messages_number(self):
        self.messages_number = self.messages_number + 2
