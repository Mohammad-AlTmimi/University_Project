from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
from typing import Optional

class MessagePayload(BaseModel):
    chat_id: str
    message: str

class getMessagePayload(BaseModel):
    user_id: str
    start: int
    end: int
    
from pydantic import BaseModel, Field, ValidationError, model_validator

class GetMessagePayload(BaseModel):
    user_id: str
    start: int
    end: int

    @model_validator(mode="after")
    def check_range(cls, values):
        start, end = values.start, values.end
        if (end - start) >= 10:
            raise ValueError("The difference between start and end must be less than 10")
        return values
