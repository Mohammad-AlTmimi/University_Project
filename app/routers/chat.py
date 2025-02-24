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
from datetime import datetime, timezone
from app.schemas.chat import MessagePayload
from app.models.chat import Chat
from app.schemas.chat import GetChatsPayload, GetOneChat
from app.controlers.ai import AIResponse
from app.schemas.ai import MessageResponse

router = APIRouter()

@router.post('/addmessage')
async def addMessage(
    payload: MessagePayload,  # Use Pydantic model
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db),
    nodb: dict = Depends(get_nodb),
):
    try:
        user_id = user.get("user_id")

        # Fetch user
        resultUser = await db.execute(
            text('SELECT * FROM users WHERE id = :user_id'), 
            {"user_id": user_id}
        )
        user_record = resultUser.fetchone()

        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")

        # Correct payload attribute access
        chat_record = None
        if payload.chat_id == "newchat":
            chat_record = await creatChat(user_id , db)
        else:
            oneChat = GetOneChat(
                user_id=user_id,
                chat_id=payload.chat_id
            )
            chat_record = await getChat(oneChat , db)

        if not chat_record:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Correct payload attribute access
        message_text = payload.message
        message_type = await classify_question(message_text)
        chat_id = chat_record.id

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
            "create_time": datetime.now(timezone.utc).replace(tzinfo=None)
        }

        response_message = {
            'user_id': user_id,
            'message': AIMessage,  # Correctly access the first message
            'type': 'response',
            'chat_id': chat_id,
            'create_time': datetime.now(timezone.utc).replace(tzinfo=None)
        }

        # Insert chat message to MongoDB
        chat_collection = nodb["chats"]
        result = chat_collection.insert_one(chat_message)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert chat message into MongoDB")

        # Insert response message to MongoDB
        response_result = chat_collection.insert_one(response_message)
        if not response_result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert response message into MongoDB")

        # Update last interaction in SQLAlchemy
        await updateLastInteractoin(chat_id=chat_id , db=db)

        # Return success response
        return {
            "message": "Chat added successfully", 
            "message_id": str(result.inserted_id),
            'chat_id': chat_id,
            "TYPE": message_type,
            "AI Response": AIMessage,
            "Token": user.get('Token')
        }

    except HTTPException as http_exc:
        raise http_exc  # Re-raise known HTTP exceptions to maintain status codes

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: {str(e)}")


   
@router.get("/chats/")
async def get_chats(
    user: dict = Depends(authenticate),
    start: int = Query(1, alias="start"),   # Oldest chat requested
    end: int = Query(10, alias="end"),      # Newest chat requested
    db: AsyncSession = Depends(get_db)
    
):
    try:
        payload = GetChatsPayload(
            user_id = user.get("user_id"),
            start=start,
            end=end
        )

        chats = await getChats(payload, db)

        if not chats:
            raise HTTPException(status_code=404, detail="No chats found in this range")
        return {
                'Chats': chats,
                'Token': user.get('Token')
            }
    except HTTPException as http_exc:
        raise http_exc  # Re-raise known HTTP exceptions to maintain status codes

    except Exception as e:
        return HTTPException(status_code=401 , detail=e)