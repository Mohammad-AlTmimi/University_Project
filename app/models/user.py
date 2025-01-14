import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from passlib.context import CryptContext

# Initialize the password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserStatus(PyEnum):
    active = 'active'
    inactive = 'inactive'
    deactive = 'deactive'
    pending = 'pending'

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4())[:8])
    user_id = Column(String(8), index=True, unique=True)
    username = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(UserStatus), nullable=False, default=UserStatus.pending)
    email = Column(String(28), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)  # Store the hashed password in password_hash

    # Define the relationship with ChatSession
    sessions = relationship('ChatSession', back_populates='user', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, raw_password):
        # Hash the password and store it in the password_hash column
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password):
        # Verify the given raw password against the hashed password
        return pwd_context.verify(raw_password, self.password_hash)
