import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.nodatabase import get_nodb
from app.ml_models.sbertmodel import classify_question
from app.controlers.chat import creatChat, getChats, updateLastInteractoin,getChat
from datetime import datetime, timezone
from app.schemas.chat import MessagePayload
from app.models.chat import Chat
from app.schemas.chat import GetChatsPayload, GetOneChat, GetMessages
from app.controlers.ai import AIResponse
from app.schemas.ai import MessageResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import json
from fastapi.responses import StreamingResponse
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
        messages = []
        messages.append({"role": "user", "content": message_text})
        aiPayload = MessageResponse(
            messages=messages,
            portal_id='guest',
            user_id= 'guest',
            messageType= message_type,
        )
        async def stream_response():
            chat_message = {
                "user_id": user_id,
                "message": message_text,
                "type": message_type,
                "chat_id": chat_id,
                "create_time": datetime.now(timezone.utc).replace(tzinfo=None),
            }

            response_message = {
                'user_id': user_id,
                'message': '', 
                'type': 'response',
                'chat_id': chat_id,
                'create_time': datetime.now(timezone.utc).replace(tzinfo=None),
            }
            chat_collection = nodb["messages"]
            result = await chat_collection.insert_one(chat_message)
            
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to insert chat message into MongoDB")
            
            async for ai_message_chunk in AIResponse(aiPayload):
                response_message['message'] += ai_message_chunk
                yield f"data: {json.dumps({'content': ai_message_chunk})}\n\n"

            yield f"data: {json.dumps({'status': '[DONE]', 'chat_id': payload.chat_id})}\n\n"
            print('hi')
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

