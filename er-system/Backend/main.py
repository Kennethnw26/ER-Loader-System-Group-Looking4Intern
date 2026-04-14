from fastapi import FastAPI
from Backend.database import get_hospitals

app = FastAPI()

@app.get("/")
def root():
    return {"message": "ER Load Balancer Running"}

@app.get("/hospitals")
def hospitals():
    return {"hospitals": get_hospitals()}