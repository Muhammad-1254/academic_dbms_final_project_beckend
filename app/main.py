
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


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






@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred. Please try again later."},
    )
