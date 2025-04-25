from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from app.schemas.admin import LogInAdmin
from app.models.admin import Admin
from app.controlers.admin import SearchAdmin, createToken
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.middlewares.auth.adminauth import authenticate
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

@router.post('/stopservice')
async def stopservice(
    admin: dict = Depends(authenticate),
    db: AsyncSession = Depends(get_db)
)
    