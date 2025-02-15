from __future__ import annotations
import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import Session
from sqlalchemy import event
from app.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserStatus(PyEnum):
    active = 'active'
    inactive = 'inactive'
    suspended = 'suspended'

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    profile_image = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(UserStatus), nullable=False, default=UserStatus.active)
    password_hash = Column(String, nullable=False)
    portal_id = Column(String , ForeignKey('user_portal.id'), nullable=False)


    # One-to-one relationship with UserPortal
    portal: Mapped["UserPortal"] = relationship("UserPortal", back_populates="user", uselist=False, cascade="all, delete")

    # One-to-many relationship with Chat (sessions)
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password):
        """Verifies the given raw password against the stored hash."""
        return pwd_context.verify(raw_password, self.password_hash)

