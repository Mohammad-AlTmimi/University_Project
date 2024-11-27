from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from requests import Request
from app.database import get_db
from .models import User
from app.routers.chat import router as chat_router
from app.controlers.user import createToken
from app.schemas.user import UserCreate
from app.controlers.user import createUser as crUser
app = FastAPI()

app.include_router(chat_router, prefix='/userChat')

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/createUser")
async def createUser(user: UserCreate, db: AsyncSession = Depends(get_db)):
    newUser = await crUser(user, db)  # Ensure you await if it's an async function
    token = createToken(newUser.id , newUser.user_id)
    print("hiihihihiih")
    print(token)
    print("hiihihihiih")
    return {'User': newUser , 'Token': token}  # Return the created user or any necessary response

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
