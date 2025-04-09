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
from fastapi.responses import StreamingResponse
import json
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
            start= max(1 , chat_record.messages_number - 6),
            end= chat_record.messages_number
        )
        messages_records = await PageMessages(oneChat, nodb) if payload.chat_id != 'newchat' else []
        messages = []
        print(chat_record.messages_number , messages_records)
        if payload.chat_id != 'newchat':  
            for elm in messages_records:                
                if elm.get('type' , '') != 'question':  
                    messages.append({'role': 'user', 'content': elm.get('message', '') , 'type': elm.get('type' , '')})
                else:  
                    messages.append({'role': 'system', 'content': elm.get('message', '')})

        messages.append({"role": "user", "content": message_text , 'type': message_type})


        aiPayload = MessageResponse(
            messages=messages
        )

        async def stream_response():
            response_message = {
                'user_id': user_id,
                'message': '', 
                'type': 'question',
                'chat_id': chat_id,
                'create_time': datetime.now(timezone.utc).replace(tzinfo=None)
            }

            chat_message = {
                "user_id": user_id,
                "message": message_text,
                "type": message_type,
                "chat_id": chat_id,
                "create_time": datetime.now(timezone.utc).replace(tzinfo=None),
            }
            chat_collection = nodb["messages"]
            result = await chat_collection.insert_one(chat_message)
            
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to insert chat message into MongoDB")
            
            async for ai_message_chunk in AIResponse(aiPayload):
                response_message['message'] += ai_message_chunk
                yield f"data: {json.dumps({'content': ai_message_chunk})}\n\n"

            yield "data: [DONE]\n\n"

            response_result = await chat_collection.insert_one(response_message)
            if not response_result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to insert AI response into MongoDB")

            await updateLastInteractoin(chat_id=chat_id, db=db)

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )

    except HTTPException as http_exc:
        raise http_exc  

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error: {str(e)}")

   
@router.get("/chats/")
async def get_chats(
    user: dict = Depends(authenticate),
    db: AsyncSession = Depends(get_db)
    
):
    try:
        user_id = user.get("user_id")
        resultUser = await db.execute(
            text('SELECT * FROM users WHERE id = :user_id'), 
            {"user_id": user_id}
        )
        user_record = resultUser.fetchone()

        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")

        payload = GetChatsPayload(
            user_id = user.get("user_id"),
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
    