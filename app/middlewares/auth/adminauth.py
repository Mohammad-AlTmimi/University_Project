import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status, Header

from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)