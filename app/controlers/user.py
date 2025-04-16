import jwt
import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text
from passlib.context import CryptContext
from app.schemas.user import createUser as userType
from app.models.user import User, UserStatus, UserUpdate
from app.database import get_db
from app.models import User , UserPortal
from app.schemas.user import loginUser
from sqlalchemy.future import select
from bs4 import BeautifulSoup
import aiohttp
from dotenv import load_dotenv
import os
import unicodedata

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
                name=user.name,
                updated = UserUpdate.Yes
            )
            newUser.set_password(user.password)

            db.add(newUser)
            await db.flush()  

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

async def loginPortal(portalId: str, portalPassword: str):
    url = 'https://portal.hebron.edu/Default.aspx'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': url,
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to load login page")
            
            page_content = await response.text()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value'] if soup.find("input", {'name': '__VIEWSTATE'}) else ''
            viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value'] if soup.find("input", {'name': '__VIEWSTATEGENERATOR'}) else ''
            eventvalidation = soup.find("input", {'name': '__EVENTVALIDATION'})['value'] if soup.find("input", {'name': '__EVENTVALIDATION'}) else ''
            if viewstate == None or viewstategenerator == None or eventvalidation == None:
                raise HTTPException(status_code=403 , detail="Failed to authenticate")
            return viewstate , viewstategenerator, eventvalidation

async def signPortal(portalId: str, portalPassword: str):
    viewstate , viewstategenerator, eventvalidation = await loginPortal(portalId=portalId, portalPassword=portalPassword)
    async with aiohttp.ClientSession() as session:
        url = 'https://portal.hebron.edu/Default.aspx'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': url,
        }
        data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'LoginPanel1$Username': portalId,
            'LoginPanel1$UserPassword': portalPassword,
            'LoginPanel1$Button1': 'دخول' 
        }
        
        async with session.post(url, data=data, headers=headers) as login_response:
            if login_response.status != 200:
                raise HTTPException(status_code=login_response.status, detail="Failed to authenticate")
            
            login_content = await login_response.text()
            soup = BeautifulSoup(login_content, 'html.parser')
            
            college = soup.find('span', id='std_info1_std_cologe')
            major = soup.find('span', id='std_info1_std_major')
            student_name = soup.find('span', id='std_info1_std_name')
            session_id = session.cookie_jar.filter_cookies(url).get('ASP.NET_SessionId') 
            print(session_id)
            await scrapUserCourses(session_id=session_id)
            if college and major and college.text.strip() == 'كلية تكنولوجيا المعلومات' and major.text.strip() == 'علم الحاسوب':
                return student_name.text.strip() if student_name else "Student name not found"
            else:
                raise HTTPException(status_code=403, detail="Unauthorized student to sign up")

async def scrapUserCourses(session_id):
    url = os.getenv('URLB')
    cookies = {'ASP.NET_SessionId': session_id}

    try:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                courses = [
                [
                    unicodedata.normalize('NFKC', cell.get_text(strip=True)).replace('\xa0', ' ')
                    for cell in row.find_all('td')
                ]
                for row in soup.find_all('tr', {'bgcolor': '#F7F7DE'})
            ]

                print(f"Number of courses found: {len(courses)}")
                print(courses)

    except aiohttp.ClientError as e:
        raise Exception(f"Failed to fetch user courses: {str(e)}")