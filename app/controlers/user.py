from app.schemas.user import UserCreate
from fastapi import Depends, HTTPException
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
import jwt
import datetime
import os

from sqlalchemy.exc import SQLAlchemyError
def createToken(user_id , user_key):
    SECRET_KEY = os.getenv('jwtToken')
    payload = {
        "user_id": user_id,
        "user_key": user_key,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


async def createUser(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        newUser = User(**user.model_dump())
        db.add(newUser)
        await db.commit()
        await db.refresh(newUser)
        return newUser
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
