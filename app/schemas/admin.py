from pydantic import BaseModel
from typing import List, Dict

class LogInAdmin(BaseModel):
    portal_id: str
    password: str