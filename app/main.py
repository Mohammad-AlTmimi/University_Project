from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from requests import Request
from app.database import get_db, init_db, delete_table
from .models import User, UserPortal, Chat
from app.routers.chat import router as chat_router
from app.routers.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # Run database initialization
    yield  # The app will run here
    
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",  # Your frontend URL
    "http://127.0.0.1:5173",  # If you're using another localhost variation
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)




# Initialize the FastAPI app with the lifespan context manager

app.include_router(chat_router, prefix='/chat')
app.include_router(user_router, prefix='/user')


@app.get("/")
def root():
    return {"message": "Hello World"}
@app.delete('/')
async def delet():
    await delete_table()
    return {'delete'}
@app.get("/db-status")
async def db_status(db: AsyncSession = Depends(get_db)):
    try:
        # Try a simple query to check the connection
        resultUser = await db.execute(select(User))
        users = resultUser.scalars().all()
        resultPortal = await db.execute(select(UserPortal))
        portals = resultPortal.scalars().all()
        resultChat = await db.execute(select(Chat))
        chat = resultChat.scalars().all()
        return {"status": "connected", "users": users[:5], "portal": portals[:5], "Chats": chat[:5]}  # Return a sample of data
    except Exception as e:
        # In case of any error with the DB connection
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )
