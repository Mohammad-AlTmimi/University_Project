import uuid
from enum import Enum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from app.database import Base
from sqlalchemy.orm import relationship

class UserStatus(Enum):
    active = 'Active'
    inactive = 'Inactive'
    deactive = 'Deactiev'
    pending = 'Pending'

class User(Base):
    __tablename__ = 'users'
    id = Column(String(8), primary_key=True, index=True)
    username = Column(String, index=True)
    profile_image = Column(String)
    status = Column(SQLAlchemyEnum(UserStatus), default=UserStatus.pending)

    # Define the relationship with chatSession
    sessions = relationship('chatSession', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, id, username, status=UserStatus.pending, profile_image=None):
        self.id = id
        self.username = username
        self.status = status
        self.profile_image = profile_image
