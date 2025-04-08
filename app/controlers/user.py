import jwt
import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text
from passlib.context import CryptContext
from app.schemas.user import createUser as userType
from app.models.user import User, UserStatus
from app.database import get_db
from app.models import User , UserPortal
from app.schemas.user import loginUser
from sqlalchemy.future import select
import requests
from bs4 import BeautifulSoup
import aiohttp
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def createToken(user_id, user_key, type='Default'):
    SECRET_KEY = os.getenv('jwtToken')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables.")
    
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    expiration_timestamp_ms = int(expiration_time.timestamp() * 1000)

    payload = {
        'user_id': f"{user_id} {expiration_timestamp_ms}",
        'portal_id': f"{user_key} {expiration_timestamp_ms}",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
    if type != 'Default':
        SECRET_KEY = os.getenv('jwtTokenResetPassword')
        
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


async def createUser(user: userType, db: AsyncSession):
    try:
        async with db.begin():  # Start a transaction
            # Step 1: Create the UserPortal object first
            portal = UserPortal(
                portal_id=user.portal_id, 
                portal_password=user.portal_password
            )
            db.add(portal)
            await db.flush()  # Flush to assign an ID before commit

            # Step 2: Create the User object
            newUser = User(
                password_hash=user.password,
                portal_id=portal.id,
                name=user.name
            )
            newUser.set_password(user.password)

            db.add(newUser)
            await db.flush()  # Ensure data is staged for commit

        # If no error occurs, commit happens automatically
        await db.commit()
        return {"user_id": newUser.id, "portal_id": portal.id}

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=403, detail="User or UserPortal already exists with the provided details.")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=404, detail=f"An unexpected error occurred: {str(e)}")

async def searchUser(payload: loginUser, db: AsyncSession):
    try:
        result = await db.execute(
        select(User).join(UserPortal).where(UserPortal.portal_id == payload.portal_id)
        )
        user = result.scalar_one_or_none()

        if user and pwd_context.verify(payload.password, user.password_hash) and user.status == UserStatus.active:
            return {
                    "user": {
                    "id": user.id,
                    "name": user.name,
                },
                "token": createToken(user.id, user.portal_id)
            }
        else:
            raise HTTPException(status_code=404, detail="Invalid credentials")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to search for user")


async def signPortal(portalId: str, portalPassword: str):
    url = 'https://portal.hebron.edu/Default.aspx'
    
    
    async with aiohttp.ClientSession() as session:
        # First, get the login page to extract hidden fields
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to load login page")
            
            page_content = await response.text()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract hidden fields
            viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value'] if soup.find("input", {'name': '__VIEWSTATE'}) else ''
            viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value'] if soup.find("input", {'name': '__VIEWSTATEGENERATOR'}) else ''
            eventvalidation = soup.find("input", {'name': '__EVENTVALIDATION'})['value'] if soup.find("input", {'name': '__EVENTVALIDATION'}) else ''
            if viewstate == None or viewstategenerator == None or eventvalidation == None:
                raise HTTPException(status_code=403 , detail="Failed to authenticate")
        # Prepare login data
        data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'LoginPanel1$Username': portalId,
            'LoginPanel1$UserPassword': portalPassword,
            'LoginPanel1$Button1': 'دخول'  # Arabic for "Login"
        }
        
        # Send login request
        async with session.post(url, data=data, headers=headers) as login_response:
            if login_response.status != 200:
                raise HTTPException(status_code=login_response.status, detail="Failed to authenticate")
            
            login_content = await login_response.text()
            soup = BeautifulSoup(login_content, 'html.parser')
            
            # Extract student information
            college = soup.find('span', id='std_info1_std_cologe')
            major = soup.find('span', id='std_info1_std_major')
            student_name = soup.find('span', id='std_info1_std_name')
            
            if college and major and college.text.strip() == 'كلية تكنولوجيا المعلومات' and major.text.strip() == 'علم الحاسوب':
                return student_name.text.strip() if student_name else "Student name not found"
            else:
                raise HTTPException(status_code=403, detail="Unauthorized student to sign up")
