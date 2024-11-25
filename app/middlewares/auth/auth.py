import jwt
import datetime
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status

load_dotenv()

def createToken(user_id , user_key):
    SECRET_KEY = os.getenv('jwtToken')
    payload = {
        "user_id": user_id,
        "user_key": user_key,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

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

    
    