from pydantic import BaseModel
from enum import Enum
from typing import Optional
import uuid

class UserStatus(str, Enum):
    active = 'Active'
    inactive = 'Inactive'
    deactive = 'Deactive'
    pending = 'Pending'

# Pydantic schema for user creation
class UserCreate(BaseModel):
    username: str
    profile_image: Optional[str] = None  # Optional field for profile image
    status: UserStatus = UserStatus.pending  # Default status as pending

    class Config:
        # Use UUID for ID generation
        orm_mode = True

# Pydantic schema for user response
class UserResponse(BaseModel):
    id: str  # id will be a string of 8 characters
    username: str
    profile_image: Optional[str] = None
    status: UserStatus

    class Config:
        orm_mode = True  # Tells Pydantic to convert SQLAlchemy models to Pydantic models
