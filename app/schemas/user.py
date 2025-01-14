from pydantic import BaseModel, field_validator, model_validator, root_validator
from enum import Enum
from typing import Optional

class userstatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    deactive = 'deactive'
    pending = 'pending'

# Pydantic schema for user creation
class UserCreate(BaseModel):
    username: str
    profile_image: Optional[str] = None  # Optional field for profile image
    status: userstatus = userstatus.active  # Default status as pending
    user_id: str
    email: str
    password: str

    
    @field_validator("email")
    def validateEmail(cls, value: str):
        # Ensure the email ends with "@students.hebron.edu" and has a length of 28 characters
        if not value.endswith("@students.hebron.edu") or len(value) != 28:
            raise ValueError("Email must belong to '@students.hebron.edu' domain and have a length of 28 characters.")

        # Check that the second and third characters are '2' or greater lexicographically
        if not (value[1] >= '2' and value[2] >= '2'):
            raise ValueError("Email must have '2' or greater at the second and third positions after the '@'.")
        return value

    class Config:
        # Use UUID for ID generation
        from_attributes = True


class UserRequest(BaseModel):
    id: str
    username: str

# Pydantic schema for user response
class UserResponse(BaseModel):
    id: str
    username: str
    profile_image: Optional[str] = None
    status: userstatus

    class Config:
        from_attributes = True 