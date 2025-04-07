from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import os

# Define Base
Base = declarative_base()
print('-'*100)
print(os.getenv('SYNC_URL_DATABASE'))

# Database connection URL (async)
DATABASE_URL = os.getenv('ASYNC_URL_INSTANCE')

# Sync connection URL for database creation
SYNC_DATABASE_URL = os.getenv('SYNC_URL_DATABASE')

# Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Sync Engine
sync_engine = create_engine(SYNC_DATABASE_URL)

# Session setup
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Ensure database exists (sync)
if not database_exists(sync_engine.url):
    create_database(sync_engine.url)
    print("Database created!")
else:
    print("Database already exists.")

async def init_db():
    """Create tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for getting a database session."""
    async with SessionLocal() as session:
        yield session

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

# Create database asynchronously if it does not exist
async def create_async_database():
    if not await database_exists(engine.url):
        await create_database(engine.url)
        print("Async Database created!")
    else:
        print("Async Database already exists!")

async def lifespan(app):
    await create_async_database()  # Ensure async database is created
    await init_db()  # Run database initialization
    yield
