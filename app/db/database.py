from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

connection_string = 'postgresql://usmansoomro1234:Q1crbwy8CTXe@ep-wispy-art-23975610.ap-southeast-1.aws.neon.tech/rdbms_project?sslmode=require'


engine = create_engine(connection_string)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db =SessionLocal() 
    
    try:
        yield db
    finally:
        db.close()
