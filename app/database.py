from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

Base = declarative_base()

SYNC_DATABASE_URL = os.getenv('SYNC_URL_DATABASE')
ASYNC_DATABASE_URL = os.getenv('ASYNC_URL_INSTANCE')


sync_engine = create_engine(SYNC_DATABASE_URL)
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE user_portal CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE users CASCADE")))
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("DROP TABLE chats CASCADE")))

def create_database_if_not_exists():
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)

async def create_async_database():
    create_database_if_not_exists()
    return engine

async def lifespan(app):
    await create_async_database()
    await init_db()
    yield