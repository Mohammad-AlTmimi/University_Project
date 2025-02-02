import jwt
import datetime
import os
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text
from passlib.context import CryptContext
from app.schemas.user import createUser
from app.models.user import User
from app.database import get_db
from app.models import User , UserPortal

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


async def createUser(user: createUser, db: AsyncSession = Depends(get_db)):
    try:
        # Create a new User object
        newUser = User(password_hash=user.password)

        # Add user to the session
        db.add(newUser)
        await db.commit() 
        await db.refresh(newUser)  

        # Create a UserPortal object and associate it with the new user
        portal = UserPortal(
            portal_id=user.portal_id, 
            portal_password=user.portal_password, 
            user_id=newUser.id
        )

        # Add user portal to the session
        db.add(portal)
        await db.commit()  # Commit changes for portal as well
        await db.refresh(portal)  # Refresh portal to get any generated values

        return {"user_id": newUser.id, "portal_id": portal.id}  # Return the created user and portal IDs

    except IntegrityError:
        # Rollback on error
        await db.rollback()
        raise ValueError("User or UserPortal already exists with the provided details.")



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
