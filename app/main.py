from fastapi import FastAPI
from app.exceptions import CustomError
from requests import Request
app = FastAPI()

@app.get("/")
def root():
    return "Hello World"

