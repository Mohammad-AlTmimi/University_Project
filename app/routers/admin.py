from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from app.schemas.admin import LogInAdmin, ToggleRequest
from app.models.admin import Admin
from app.controlers.admin import SearchAdmin, createToken, update_env_file
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.middlewares.auth.adminauth import authenticate
import os
from dotenv import load_dotenv
from app.nodatabase import get_nodb
from motor.motor_asyncio import AsyncIOMotorDatabase
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone
from app.controlers.ai import extract_text_from_pdf, generate_embeddings, chunk_text
from fastapi.responses import JSONResponse


env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
router = APIRouter()

@router.post('/login')
async def loginAdmin(
    payload: LogInAdmin,
    db: AsyncSession = Depends(get_db)
):
    try:
        admin = await SearchAdmin(payload, db)
        token = createToken(admin.id, admin.portal_id)
        return {
            'Token': token,
            'role': 'admin'
        }
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise e

@router.post('/services/{service_id}/toggle')
async def stopservice(
    service_id: str,
    payload: ToggleRequest,
    admin: dict = Depends(authenticate),
    db: AsyncSession = Depends(get_db)
):
    try:
        allowed_services = ['BUILD_TABLE_QUESTION']
        if service_id not in allowed_services:
            raise HTTPException(status_code=400, detail="Invalid service ID")
        env_key = f"SERVICE_{service_id}_ENABLED"
        env_value = payload.action
        await update_env_file(env_key, env_value)
        return {
            "message": f"Service {service_id} {payload.action}ed successfully",
            'Token': admin.get('Token')
        }
        
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to {payload.action} service: {str(e)}"
        )

@router.get("/services")
async def get_services(admin: dict = Depends(authenticate)):
    try:
        allowed_services = ["SERVICE_BUILD_TABLE_QUESTION_ENABLED"]
        
        statuses = {}
        for service in allowed_services:
            if os.getenv(service) == 'start':
                statuses[service] = 'start'
            else :
                statuses[service] = 'stop'
        
        return statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")
@router.patch('/uploadsemestercourses')
async def uploadxslx(
    file: UploadFile = File(...),
    admin = Depends(authenticate),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    try:
        if not file.filename.endswith(".xlsx"):
            raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")
        content = await file.read()
        excel_data = BytesIO(content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        data = df.to_dict(orient='records')
        
        db = nodb['semester_courses']
        semester_obj = {
            'create_time': datetime.now(timezone.utc).replace(tzinfo=None),
            'courses': data,
            'Token': admin.get('Token')
        }
        print(data)
        result = await db.insert_one(semester_obj)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to insert Course Semester inot MongoDB")
        return{
            'message': 'File uploaded successfully',
            'inserted_id': str(result.inserted_id),
            'Token': admin.get('Token')
        }
      
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise HTTPException(status_code=500,detail=F"Failed to upload file: {str(e)}") 
    
@router.post('/upload-pdf')
async def Upload_PDF(
    file: UploadFile = File(...),
    admin = Depends(authenticate),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    try:


        text = extract_text_from_pdf(file.file)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")

        chunks = chunk_text(text)

        embedding_documents = generate_embeddings(chunks)
        chunks_collection = nodb['hu_information']
        if embedding_documents:
            await chunks_collection.insert_many(embedding_documents)

        return {
            'message': "PDF processed and saved successfully.",
            'Token': admin.get('Token')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/courses')
async def courses(
    admin = Depends(authenticate),
    nodb: AsyncIOMotorDatabase = Depends(get_nodb)
):
    try:
    
        db_availabe_course = nodb['semester_courses']
    
        availabe_course_cursor = await db_availabe_course.find().sort('create_time', -1).limit(1).to_list(length=None)[0]
        return {
            'Courses': availabe_course_cursor,
            'Token': admin.get('Token')
        }
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise e