import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from app.database import Base
from sqlalchemy.orm import relationship

class userstatus(PyEnum):
    active = 'active'
    inactive = 'inactive'
    deactive = 'deactive'
    pending = 'pending'

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(8), primary_key=True, index=True, default=lambda: str(uuid.uuid4())[:8])
    user_id = Column(String(8), index=True , unique=True)
    username = Column(String)
    profile_image = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(userstatus), nullable=False)
    email = Column(String(28))

    # Define the relationship with chatSession
    sessions = relationship('ChatSession', back_populates='user', cascade='all, delete-orphan')
    def __init__(self, username, status=userstatus.pending, profile_image=None, email=None, user_id=None):
        
        self.username = username
        self.status = status
        self.profile_image = profile_image
        self.email = email
        self.user_id = user_id
