from app.schemas.user import UserCreate
from fastapi import Depends, HTTPException
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


from sqlalchemy.exc import SQLAlchemyError

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
