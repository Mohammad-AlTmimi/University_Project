from fastapi import HTTPException
from app.schemas.admin import LogInAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.admin import Admin
from sqlalchemy import and_
import jwt
import datetime
from passlib.context import CryptContext
from dotenv import load_dotenv, set_key, dotenv_values
import os
import asyncio

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def SearchAdmin(payload: LogInAdmin, db: AsyncSession):
    try:
        result = await db.execute(
            select(Admin).where(
                payload.portal_id == Admin.portal_id
            )
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            raise HTTPException(status_code=404, detail='No User Found')
        if not admin.verify_password(payload.password):
            raise HTTPException(status_code=404, detail='Wrong Password')
        return admin
    except Exception as e:
        raise e
    
def createToken(admin_id, portal_id):
    SECRET_KEY = os.getenv('jwtTokenAdmin')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables.")
    
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    expiration_timestamp_ms = int(expiration_time.timestamp() * 1000)

    payload = {
        'admin_id': f"{admin_id} {expiration_timestamp_ms}",
        'portal_id': f"{portal_id} {expiration_timestamp_ms}",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
        
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

async def update_env_file(key: str, value: str):
    env_file_path = env_path
    try:
        async with asyncio.Lock():
            env_vars = dotenv_values(env_file_path)
            
            env_vars[key] = value
            
            set_key(env_file_path, key, value)
            

    except Exception as e:
        raise Exception(f"Failed to update .env file: {str(e)}")