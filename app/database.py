from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Update the DATABASE_URL to use asyncpg driver
DATABASE_URL = "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"

# Create the asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session local factory that will use AsyncSession
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session
