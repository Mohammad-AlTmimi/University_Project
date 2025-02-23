import jwt
import datetime
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status, Header
from typing import Dict, Any
from app.controlers import createToken
load_dotenv()
#PYjwt


# Authorization <Bear> token
async def authenticate(Authorization: str = Header(...)) -> Dict[str, Any]:
    try:
        SECRET_KEY = os.getenv('jwtToken')
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