from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncio
from sqlalchemy.sql import text
# Define Base here (Option One)
Base = declarative_base()

# Database connection URL
DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/testproject"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Create tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for getting a database session."""
    async with SessionLocal() as session:
            yield session
#delete me in deployment plesase :)
async def delete_table():
    async with engine.begin() as conn: 
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE user_portal CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE users CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE chats CASCADE")))

