from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from datetime import datetime
from typing import Optional

class MessagePayload(BaseModel):
    chat_id: str
    message: str

class createMessage(BaseModel):
    user_id: str
    chat_id: str

    
class GetChatsPayload(BaseModel):
    user_id: str

    
class GetOneChat(BaseModel):
    user_id: str
    chat_id: str
    
    
class GetMessages(BaseModel):
    user_id: str
    chat_id: str
    start: int
    end: int


    