from pydantic import BaseModel, field_validator, EmailStr, validator
from enum import Enum
from typing import Optional

class UserStatus(str, Enum):
    active = 'Active'
    inactive = 'Inactive'
    deactive = 'Deactive'
    pending = 'Pending'

# Pydantic schema for user creation
class UserCreate(BaseModel):
    username: str
    profile_image: Optional[str] = None  # Optional field for profile image
    status: UserStatus = UserStatus.pending # Default status as pending
    email: str
    @field_validator("username")
    def validateId(cls, value: str):
        if len(value) != 8 or not(value[1] >= 2 and value[2] >= 2):
            raise ValueError('User Id not Accepted')
        return value
    @field_validator("email")
    def validateEmail(cls, value: EmailStr):
        if not value.endswith("@students.hebron.edu") or len(value) != 28:
            raise ValueError("Email must belong to '@students.hebron.edu' domain.")
        return value
    class Config:
        # Use UUID for ID generation
        from_attributes = True

class UserRequest(BaseModel):
    id: str
    username: str

# Pydantic schema for user response
class UserResponse(BaseModel):
    id: str  # id will be a string of 8 characters
    username: str
    profile_image: Optional[str] = None
    status: UserStatus

    class Config:
        from_attributes = True  # Tells Pydantic to convert SQLAlchemy models to Pydantic models
