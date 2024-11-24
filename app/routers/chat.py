from fastapi import APIRouter , Depends
from authenticate import authenticate , createToken
router = APIRouter()

@router.post('/addChat')
async def addChat(payload: dict, user: dict = Depends(authenticate)):
    user_id = user.get("user_id")
    
    

