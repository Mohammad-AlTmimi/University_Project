from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from app.schemas.user import createUser, loginUser, ForgetPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.controlers.user import createToken
from app.database import get_db
from app.controlers.user import createUser as crUser , searchUser, signPortal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat
from app.middlewares.auth import authenticate
from app.models import User , UserPortal
from sqlalchemy.future import select
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/signup")
async def signup(user: createUser , db: AsyncSession = Depends(get_db)): 
    try:
        name = await signPortal(user.portal_id , user.portal_password)
        user.name = name
        newUser = await crUser(user , db)  # Ensure you await if it's an async function
        token = createToken(newUser['user_id'] , newUser['portal_id'])
        return {'User': newUser , 'Token': token, 'Name': name}
    except HTTPException as e:
        print(e)
        raise e 
    
    except Exception as e:
        print(e)
        raise (e)

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
        
@router.post('/changephoto')
async def changephoto(
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    return 'complete when you have s3 bucket'

@router.post('/forgetpassword')
async def forgetPassword(
    payload: ForgetPasswordRequest,
    db :AsyncSession = Depends(get_db)
):
    try:
        name = await signPortal(payload.portal_id , payload.portal_password) 
        result = await db.execute(
            select(User).join(UserPortal).where(UserPortal.portal_id == payload.portal_id)
        )
        user = result.scalar_one_or_none()     
        if not user:
            return HTTPException(status_code=404 , detail='User does not exist')
        token = createToken(user.id , payload.portal_id , 'resetpassword')
        return {
            'token': token
        }
    except HTTPException as httpx:
        raise httpx   
@router.post('/resetpassword')
async def resetpassword(
    payload: ResetPasswordRequest,  
    Authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await authenticate(Authorization, "ResetPassword")
        user_id = user.get("user_id")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user: 
            raise HTTPException(status_code=404, detail="No user found")

        user.password_hash = payload.password  
        user.set_password(payload.password)  
        await db.commit()
        return {"password": payload.password}

    except HTTPException as httpx:
        raise httpx
    
    
@router.post('/changepassword')
async def changepassword(
    payload: ChangePasswordRequest,  
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db),
):
    try:
        user_id = user.get("user_id")
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user: 
            raise HTTPException(status_code=404, detail="No user found")
        if not pwd_context.verify(payload.old_password, user.password_hash):
            raise HTTPException(status_code=404, detail="Wrong Password")

        user.password_hash = payload.password  
        user.set_password(payload.password)  
        await db.commit()
        return {"password": payload.password}
    
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise e
    
    
    