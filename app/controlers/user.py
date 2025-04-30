import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import jwt
from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text
from passlib.context import CryptContext
from app.schemas.user import createUser as userType
from app.models.user import User, UserStatus, UserUpdate, UserRole
from app.database import get_db
from app.models import User , UserPortal
from app.schemas.user import loginUser
from sqlalchemy.future import select
from bs4 import BeautifulSoup
import aiohttp
from dotenv import load_dotenv
import os
import unicodedata
from app.nodatabase import get_nodb
import re
from app.controlers.admin import createToken as createAdminToken
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import datetime as dt
from sqlalchemy import and_

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def createToken(user_id, user_key, type='Default'):
    SECRET_KEY = os.getenv('jwtToken')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables.")
    
    expiration_time = datetime.now(dt.timezone.utc) + timedelta(minutes=30)
    expiration_timestamp_ms = int(expiration_time.timestamp() * 1000)

    payload = {
        'user_id': f"{user_id} {expiration_timestamp_ms}",
        'portal_id': f"{user_key} {expiration_timestamp_ms}",
        "exp": datetime.now(dt.timezone.utc) + timedelta(minutes=30)
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
        select(User).join(UserPortal).where(
            and_(
                UserPortal.portal_id == payload.portal_id,
                User.role == UserRole.student
            )
            
            
            )
        )
        user = result.scalar_one_or_none()

        if user and pwd_context.verify(payload.password, user.password_hash) and user.status == UserStatus.active:
            return {
                    "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role
                },
                "token": createToken(user.id, user.portal_id) if user.role == UserRole.student else createAdminToken(admin_id=user.id, portal_id=payload.portal_id)
            }
        else:
            raise HTTPException(status_code=404, detail="Invalid credentials")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed to search for user")


async def loginPortal(portalId: str, portalPassword: str):
    url = 'https://portal.hebron.edu/Default.aspx'

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until='domcontentloaded')
            
            html = await page.content()  # Get the HTML content
            soup = BeautifulSoup(html, 'html.parser')
            
            viewstate = soup.find("input", {'name': '__VIEWSTATE'})['value'] if soup.find("input", {'name': '__VIEWSTATE'}) else ''
            viewstategenerator = soup.find("input", {'name': '__VIEWSTATEGENERATOR'})['value'] if soup.find("input", {'name': '__VIEWSTATEGENERATOR'}) else ''
            eventvalidation = soup.find("input", {'name': '__EVENTVALIDATION'})['value'] if soup.find("input", {'name': '__EVENTVALIDATION'}) else ''
            
            await browser.close()

            if not viewstate or not viewstategenerator or not eventvalidation:
                raise HTTPException(status_code=403, detail="Failed to extract ASP.NET hidden fields")
            
            return viewstate, viewstategenerator, eventvalidation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

        
async def signPortal(portalId: str, portalPassword: str):
    viewstate , viewstategenerator, eventvalidation = await loginPortal(portalId=portalId, portalPassword=portalPassword)
    async with aiohttp.ClientSession() as session:
        background_tasks: BackgroundTasks
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
            
                
            if (
                college and major
                and college.text.strip() == 'كلية تكنولوجيا المعلومات'
                and major.text.strip() == 'علم الحاسوب'
            ):
                asyncio.create_task(scrapUserCourses(session_id=session_id, portal_id=portalId))
                return student_name.text.strip() if student_name else "Student name not found"
            else:
                raise HTTPException(status_code=403, detail="Unauthorized student to sign up")
      

def extract_detail_blocks(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    detail_blocks_data = []

    for block in soup.select('div.DetailBlock'):
        try:

            course_type = block.select_one('.DetailBlockHeader').get_text(strip=True)


            remaining_span = block.select_one('span[id*="lblHoursRemaining_"]')
            remaining_hours = remaining_span.get_text(strip=True) if remaining_span else "0"

            course_rows = block.select('table[id*="gv_DtlCourses_"] tr')[1:]

            courses = []
            for row in course_rows:
                cells = [unicodedata.normalize('NFKC', cell.get_text(strip=True)).replace('\xa0', ' ') for cell in row.find_all('td')]
                if cells:
                    cells[-1] = cells[-1].split(',')
                    cells[2] = int(cells[2])
                    cells[0] = cells[0].split('/')[0]
                    courses.append(cells)

            detail_blocks_data.append({
                "course_type": course_type,
                "remaining_hours": int(remaining_hours),
                "courses": courses
            })
        except Exception as e:
            print(f"Error parsing block: {e}")

    return detail_blocks_data
              
async def scrapUserCourses(session_id, portal_id):
    url = os.getenv('URLB')
    cookies = {'ASP.NET_SessionId': session_id}
    
    try:
        async with aiohttp.ClientSession(cookies=cookies) as session:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': url,
        }
            async with session.get(url, headers=headers) as response:
                db = await get_nodb()
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                element = soup.find(string=re.compile("الخطة الدراســـية"))
                number = ""
                if element:
                    match = re.search(r"\d+", element)
                    if match:
                        number = match.group()
                blocks_data = extract_detail_blocks(text)


                print(f"Number of courses found: {len(blocks_data)}")
                print(blocks_data)
                collection = db['student_data']
                semester = os.getenv('semester')
                print(number)
                under_warning_text = soup.find(id="ContentPlaceHolder1_Label1422").text.strip()
                under_warning_value = under_warning_text.split(":")[-1].strip()
                is_under_warning = True if under_warning_value == "نعم" else False
                
                # Extract user level
                user_level_text = soup.find(id="ContentPlaceHolder1_Label322").text.strip()
                user_level_value = user_level_text.split(":")[-1].strip()
                gpa_text = soup.find(id="ContentPlaceHolder1_avg_total").text.strip()
                gpa_value = gpa_text.split(":")[-1].strip()
                print(user_level_value , is_under_warning, gpa_value)
                await collection.insert_one(
                    {
                        'semester': semester,
                        'portal_id': portal_id,
                        'courses': blocks_data,
                        'active': True,
                        'planNumber': str(number),
                        'level': user_level_value,
                        'under_warning': is_under_warning,
                        'GPA': gpa_value,
                        'create_time': datetime.now(dt.timezone.utc)
                    }
                )

    except aiohttp.ClientError as e:
        raise Exception(f"Failed to fetch courses from {url}: {str(e)}")