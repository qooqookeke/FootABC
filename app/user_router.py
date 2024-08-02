from io import BytesIO
import os
import shutil
import boto3
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends, Request, Response, BackgroundTasks, File, UploadFile
from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config import Config
from fastapi.responses import JSONResponse

from app.user_database import get_db
from app.user_schema import UserCreate, LoginBase, Token, idFindForm_email, idFindform_sms, pwFindForm_email, pwFindForm_sms, Verificationemail, Verificationsms, updatePw, gptBase
from app.user_crud import UserService, pwd_context
from auth.email import send_email, verify_code
from auth.sms import send_verification, check_verification
from gpt import post_gpt, create_prompt


router = APIRouter()

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
async def login(userLogin: LoginBase, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userLogin(userLogin, db)    
    if not existing_user or not pwd_context.verify(userLogin.password, existing_user.hashed_pw):
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
@router.post("/findId_phone")
async def findIdSms(body: idFindform_sms, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_sms(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    send_verification(body.phone)
    return {"msg": f"{body.phone}로 본인인증 코드가 전송되었습니다."}

# sms 비번 찾기(변경)
@router.post("/findPw_phone")
async def findPwSms(body: pwFindForm_sms, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userPwFind_sms(body.username, body.phone, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 아이디가 존재하지 않습니다.")
    send_verification(body.phone)
    return {"msg": f"{body.phone}로 본인인증 코드가 전송되었습니다."}
    

# sms 코드 인증 확인
@router.post("/verify-sms/")
def check_verification_code(request: Verificationsms):
    check = check_verification(request.phone, request.verify_code)
    return check


# 이메일 아이디 찾기
@router.post("/find_id/email")
async def findIdEmail(body: idFindForm_email, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    background_tasks.add_task(send_email, body.email)
    return {"msg": f"{body.email}로 본인인증 이메일이 전송되었습니다."}

# 이메일 비번 찾기(변경)
@router.post("/find_pw/email")
async def findPwEmail(body: pwFindForm_email, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    print(body)
    existing_user = await UserService.userPwFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="일치하는 계정 정보가 존재하지 않습니다.")
    background_tasks.add_task(send_email, body.email)
    return {"msg": f"{body.email}로 본인인증 이메일이 전송되었습니다."}


# 이메일 코드 인증 확인
@router.post("/verify-email/")
def verification_email_code(request: Verificationemail):
    if verify_code(request.email, request.verify_code):
        return {"msg": "본인인증을 성공하였습니다."}
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 인증코드입니다.")


# 이메일 아이디 찾기 결과 -> 아이디 조회 확인
@router.post("/find_id/email/result")
async def find_id(body: idFindForm_email, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="계정정보를 다시 확인해주세요.")
    return {"msg": f"계정 아이디는 {existing_user.userId} 입니다."}


# sms 아이디 찾기 결과 -> 아이디 조회 확인
@router.post("/find_id/phone/result")
async def find_id(body: idFindform_sms, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userIdFind_phone(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="계정정보를 다시 확인해주세요.")
    return {"msg": f"계정 아이디는 {existing_user.userId} 입니다."}


# 이메일 비번 찾기 결과 -> 새로운 비번 설정
@router.post("/find_pw/email/password-reset/")
async def reset_password(body: pwFindForm_email, newPw: updatePw, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userPwFind_email(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="계정정보를 다시 확인해주세요.")
    await UserService.updatePw_email(body, newPw, db)
    return {"msg": "비밀번호가 성공적으로 변경되었습니다."}


# sms 비번 찾기 결과 -> 새로운 비번 설정
@router.post("/find_pw/phone/password-reset/")
async def reset_password(body: pwFindForm_sms, newPw: updatePw, db: AsyncSession = Depends(get_db)):
    existing_user = await UserService.userPwFind_sms(body, db)
    if not existing_user:
        raise HTTPException(status_code=401, detail="계정정보를 다시 확인해주세요.")
    await UserService.updatePw_sms(body, newPw, db)
    return {"msg": "비밀번호가 성공적으로 변경되었습니다."}


# 분석 이미지 업로드
@router.post("/analyze/")
async def analyze(request: Request, background_tasks: BackgroundTasks, 
                     LtSup: UploadFile = File(...), RtSup: UploadFile = File(...), 
                     LtMed: UploadFile = File(...), RtMed: UploadFile = File(...), 
                     LtAnk: UploadFile = File(...), RtAnk: UploadFile = File(...), Bla: UploadFile = File(...)):
    # 업로드 이미지 확인
    # if not any([RtSup, LtSup, LtMed, RtMed, LtAnk, RtAnk, Bla]):
    #     return {"detail": "이미지 없음"}
    
    current_date = datetime.now()
    
    # 로컬 저장 경로
    # img_dir = '/input'
    # os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'LtSup': LtSup,
        'RtSup': RtSup,
        'LtMed': LtMed,
        'RtMed': RtMed,
        'LtAnk': LtAnk,
        'RtAnk': RtAnk,
        'Bla': Bla
    }

    # # 로컬 저장
    # for key, file in files.items():
    #     if file:
    #         file_path = os.path.join(img_dir, filenames[key])
    #         with open(file_path, "wb") as buffer:
    #             shutil.copyfileobj(file.file, buffer)

    # image_content = await files.read()
    
    # s3 저장
    s3 = boto3.client('s3',
                        aws_access_key_id = Config.AWS_ACCESS_KEY,
                        aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        
    try:
        for key, file in files.items():
            if file:
                filename = f'{key}_{current_date.strftime("%y%m%d%H%M%S")}.jpg'
                s3.upload_fileobj(file.file, Config.S3_BUCKET,
                                filename,
                                ExtraArgs = {'ACL':'public-read',
                                        'ContentType':'image/jpeg'})
        print("파일 업로드 완료")
        
    except Exception as e:
        print(e)
        return {'error':str(e)}, 500
    
    # 이미지 분석
    # result = subprocess.run(["python", "inference_web.py"], capture_output=True, text=True)
    
    return {"detail": "분석이 완료되었습니다."}


# 이미지 분석 결과(평발 or 요족: 각도 / 발목 불안정성 / 다리모양) 
# 데이터베이스 구축 예정
@router.post("/result/")
async def result(request: Request):
    
    return request



# gpt 분석
@router.post("/gpt/", response_class=JSONResponse)
async def create_gpt(request: Request, data: gptBase):
    try:
        # 요청 본문을 로깅하여 확인
        request_body = await request.json()
        print("요청 본문:", request_body)

        content = create_prompt(data.content)
        if content is None:
            raise HTTPException(status_code=204, detail="Something went wrong")

        response_data = {
            "status": 200,
            "content": content
        }
    except HTTPException as e:
        response_data = {
            "status": e.status_code,
            "data": "다시 시도해주세요."
        }
    return JSONResponse(content=response_data)