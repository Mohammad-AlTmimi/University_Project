from app.models import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.future import select
from app.schemas.chat import GetChatsPayload, createMessage, GetOneChat
from sqlalchemy import and_
from app.controlers.ai import get_title


async def creatChat(payload, db: AsyncSession):
    try:
        
        stmt = select(Chat).where(Chat.user_id == payload).order_by(Chat.chat_number.desc()).limit(1)
        result = await db.execute(stmt)
        last_chat = result.scalar_one_or_none()
    
        chat = Chat(
            chat_number = (last_chat.chat_number + 1) if last_chat else 1,
            user_id = payload
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=403 , detail="User or UserPortal already exists with the provided details.")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=404, detail=f"An unexpected error occurred: {str(e)}")


async def getChats(payload: GetChatsPayload , db: AsyncSession):
    try:
        stmt = (
            select(Chat)
            .where(Chat.user_id == payload.user_id)
            .order_by(Chat.last_interaction.desc()) 
        )
        result = await db.execute(stmt)
        chats = result.scalars().all()
        return chats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def updateLastInteractoin(chat_id: str, db: AsyncSession):
    try:
        chat = await db.get(Chat, chat_id)
        if chat:
            chat.update_last_interaction()
            chat.update_messages_number()
            await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await db.close()
        
async def getChat(payload: GetOneChat, db: AsyncSession):
    try:
        result = await db.execute(
            select(Chat).where(
                and_(
                    Chat.user_id == payload.user_id, 
                    Chat.id == payload.chat_id
                )
            )
        )
        
        chat = result.scalar_one_or_none()  # Fetch single result or None if no match
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def set_chat_title(chat_record, message, db):
    try:
        title = await get_title(message)
        title = title.strip('"')
        chat_record.title = title
        db.add(chat_record)
        await db.commit()
        await db.refresh(chat_record)

    except Exception as e:
        print(f"Failed to set title: {e}")