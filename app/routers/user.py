from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from app.schemas.user import createUser, loginUser, ForgetPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, LoginPortal
from app.controlers.user import createToken
from app.database import get_db
from app.controlers.user import createUser as crUser , searchUser, signPortal, searchPortal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat
from app.middlewares.auth.userauth import authenticate
from app.models import User , UserPortal
from sqlalchemy.future import select
from passlib.context import CryptContext
from app.models.user import UserRole, UserUpdate
from sqlalchemy import and_


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/signup")
async def signup(user: createUser , db: AsyncSession = Depends(get_db)): 
    try:
        name = await signPortal(user.portal_id , user.portal_password)
        user.name = name if user.name == '' or not user.name else user.name
        newUser = await crUser(user , db)  # Ensure you await if it's an async function
        token = createToken(newUser['user_id'] , newUser['portal_id'])
        return {'User': newUser , 'Token': token, 'Name': user.name}
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
        user = await searchUser(payload, db)

        return {"message": "Login successful", "user": dict(user)}
    except HTTPException as http_exc:
        raise http_exc 

    except Exception as e:
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

@router.post('/updateportalpassword')
async def updateportal(
    payload,
    user: dict = Depends(authenticate), 
    db: AsyncSession = Depends(get_db)
):
    try:
        portal_ID = user.get('portal_id')
        portal = await searchPortal(
            LoginPortal(
                Id = portal_ID,
                db = db
            )
        )
        val = await signPortal(portalid=portal.portal_id, portalPassword=payload.password)
        if not val:
            raise HTTPException(status_code=401, detail='wrong password')
        result = await db.execute(
        select(User).join(UserPortal).where(
            and_(
                UserPortal.portal_id == portal.portal_id,
                User.role == UserRole.student
            )
            )
        )
        user = result.scalar_one_or_none()
        user.updated = UserUpdate.Yes
        portal.portal_password = payload.password
        db.add(user)
        db.add(portal)

        await db.flush()   # Optional, useful if you need to use the data before commit
        await db.commit()  # Actually commits the changes

        return {"message": "Portal password updated successfully"}
        
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise e
    
    
    