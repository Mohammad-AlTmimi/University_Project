import jwt
import datetime
from fastapi import HTTPException, status, Header
from typing import Dict, Any
from app.controlers import createToken
from app.models.user import User , UserStatus
from dotenv import load_dotenv
from app.database import get_db
import os
from sqlalchemy import select , and_

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)
#PYjwt


# Authorization <Bear> token
async def authenticate(
    Authorization: str = Header(...), 
    token_type: str = "Default"
) -> Dict[str, Any]:
    try:
        SECRET_KEY = os.getenv('jwtToken') if token_type == "Default" else os.getenv('jwtTokenResetPassword')
        if not SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT secret key is not set"
            )
        
        # Ensure Authorization header follows "Bearer <token>" format
        if not Authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format"
            )
        token = Authorization.split(" ")[1]  # Extract token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload['user_id']:
            payload['user_id'] = payload['user_id'].split(' ')[0]
            
        if 'portal_id' in payload:
            payload['portal_id'] = payload['portal_id'].split(' ')[0]
        async for db in get_db(): 
            user_id = payload['user_id']
            result = await db.execute(select(User).where(
                and_(
                    User.id == user_id,
                    User.status == UserStatus.active
                )
                
            ))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=401, detail='not authorized')
        payload['Token'] = createToken(payload.get('user_id'), payload.get('portal_id'))
        return payload  # Return the decoded JWT payload

    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing or improperly formatted"
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(status_code=500 , detail=e)