from fastapi import APIRouter , Depends
from app.middlewares.auth import authenticate, createToken
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.user import UserCreate
router = APIRouter()

@router.post('/addChat')
async def addChat(payload: dict, user: dict = Depends(authenticate), db: AsyncSession = Depends(get_db)):
    user_id = user.get("user_id")
    result = await db.execute(
        '''
        SELECT * 
        FROM users
        WHERE id = :user_id
        ''',
        {"user_id": user_id}
    )
    user_record = result.fetchone()
    
    

