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
    
class GeneralQuestionTemplate(BaseModel):
    portal_id: str
    user_id: str
    question: str
    
class SearchQuery(BaseModel):
    query: str
    search_type: str = "text" 