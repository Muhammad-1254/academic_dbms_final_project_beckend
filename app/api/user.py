from fastapi import Response,Request,Form,Query, Depends, HTTPException, status, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
import json
from db.database import get_db
import  utils
from schemas.person import PersonLogin, PersonSignup, PersonUpdate, PersonImage, UserValidateToken
from db.models.person import User, Admin, Manager
from fastapi.responses import Response
import cloudinary.uploader

from db.models.data_types import Role 




router = APIRouter()


auth_token_file_name = 'app/temp/auth_tokens.npy'



@router.post("/login")
async def login(person: PersonLogin, response: Response, db: Session = Depends(get_db)):
    try:

        person_exist = utils.get_person_by_email(person.email, person.role, db)
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
            )
        if person_exist.password != person.password:
            raise HTTPException(
                status_code=status.HTTP_401_NOT_FOUND,
                detail="email or password is invalid",
            )

        # user_credentials = json.dumps(
        #     {
        #         "email": person_exist.email,
        #         "password": f"hashed:{person_exist.password}",
        #         "role": person.role.value,
        #     }
        # )

        # # setting cookies to user browser
        # response.set_cookie(
        #     key="user_credentials", value=user_credentials,    
        # )
        data = {
            "userId":person_exist.id,
            "email": person_exist.email,
            "username": person_exist.username,
            "isAuth":person_exist.is_auth,
            "role": person.role.value,
            "profileImage":person_exist.image
        }


        return {"message": "user login successfully", "data":data}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}


@router.post("/signup")
async def signup(
    person: PersonSignup, response: Response, db: Session = Depends(get_db)
):
    try:
        person_exist = utils.get_person_by_email(person.email, person.role, db)
        if person_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email already exist",
            )

        if person.role.value == "user":
            new_person = User(
                username=person.username, email=person.email, password=person.password
            )

        elif person.role.value == "manager":
            new_person = Manager(
                username=person.username,
                email=person.email,
                password=person.password,
            )
        elif person.role.value == "admin":
            new_person = Admin(
                username=person.username,
                email=person.email,
                password=person.password,
            )
            

        db.add(new_person)
        db.commit()
        db.refresh(new_person)
       
       
        # setting cookies to user browser
        # user_credentials = json.dumps(
        #     {
        #         "email": person.email,
        #         "password": f"hashed:{person.password}",
        #         "role": person.role.value,
        #     }
        # )

        # response.set_cookie(
        #     key="user_credentials", value=user_credentials, 
        # )

        # checking if user then generating auth token and email to user
        if person.role.value == "user":
            print(new_person.id)       
            new_token = utils.generate_new_auth_token(new_person.id)
            utils.sendEmail(person.email, "Authorize your account", f"Kindly authorize your account by using this 6 digit token: {new_token}")
        data = {
            "userId":new_person.id,
            "email": new_person.email,
            "username": new_person.username,
            "isAuth":new_person.is_auth,
            "role": person.role.value,
        }
        return {"message": "user signup successfully", "data": data}

    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}



@router.put("/update_username")
async def update(person: PersonUpdate,request:Request, db: Session = Depends(get_db)):
    try:
        print(f"person: {person}")
        person_exist = utils.get_person_by_email(person.email, person.role, db)
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
            )    

        # checking if user is login or not
        # user_credentials = request.cookies.get("user_credentials")
        # print(f"user_credentials: ",user_credentials)
        # user_credentials = json.loads(user_credentials)
        # person_password = user_credentials["password"].split(":")[1]
        # print(f"person_password: ",person_password)
        
        # if person_password != person_exist.password:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="user not login",
        #     )
        person_exist.username= person.username
        db.commit()
        db.refresh(person_exist)     
        return {"message": "username updated successfully"}  
           
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Somtheing went wrong: {e}"}




@router.get("/profile/image")
async def get_image_(
    email: str = Query(''),
    role: Role = Query(Role.USER),
    
     db: Session = Depends(get_db)
    ):
    try:
        if role == Role.USER:
            person_exist = db.query(User).filter(User.email == email).first()
        elif role == Role.MANAGER:
            person_exist = db.query(Manager).filter(Manager.email == email).first()
        elif role == Role.ADMIN:
            person_exist = db.query(Admin).filter(Admin.email == email).first()
        
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return {"message":"profile image deleted successfully","data":person_exist.image}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}




@router.post('/profile/image')
async def upload_image_(
    email: str = Form("usman"),
    role: Role = Form(Role.USER),
    
     file:UploadFile=File(...), 
     db: Session = Depends(get_db)
    
    ):
    try:
        if role == Role.USER:
            person_exist = db.query(User).filter(User.email == email).first()
        elif role == Role.MANAGER:
            person_exist = db.query(Manager).filter(Manager.email == email).first()
        elif role == Role.ADMIN:
            person_exist = db.query(Admin).filter(Admin.email == email).first()
        
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        result = cloudinary.uploader.upload(file.file, public_id=f"{person_exist.id}:_:profile")
        person_exist.image = result['secure_url']
        db.commit()
        db.refresh(person_exist)
        return {"message":"profile image uploaded successfully","url": result['secure_url']}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}


@router.put("/profile/image")
async def update_image_(
     email: str = Form("usman"),
    role: Role = Form(Role.USER),
    
     file:UploadFile=File(...), 
     db: Session = Depends(get_db)
    ):
    try:
        if role == Role.USER:
            person_exist = db.query(User).filter(User.email == email).first()
        elif role == Role.MANAGER:
            person_exist = db.query(Manager).filter(Manager.email == email).first()
        elif role == Role.ADMIN:
            person_exist = db.query(Admin).filter(Admin.email == email).first()
        
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        result = cloudinary.uploader.upload(file.file, public_id=f"{person_exist.id}:_:profile",  overwrite=True)
        person_exist.image = result['secure_url']
        db.commit()
        db.refresh(person_exist)
        return {"message":"profile image updated successfully","url": result['secure_url']}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}


@router.delete("/profile/image")
async def update_image_(
    email: str = Form("usman"),
    role: Role = Form(Role.USER),
    
     db: Session = Depends(get_db)
    ):
    try:
        if role == Role.USER:
            person_exist = db.query(User).filter(User.email == email).first()
        elif role == Role.MANAGER:
            person_exist = db.query(Manager).filter(Manager.email == email).first()
        elif role == Role.ADMIN:
            person_exist = db.query(Admin).filter(Admin.email == email).first()
        
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        result = cloudinary.uploader.destroy(public_id=f"{person_exist.id}:_:profile")
        print(f"deleted profile image result: {result}")
        person_exist.image = None
        db.commit()
        db.refresh(person_exist)
        return {"message":"profile image deleted successfully"}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}


@router.delete('/delete')
async def delete_user_(
    email: str = Form("usman"),
    role: Role = Form(Role.USER),
    
     db: Session = Depends(get_db)
    ):
    try:
        if role == Role.USER:
            person_exist = db.query(User).filter(User.email == email).first()
        elif role == Role.MANAGER:
            person_exist = db.query(Manager).filter(Manager.email == email).first()
        elif role == Role.ADMIN:
            person_exist = db.query(Admin).filter(Admin.email == email).first()
        
        if person_exist is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        result = cloudinary.uploader.destroy(public_id=f"{person_exist.id}:_:profile")
        print(f"deleted profile image result: {result}")

        db.delete(person_exist)
        db.commit()
        return {"message":"User deleted successfully"}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}


@router.get("/user/authorize/generate_new_token")
async def new_token_(user_id:str, email:str, ):
    try:
        
        new_token = utils.generate_new_auth_token(user_id)
        utils.sendEmail(email, "Authorize your account", f"Kindly authorize your account by using this 6 digit token: {new_token}")
        return {"message": "new token generated successfully"}
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}





@router.post("/user/authorize/validate_token")
async def authorize_user_(token:UserValidateToken, db: Session = Depends(get_db)):
    try:
        if utils.validate_token(token.user_id, token.token):
            user = db.query(User).filter(User.id == token.user_id).first()
            user.is_auth = True
            db.commit()
            db.refresh(user)
            return {"message": "user authorize successfully", "is_auth":True}
        else:
            new_token = utils.generate_new_auth_token(token.user_id)
            utils.sendEmail(user.email, "Authorize your account", f"The old token is expired, kindly use this new token: {new_token} \nvalid in 24 hours")
            return {"message": "User Authorization failed, kindly check your email", "is_auth":False}
            
    except Exception as e:
        print(f"error: {e}")
        return {"message": f"Something went wrong: {e}"}











