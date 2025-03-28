from pydantic import Field, BaseModel

class createUser(BaseModel):
    portal_id: str
    portal_password: str
    password: str
    name: str = None
    
class loginUser(BaseModel):
    password: str
    portal_id: str
    
class ForgetPasswordRequest(BaseModel):
    portal_id: str
    portal_password: str
    
class ResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=128, description="New password for the user")
class ChangePasswordRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=128, description="New password for the user")
    old_password: str
    