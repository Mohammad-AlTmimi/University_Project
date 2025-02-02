from pydantic import Field, BaseModel

class createUser(BaseModel):
    portal_id: str
    portal_password: str
    password: str