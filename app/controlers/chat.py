from app.models import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.future import select
from app.schemas.chat import getMessagePayload

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


async def getChats(payload: getMessagePayload , db: AsyncSession):
    try:
        stmt = (
            select(Chat)
            .order_by(Chat.last_interaction.desc())  # Order by most recent last_interaction
            .offset(payload.start - 1)  # Skip the first `start` chats
            .limit(payload.end - payload.start)  # Get chats between start and end range
        )
        result = await db.execute(stmt)
        chats = result.scalars().all()
        return chats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def updateLastInteractoin(chat_id: str, db: AsyncSession):
    chat = await db.get(Chat, chat_id)
    if chat:
        chat.update_last_interaction()  # This updates the specific chat's last_interaction
        await db.commit()