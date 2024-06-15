
from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

import api.museum
from db.database import engine
from db.database import Base

from api import user, museum
import utils

import os
from fastapi.responses import JSONResponse
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    Base.metadata.create_all(bind=engine)
    utils.initialize_cloudinary()
    yield
    

app = FastAPI(lifespan=lifespan)


# Define the origins that should be allowed to make requests to your API
origins = [
    "http://localhost:3000",
]

# Add the CORS middleware to your FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# routers
app.include_router(user.router, prefix="/api/v1/user")
app.include_router(museum.router, prefix="/api/v1/museum")


@app.get('/api/v1/drop_all_tables')
async def drop_tables():
    Base.metadata.drop_all(bind=engine)
    return {"message": "Tables dropped successfully"}
@app.get("/api/v1/health")
async def health():
    return {"message":"Health is good!"}
