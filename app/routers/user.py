from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.schemas.user import createUser, loginUser
from app.controlers.user import createToken
from app.database import get_db
from app.controlers.user import createUser as crUser , searchUser, signPortal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat


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
    try:
        """
        Expects payload with:
        {
            "portal_id": <portal_id>,
            "password": <user_password>
        }
        """
        # Call searchUser with the full payload
        user = await searchUser(payload, db)

        # Return success message or additional data
        return {"message": "Login successful", "user": dict(user)}
    except HTTPException as http_exc:
        raise http_exc  # Re-raise known HTTP exceptions to maintain status codes

    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Log for debugging (or use logging module)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
        
@router.get('/changephoto')
async def changephoto(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    return 'complete when you have s3 bucket'
    
