from pydantic import BaseModel
from typing import List, Dict

class MessageResponse(BaseModel):
    messages: List[Dict[str , str]]
    portal_id: str
    user_id: str
    messageType: str


class PortalPayload(BaseModel):
    portal_id: str 
    user_id: str