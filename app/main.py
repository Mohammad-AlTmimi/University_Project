from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {'H' : 'Hello World'}