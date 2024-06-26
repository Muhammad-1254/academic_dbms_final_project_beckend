from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
connection_string = os.getenv("DATABASE_URL")


engine = create_engine(connection_string)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db =SessionLocal() 
    
    try:
        yield db
    finally:
        db.close()
