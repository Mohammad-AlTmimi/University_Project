import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from passlib.context import CryptContext

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserStatus(PyEnum):
    active = 'active'
    inactive = 'inactive'
    suspended = 'suspended'  # Fixed inconsistent casing

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    profile_image = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(UserStatus), nullable=False, default=UserStatus.active)
    password_hash = Column(String, nullable=False)  # Store hashed password

    # Define relationship with Chat
    sessions = relationship('Chat', back_populates='user', cascade='all, delete-orphan')
    # Define relationship with user_portal
    portal = relationship('UserPortal', back_populates='user', uselist=False, cascade='all, delete-orphan')
    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password):
        """Verifies the given raw password against the stored hash."""
        return pwd_context.verify(raw_password, self.password_hash)
