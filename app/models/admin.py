from sqlalchemy import Column, String, Enum as SQLAlchemyEnum, ForeignKey ,DateTime
from app.database import Base
import uuid
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Admin(Base):
    __tablename__= 'admins'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portal_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    
    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password):
        """Verifies the given raw password against the stored hash."""
        return pwd_context.verify(raw_password, self.password_hash)

