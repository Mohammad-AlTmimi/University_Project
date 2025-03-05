import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from app.middlewares.auth import authenticate
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.controlers.user import createToken
from app.nodatabase import get_nodb
from app.ml_models.sbertmodel import classify_question
from app.controlers.chat import creatChat, getChats, updateLastInteractoin,getChat
from app.controlers.message import PageMessages
from datetime import datetime, timezone
from app.schemas.chat import MessagePayload
from app.models.chat import Chat
from app.schemas.chat import GetChatsPayload, GetOneChat, GetMessages
from app.controlers.ai import AIResponse
from app.schemas.ai import MessageResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post('/addmessage')
async def addMessage(
    payload: MessagePayload,  # Use Pydantic model
    db: AsyncSession = Depends(get_db),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    try:
        user_id = 'Guest'
        message_text = payload.message
        message_type = await classify_question(message_text)
        chat_id = 'Guest'

        aiPayload = MessageResponse(
            messages=[{"role": "user", "content": message_text}],
            type=message_type
        )
        AIMessage = await AIResponse(aiPayload)

        chat_message = {
            "user_id": user_id,
            "message": message_text,
            "type": message_type,
            "chat_id": chat_id,
            "create_time": datetime.now(timezone.utc).replace(tzinfo=None),
        }

        response_message = {
            'user_id': user_id,
            'message': AIMessage,  # Correctly access the first message
            'type': 'response',
            'chat_id': chat_id,
            'create_time': datetime.now(timezone.utc).replace(tzinfo=None),
        }   

        # Insert chat message to MongoDB
        chat_collection = nodb["messages"]
        result = await chat_collection.insert_one(chat_message)
        response_result = await chat_collection.insert_one(response_message)
        
        if not result.inserted_id or not response_result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert messages into MongoDB")

        # Update last interaction in SQLAlchemy
        await updateLastInteractoin(chat_id=chat_id , db=db)
        

        # Return success response
        return {
            "message": "Chat added successfully", 
            "message_id": str(result.inserted_id),
            'chat_id': chat_id,
            "TYPE": message_type,
            "AI Response": AIMessage
        }

    except HTTPException as http_exc:
        raise http_exc  # Re-raise known HTTP exceptions to maintain status codes

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: {str(e)}")


