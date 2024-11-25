from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatSessionBase(BaseModel):
    id: Optional[str] = Field(None, title="Session ID", description="Unique identifier for the chat session")
    user_id: str = Field(..., title="User ID", description="Identifier for the user associated with the chat session")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, title="Timestamp", description="Timestamp of the chat session creation")

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy models


class ChatSessionCreate(BaseModel):
    user_id: str = Field(..., title="User ID", description="Identifier for the user associated with the chat session")


class ChatSessionResponse(ChatSessionBase):
    id: str = Field(..., title="Session ID", description="Unique identifier for the chat session")
