import jwt
import datetime
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status

load_dotenv()
#PYjwt


from fastapi import Header, HTTPException, status
# Authorization <Bear> token
async def authenticate(Authorization: str = Header(...)):
    try:
        SECRET_KEY = os.getenv('jwtToken')
        token = Authorization.split(" ")[1]  # Extract token from "Bearer <token>"
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Return the decoded payload
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

    
    