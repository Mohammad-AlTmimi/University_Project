from pydantic import BaseModel
from typing import List, Dict, Literal

class LogInAdmin(BaseModel):
    portal_id: str
    password: str
    
class ToggleRequest(BaseModel):
    action: Literal["start", "stop"]