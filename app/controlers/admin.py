from fastapi import HTTPException
from app.schemas.admin import LogInAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User, UserRole
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload
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
    
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

async def getusers(
    db: AsyncSession,
    start: int,
    end: int
):
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.portal))  # Eager-load UserPortal
            .where(User.role == UserRole.student)
            .limit(end - start + 1)
            .offset(start - 1)
        )

        users = result.scalars().all()

        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(User).where(User.role == UserRole.student)
        )
        count = count_result.scalar()

        # Format response with only portal_id from portal
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "name": user.name,
                "role": user.role.value,
                "status": user.status.value,
                "portal_id": user.portal.portal_id if user.portal else None
            })

        return {
            'count': count,
            'users': users_data
        }

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to search for users")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
   
        
