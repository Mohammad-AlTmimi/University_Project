from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from app.schemas.admin import LogInAdmin, ToggleRequest
from app.models.admin import Admin
from app.controlers.admin import SearchAdmin, createToken, update_env_file
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.middlewares.auth.adminauth import authenticate
import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
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
            'Token': token
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
        }
        
    except HTTPException as httpx:
        raise httpx
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to {payload.action} service: {str(e)}"
        )
    