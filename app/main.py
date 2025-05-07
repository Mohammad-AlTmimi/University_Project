import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, init_db, delete_table, create_async_database
from .models import User, UserPortal, Chat
from app.routers.admin import router as admin_router
from app.routers.chat import router as chat_router
from app.routers.user import router as user_router
from app.routers.guest import router as guest_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.nodatabase import delete_nodb
from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_async_database()
    await init_db()
    yield
    
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",  # Your frontend URL
    "http://127.0.0.1:5173",  # If you're using another localhost variation
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)





app.include_router(chat_router, prefix='/chat')
app.include_router(user_router, prefix='/user')
app.include_router(guest_router, prefix='/guest')
app.include_router(admin_router, prefix='/admin')


@app.get("/")
def root():
    return {
        'hello world'
    }
@app.delete('/')
async def delet():
    await delete_table()
    await delete_nodb()
    return {'delete'}
@app.get("/db-status")
async def db_status(db: AsyncSession = Depends(get_db)):
    try:
        resultUser = await db.execute(select(User))
        users = resultUser.scalars().all()
        resultPortal = await db.execute(select(UserPortal))
        portals = resultPortal.scalars().all()
        resultChat = await db.execute(select(Chat))
        chat = resultChat.scalars().all()
        
        return {"status": "connected", "users": users[:5], "portal": portals[:5], "Chats": chat[:5]}
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )
