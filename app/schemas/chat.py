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
    start: int
    end: int

    @model_validator(mode="after")
    def check_range(cls, values):
        start, end = values.start, values.end
        if (end - start) >= 10:
            raise ValueError("The difference between start and end must be less than 10")
        return values
    
class GetOneChat(BaseModel):
    user_id: str
    chat_id: str

    