from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import createUser
from app.controlers.user import createToken
from app.database import get_db
from app.controlers.user import createUser as crUser , searchUser
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter()

@router.post("/signup")
async def signup(user: createUser): 
    return {"data": 'Hello World'}
    newUser = await crUser(user)  # Ensure you await if it's an async function
    token = createToken(newUser.user_id , newUser.portal_id)
    return {'User': newUser , 'Token': token}  # Return the created user or any necessary response

@router.post('/login')
async def login(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    Expects payload with:
    {
        "user_id": <user_id>,
        "user_password": <user_password>
    }
    """
    # Validate payload
    if "user_id" not in payload or "user_password" not in payload:
        raise HTTPException(status_code=400, detail="Invalid payload: user_id and user_password are required")
    
    # Call searchUser with the full payload
    user = await searchUser(payload, db)

    # Return success message or additional data
    return {"message": "Login successful", "user": dict(user)}
