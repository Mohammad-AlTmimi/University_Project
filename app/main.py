from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from requests import Request
from app.database import get_db, init_db
from .models import User
from app.routers.chat import router as chat_router
from app.routers.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


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

@app.get("/db-status")
async def db_status(db: AsyncSession = Depends(get_db)):
    try:
        # Try a simple query to check the connection
        result = await db.execute(select(User))  # Replace `User` with any valid model
        users = result.scalars().all()  # Fetching the first few users
        return {"status": "connected", "users": users[:5]}  # Return a sample of data
    except Exception as e:
        # In case of any error with the DB connection
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
