import sqlite3
from fastapi import APIRouter, HTTPException
from datetime import timedelta, datetime

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status
from config import Config

from app.user_database import get_db
from app.user_schema import UserCreate, UserBase
from app.user_crud import UserService, bcrypt_context


router = APIRouter(
    prefix='/user',
    tags=['user']
)

# Database setup
conn = sqlite3.connect('sqldata.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT UNIQUE, password1 TEXT, password2 Text)")
conn.commit()
conn.close()


# 회원가입
@router.post("/register", status_code=status.HTTP_204_NO_CONTENT)
async def register(userRegister: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing_user  = UserService.get_existing_user(db, userRegister.email)
    if existing_user :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.") # 에러 메시지로 가게끔 셋팅
    
    UserService.user_register(userRegister, db=db)
    
    return userRegister.username, {"msg": "회원가입 완료"} # return 값 json으로 전달 되게끔 셋팅
    # return UserService.create(userRegister=userRegister)


# 로그인 화면
@router.post("/login", response_model=UserBase.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                 db:Session = Depends(get_db)):
    # 이메일 & 비밀번호 확인
    existing_user = UserService.userLogin(db, form_data.email)
    if not existing_user or not bcrypt_context.verify(form_data.password, UserBase.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="아이디 또는 비밀번호가 일치하지 않습니다.", # 에러 메시지로 가게끔 셋팅
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    # token 생성
    data = {
        "sub": existing_user.email,
        "exp": datetime.utcnow() + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    access_token = jwt.encode(data, Config.JWT_SECRET_KEY, Config.ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": UserBase.username
        }

