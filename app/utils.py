from sqlalchemy.orm import Session
from db.models.person import Admin, User, Manager
from db.models.data_types import Role
import random
import numpy as np
import datetime

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os


auth_token_file_name = 'app/temp/auth_tokens.npy'


def get_person_by_email( email: str,role:Role, db: Session,):
    if role.value =='user':            
        return db.query(User).filter(User.email == email).first()
    elif role.value == 'manager':
        return db.query(Manager).filter(Manager.email == email).first()
    elif role.value == 'admin':
        return db.query(Admin).filter(Admin.email == email).first()


def generate_random_numbers():
    return random.randint(0,1000000)
    
def has_24_hours_passed(timestamp):
    current_time = datetime.datetime.now()
    time_difference = current_time - timestamp
    return time_difference.total_seconds() >= 24 * 3600


def generate_new_auth_token(user_id:str):
    token_file = np.load(auth_token_file_name, allow_pickle=True).item()
    token = str(generate_random_numbers)
    new_token = [token, datetime.datetime.now()]
    
    if len(token_file) == 0:
        token_file[user_id] = new_token
        np.save(auth_token_file_name, token_file)
        return token
    for key,value in token_file.items():
        if key == user_id:
            token_file[key] = new_token
            np.save(auth_token_file_name, token_file)
            return token
        
def validate_token(user_id:str, token:str):
    token_file = np.load(auth_token_file_name, allow_pickle=True).item()
    for key,value in token_file.items():
        if key == user_id:
            if has_24_hours_passed(value[1]):
                return False
            if value[0] == token:
                return True
    return False



def sendEmail(email:str, subject:str, message:str):
    pass


def initialize_cloudinary():
    # Configure Cloudinary
    config = cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
    # config = cloudinary.config(secure=True)
    print("****1. Set up and configure the SDK:****\nCredentials: ", config.cloud_name, config.api_key, "\n")

