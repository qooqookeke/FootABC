from fastapi import APIRouter, HTTPException, Depends, Request, Response, BackgroundTasks
from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config import Config
from fastapi.responses import JSONResponse
# from gpt import create_prompt

from app.user_database import get_db
from app.user_schema import UserCreate, UserBase, Token, idFindForm_email, idFindform_sms, pwFindForm_email, pwFindForm_sms, Verificationemail, Verificationsms, setNewPw
from app.user_crud import UserService, pwd_context
from auth.email import send_email, verify_code
from auth.sms import verify_send_sms, verify_sms


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
    existing_user = await UserService.userLogin(login_form, db)    
    if not existing_user or not pwd_context.verify(login_form.password, existing_user.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
            )
    
    # token 생성
    data = {
        "sub": existing_user.username,
        "exp": datetime.now() + timedelta(minutes=int(Config.JWT_ACCESS_TOKEN_EXPIRES))
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


# sms 아이디 찾기
@router.post("/find_id/phone")
async def findIdSms(body: idFindform_sms, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_sms(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    verify_send_sms(body.phone)
    return {"msg": f"{body.phone}로 본인인증 코드가 전송되었습니다."}

# sms 비번 찾기(변경)
@router.post("/find_pw/phone")
async def findPwSms(body: pwFindForm_sms, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userPwFind(body.username, body.phone, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 아이디가 존재하지 않습니다.")
    verify_send_sms(body.phone)
    return {"msg": f"{body.phone}로 본인인증 코드가 전송되었습니다."}
    

# sms 코드 인증 확인
@router.post("/verify-sms/")
def check_verification_code(request: Verificationsms):
    if not verify_sms(sms=request.phone, code=request.verify_code):
        raise HTTPException(status_code=400, detail="유효하지 않은 인증코드입니다.")
    return {"msg": "본인인증을 성공했습니다."}


# 이메일 아이디 찾기
@router.post("/find_id/email")
async def findIdEmail(body: idFindForm_email, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    send_email(body.email)
    return {"msg": f"{body.email}로 본인인증 이메일이 전송되었습니다."}

# 이메일 비번 찾기(변경)
@router.post("/find_pw/email")
async def findPwEmail(body: pwFindForm_email, db: AsyncSession = Depends(get_db)):
    print(body)
    existing_user = await UserService.userPwFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    send_email(body.email)
    return {"msg": f"{body.email}로 본인인증 이메일이 전송되었습니다."}


# 이메일 코드 인증 확인
@router.post("/verify-email/")
def verification_email_code(request: Verificationemail):
    if verify_code(request.email, request.verify_code):
        return {"msg": "본인인증을 성공하였습니다."}
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 인증코드입니다.")


# 아이디 찾기 결과 -> 아이디 조회 확인
# @router.get("/find_id/result")
# def findIdResult(re) 

# # 비번 찾기 결과 -> 새로운 비번 설정
# @router.post("/password-reset/")
# def reset_password(request: setNewPw, db: AsyncSession = Depends(get_db)):
#     if not verify_sms(request.email, request.code):
#         raise HTTPException(status_code=400, detail="Invalid verification code")
#     user = UserService.settingpw(db, email=request.email, new_password=request.new_password)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"msg": "Password reset successful"}


# 분석 이미지 업로드
# @router.post("/uploadimages/")
# async def create_gpt(request: Request, Rt sup: File:(...), Lt sup: File(...), )

# # gpt 분석
# @router.post("/gpt/", response_class=JSONResponse)
# async def create_gpt(request: Request, data: gptScript):
#     try:
#         # 요청 본문을 로깅하여 확인
#         request_body = await request.json()
#         print("요청 본문:", request_body)

#         # 데이터 검증
#         data = gptScript(**request_body)
#         print("검증된 데이터:", data)

#         print(data)
#         content = create_prompt(data.content)
#         if content is None:
#             raise HTTPException(status_code=204, detail="Something went wrong")

#         response_data = {
#             "status": 200,
#             "content": content
#         }
#     except HTTPException as e:
#         response_data = {
#             "status": e.status_code,
#             "data": "다시 시도해주세요."
#         }
#     return JSONResponse(content=response_data)
