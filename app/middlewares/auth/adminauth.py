import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status, Header
from app.controlers.admin import createToken
from dotenv import load_dotenv
from typing import Dict, Any
import os
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

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
        if payload['admin_id'] and payload['portal_id']:
            payload['admin_id'] = payload['admin_id'].split(' ')[0]
            payload['portal_id'] = payload['portal_id'].split(' ')[0]
        else :
            raise HTTPException(status_code=401, detail='Token Is Not Suitable')
        payload['Token'] = createToken(payload.get('admin_id'), payload.get('portal_id'))
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