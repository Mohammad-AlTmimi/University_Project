from pydantic import Field, BaseModel

class createUser(BaseModel):
    portal_id: str
    portal_password: str
    password: str
    name: str = None
    
class loginUser(BaseModel):
    password: str
    portal_id: str