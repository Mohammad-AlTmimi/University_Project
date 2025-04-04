from fastapi import HTTPException
from app.schemas.admin import LogInAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.admin import Admin
from sqlalchemy import and_
import jwt
import datetime
import os
from passlib.context import CryptContext

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
        'user_id': f"{admin_id} {expiration_timestamp_ms}",
        'portal_id': f"{portal_id} {expiration_timestamp_ms}",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
        
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token