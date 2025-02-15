from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import createUser, loginUser
from app.controlers.user import createToken
from app.database import get_db
from app.controlers.user import createUser as crUser , searchUser, signPortal
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter()

@router.post("/signup")
async def signup(user: createUser , db: AsyncSession = Depends(get_db)): 
    try:
        name = await signPortal(user.portal_id , user.portal_password)
        user.name = name
        newUser = await crUser(user , db)  # Ensure you await if it's an async function
        token = createToken(newUser['user_id'] , newUser['portal_id'])
        return {'User': newUser , 'Token': token, 'Name': name}  # Return the created user or any necessary response
    except HTTPException as e:
        # If an HTTPException was raised in signPortal, this will be caught here
        raise e 
    except Exception as e:
        return (e)

@router.post('/login')
async def login(payload: loginUser, db: AsyncSession = Depends(get_db)):
    """
    Expects payload with:
    {
        "user_id": <user_id>,
        "user_password": <user_password>
    }
    """
    # Call searchUser with the full payload
    user = await searchUser(payload, db)

    # Return success message or additional data
    return {"message": "Login successful", "user": dict(user)}
