from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


Base = declarative_base()


DATABASE_URL = ''
sync_engine = ''

SYNC_DATABASE_URL = os.getenv('SYNC_URL_DATABASE')
if os.environ.get('RELOAD_MODE') == 'true':
    DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/testproject"
else :
    DATABASE_URL = os.getenv('ASYNC_URL_INSTANCE')
    sync_engine = create_engine(SYNC_DATABASE_URL)

# Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
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
    await create_async_database()  
    await init_db()  
    yield
