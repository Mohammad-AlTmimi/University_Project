from fastapi import APIRouter, Depends, HTTPException, status
from app.middlewares.auth import authenticate
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.schemas.user import UserCreate
from app.controlers.user import createToken
from app.nodatabase import get_nodb
from app.scripts import classify_question
router = APIRouter()

@router.post('/addmessage')
async def addMessage(
    payload: dict, 
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db),
    nodb: dict = Depends(get_nodb),
):
    
    user_id = user.get("user_id")  # Extract user_id from decoded token payload
    result = await db.execute(
        text('''
            SELECT * 
            FROM users
            WHERE id = :user_id
        '''),
        {"user_id": user_id}
    )
    user_record = result.fetchone()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    chat_message = {
        "user_id" : "payload['user_id']",
        'message' : "payload['message']",
        'type' : classify_question("payload['message']")
    }
    chat_collection = nodb["chats"]
    
    result = chat_collection.insert_one(chat_message)

    if result.inserted_id:
        return {"message": "Chat added successfully", "chat_id": str(result.inserted_id) , 'TYPE': chat_message['type']}
    else:
        raise HTTPException(status_code=500, detail="Failed to add chat")
    


    

