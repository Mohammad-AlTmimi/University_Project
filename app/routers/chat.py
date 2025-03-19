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
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
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
        oneChat = GetMessages(
            user_id=user_id,
            chat_id=chat_id,
            start= chat_record.chat_number - 6,
            end= chat_record.chat_number
        )
        messages_records = await PageMessages(oneChat, nodb) if payload.chat_id != 'newchat' else []

        messages = []
        for elm in messages_records:
            if payload.chat_id == 'newchat':
                break
            if elm.type != 'response': 
                messages.append({'role': 'user', 'content': elm.message})
            else:  
                messages.append({'role': 'assistant', 'content': elm.template + '\n' + elm.message})
        
        messages.append({"role": "user", "content": message_text})
        
        print(messages)
        aiPayload = MessageResponse(
            messages=messages,
            type=message_type
        )
        AIMessage = await AIResponse(aiPayload)
        print(AIMessage)
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
            'template': ''
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


@router.get('/messages')
async def getmessages(
    user: dict = Depends(authenticate),
    start: int = Query(1, alias="start"),   # Oldest chat requested
    end: int = Query(10, alias="end"), # Newest chat requested
    chat_id: str = Query(alias="chat_id"),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    try:
        user_id = user.get('user_id')
        oneChat = GetMessages(
            user_id=user_id,
            chat_id=chat_id,
            start= start,
            end= end
        )
        messages_records = await PageMessages(oneChat , nodb)
        if not messages_records:
            raise HTTPException(status_code=500, detail="Failed to insert response message into MongoDB")
        return {
            'Token': user.get('Token'),
            'messages': messages_records
        }
    except HTTPException as http_exc:
        raise http_exc  # Re-raise known HTTP exceptions to maintain status codes
    