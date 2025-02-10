from app.database import Base  # Import Base only

# Import all models to ensure they are registered properly
from app.models.user import User
from app.models.chat import Chat
from app.models.user_portal import UserPortal
