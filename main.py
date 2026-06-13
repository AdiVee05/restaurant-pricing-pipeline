from fastapi import FastAPI
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Testing API code"}

from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    print("Connection!")

# engine = create_engine("sqlite://", echo=True) 
# only for a random SQL Lite Server