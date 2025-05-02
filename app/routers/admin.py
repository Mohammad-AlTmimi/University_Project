from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header,  Query
from app.schemas.admin import LogInAdmin, ToggleRequest
from app.models.admin import Admin
from app.controlers.admin import createToken, update_env_file, getusers
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
from app.controlers.ai import extract_text_from_pdf, chunk_text
from app.controlers.embedings import generate_embeddings
from fastapi.responses import JSONResponse
from app.mongodbatlas import get_atlas_db , create_text_search_index, create_vector_search_index, is_index_active
from app.schemas.ai import SearchQuery
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
router = APIRouter()



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
        expected_column_names = []
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
    db: AsyncIOMotorDatabase = Depends(get_atlas_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file.file)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")

        # Chunk the text
        chunks = chunk_text(text)

        # Generate embeddings
        embedding_documents = generate_embeddings(chunks)

        # Access the hu_information collection
        chunks_collection = db['hu_information']

        # Create search indexes if they don't exist
        existing_indexes = await chunks_collection.list_search_indexes().to_list()
        index_names = [index['name'] for index in existing_indexes]
        print('ho')
        # ✅ First insert the documents
        if embedding_documents:
            await chunks_collection.insert_many(embedding_documents)
        
        # ✅ Then check and create indexes (after collection is created)
        existing_indexes = await chunks_collection.list_search_indexes().to_list()
        index_names = [index['name'] for index in existing_indexes]
        
        if "text_search" not in index_names:
            await create_text_search_index(chunks_collection)
            if not await is_index_active(chunks_collection, "text_search"):
                print("Warning: text_search index is still building.")
        
        if "vector_search" not in index_names:
            await create_vector_search_index(chunks_collection)
            if not await is_index_active(chunks_collection, "vector_search"):
                print("Warning: vector_search index is still building.")
        
        
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

@router.get('/students')
async def getStudents(
    admin = Depends(authenticate),
    db : AsyncSession = Depends(get_db),
    start: int = Query(1, alias="start"), 
    end: int = Query(10, alias="end"), 
):
    try:
        value = await getusers(db , start=start, end=end)
        return {
            'Studetns': value,
            'Token': admin.get('Token')
        }
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise e