import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from app.middlewares.auth.userauth import authenticate as userAuthenticate
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.controlers.user import createToken
from app.nodatabase import get_nodb
from app.ml_models.sbertmodel import classify_question
from app.controlers.chat import creatChat, getChats, updateLastInteractoin,getChat,set_chat_title
from app.controlers.message import PageMessages
from datetime import datetime, timezone
from app.schemas.chat import MessagePayload
from app.models.chat import Chat
from app.schemas.chat import GetChatsPayload, GetOneChat, GetMessages
from app.controlers.ai import AIResponse, get_title
from app.schemas.ai import MessageResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import StreamingResponse
import json
router = APIRouter()


@router.post('/addmessage')
async def addMessage(
    payload: MessagePayload,  # Use Pydantic model
    user: dict = Depends(userAuthenticate), 
    db: AsyncSession = Depends(get_db),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    try:
        user_id = user.get("user_id")
        portal_id_value = user.get("portal_id")

        result = await db.execute(
            text('SELECT * FROM user_portal WHERE id = :portal_id'),
            {"portal_id": portal_id_value}
        )

        row = result.fetchone()
        resultUser = await db.execute(
            text('SELECT * FROM users WHERE id = :user_id'), 
            {"user_id": user_id}
        )
        user_record = resultUser.fetchone()

        if not user_record:
            raise HTTPException(status_code=404, detail="User not found")
        portal_id = row.portal_id
        chat_record = None
        if payload.chat_id == "newchat":
            chat_record = await creatChat(user_id , db)
            asyncio.create_task(set_chat_title(chat_record, payload.message, db))

        else:
            oneChat = GetOneChat(
                user_id=user_id,
                chat_id=payload.chat_id
            )
            chat_record = await getChat(oneChat , db)

        if not chat_record:
            raise HTTPException(status_code=404, detail="Chat not found")

        message_text = payload.message
        message_type = await classify_question(message_text)
        
        chat_id = chat_record.id
        
        oneChat = GetMessages(
            user_id=user_id,
            chat_id=chat_id,
            start= max(1 , chat_record.messages_number - 4),
            end= chat_record.messages_number
        )
        
        messages_records = await PageMessages(oneChat, nodb) if payload.chat_id != 'newchat' else []
        messages = []

        if payload.chat_id != 'newchat':
            for elm in messages_records:
                msg_type = elm.get('type', '')
                template = elm.get('template', '')
                message = elm.get('message', '')

                if msg_type != 'question': 
                    content = template + message if template else message
                    messages.append({'role': 'user', 'content': content})
                else: 
                    messages.append({'role': 'system', 'content': message})

        messages.append({
            "role": "user",
            "content": message_text,
        })

        payload.chat_id = chat_id

        aiPayload = MessageResponse(
            messages=messages,
            portal_id=portal_id,
            user_id=user_id,
            messageType=message_type
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
                "user_id": user_id, #Foriegh Key from User Table
                "message": message_text, # String Column for Message
                "type": message_type, # Type of the message column(if it is from chat gpt it consider question if it from user it's (Build Chat, General Question ...))
                "chat_id": chat_id, # Forieghn Key from Chat Table
                "create_time": datetime.now(timezone.utc).replace(tzinfo=None), #Date Time for create the response
                "template": ''
            }
            chat_collection = nodb["messages"]
            
            async for ai_message_chunk in AIResponse(aiPayload):
                if isinstance(ai_message_chunk, dict) and ai_message_chunk.get('type') == 'template':
                    chat_message['template'] = ai_message_chunk.get('data')
                else:
                    if isinstance(ai_message_chunk, dict):
                        continue
                    response_message['message'] += ai_message_chunk
                    yield f"data: {json.dumps({'content': ai_message_chunk})}\n\n"

            yield f"data: {json.dumps({'status': '[DONE]', 'chat_id': payload.chat_id, 'Token': user.get('Token')})}\n\n"
            
            result = await chat_collection.insert_one(chat_message)
            response_result = await chat_collection.insert_one(response_message)
            
            if not response_result.inserted_id or not result.inserted_id:
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
    user: dict = Depends(userAuthenticate),
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
        
        return {
                'Chats': chats,
                'Token': user.get('Token')
            }
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=401 , detail=e)


@router.get('/messages')
async def getmessages(
    user: dict = Depends(userAuthenticate),
    start: int = Query(1, alias="start"), 
    end: int = Query(10, alias="end"), 
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
    