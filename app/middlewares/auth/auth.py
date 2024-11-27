import jwt
import datetime
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status

load_dotenv()



def authenticate (token : str):
    try : 
        
        SECRET_KEY = os.getenv('jwtToken')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    
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

    
    