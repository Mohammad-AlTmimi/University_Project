import jwt
import datetime
import os
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from passlib.context import CryptContext
from app.schemas.user import UserCreate
from app.models.user import User
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def createToken(user_id, user_key):
    SECRET_KEY = os.getenv('jwtToken')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables.")
    payload = {
        "user_id": user_id,
        "user_key": user_key,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


async def createUser(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        
        password_hash = pwd_context.hash(user.password)

        newUser = User(
                user_id=user.user_id,
                username=user.username,
                profile_image=user.profile_image,
                status=user.status,
                email=user.user_id + '@students.hebron.edu',
                password_hash=password_hash  # Store the hashed password
            )
        print("eeeeeeeeeeeee")

        db.add(newUser)
        print('eeeeeeeee')
        await db.commit()
        print('seesefe')

        await db.refresh(newUser)
        print('seesefe')

        return newUser
    except SQLAlchemyError as e:
        print(e)
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create user")


async def searchUser(payload: dict, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.get(User, payload['user_id'])
        if user and pwd_context.verify(payload['user_password'], user.password):
            return {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                },
                "token": createToken(user.id, user.user_key)
            }
        else:
            raise HTTPException(status_code=404, detail="Invalid credentials")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to search for user")
