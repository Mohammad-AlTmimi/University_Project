from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.nodatabase import get_nodb
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.chat import GetMessages




async def PageMessages(payload: GetMessages , db: AsyncIOMotorDatabase):
    try:
        chat_collection = db['messages']

        # Pagination parameters
        offset = payload.start - 1  
        limit = payload.end - payload.start + 1  
        
        chat_cursor = chat_collection.find(
            {'user_id': payload.user_id, 'chat_id': payload.chat_id}
        ).sort('create_time', 1).skip(offset).limit(limit)


        chat_messages = await chat_cursor.to_list()
        chat_messages = [{**chat, '_id': str(chat['_id'])} for chat in chat_messages]

        return chat_messages
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)
        
    
