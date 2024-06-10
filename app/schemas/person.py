from pydantic import BaseModel
from db.models.data_types import Role

class PersonBase(BaseModel):
    email:str
    password:str
    
    
class PersonSignup(PersonBase):
    username:str
    role:Role
    
class PersonLogin(PersonBase):
    role:Role
    
class PersonUpdate(BaseModel):
    email:str
    username:str
    role:Role
    
class PersonImage(BaseModel):
    email:str
    role:Role


    
class UserValidateToken(BaseModel):
    user_id:str
    token:str