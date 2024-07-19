from fastapi import APIRouter, HTTPException, Depends, Request, Response
from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config import Config

from app.user_database import get_db
from app.user_schema import UserCreate, UserBase, Token
from app.user_crud import UserService, pwd_context

router = APIRouter(
    prefix='/user',
    tags=['user']
)

# 회원가입
@router.post("/create")
async def user_create(userCreate: UserCreate, db: AsyncSession = Depends(get_db)):    
    existing_user = await UserService.get_existing_user(db, userCreate.userId, userCreate.email, userCreate.phone)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    await UserService.userCreate(db, userCreate)
    return {"detail": "회원가입이 완료되었습니다."}


# 로그인
@router.post("/login", response_model=Token)
async def login(login_form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userLogin(login_form.username, login_form.password, db)    
    if not existing_user or not pwd_context.verify(login_form.password, existing_user.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    # token 생성
    data = {
        "sub": existing_user.username,
        "exp": datetime.now() + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    access_token = jwt.encode(data, Config.JWT_SECRET_KEY, Config.ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userId": existing_user.userId,
        "msg": "로그인 완료입니다."
        }


# 로그아웃
@router.get("/logout")
async def logout(response: Response, request: Request):
    request.cookies.get("access_token")
    response.delete_cookie(key="access_token")
    return HTTPException(status_code=status.HTTP_200_OK, detail="로그아웃 완료입니다.")


# 아이디 찾기
@router.get("/findid")
async def findid(user_find: userFind, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userLogin(login_form.username, login_form.password, db)
    
    return {"userId": existing_user.userId}

# 비번 찾기
@router.get("/findpw")