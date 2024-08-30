from io import BytesIO
import os
import random
import shutil
import subprocess
import boto3
from typing import Annotated, List, Optional
import cv2
from fastapi import APIRouter, HTTPException, Depends, Request, Response, BackgroundTasks, File, UploadFile, Response
from datetime import timedelta, datetime


from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.ai.analysis_inference_medi import predict_and_save as medi_predict
from config import Config
from fastapi.responses import FileResponse, JSONResponse
from app.s3 import s3Upload

from app.user_database import get_db
from app.user_schema import UserCreate, LoginBase, Token, idFindForm_email, idFindform_sms, pwFindForm_email, pwFindForm_sms, Verificationemail, Verificationsms, updatePw, resultBase, gptBase
from app.user_crud import UserService, pwd_context
from auth.email import send_email, verify_code
from auth.sms import send_verification, check_verification
from app.ai.gpt import post_gpt, create_prompt
# from analysis_inference_n1 import predict_and_save


router = APIRouter()

# 메모리 저장
memory_store = []

# 회원가입
@router.post("/create")
async def user_create(userCreate: UserCreate, db: AsyncSession = Depends(get_db)):    
    existing_user = await UserService.get_existing_user(db, userCreate.userId, userCreate.email, userCreate.phone)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    await UserService.userCreate(db, userCreate)
    return {"detail": "회원가입이 완료되었습니다."}


# 로그인(id:aaa111, pw:a123456)
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
    print(access_token)
    
    # 쿠키에 토큰 설정
    response = JSONResponse(content={
        "userId": existing_user.userId,
        "msg": "로그인 완료입니다."
    })
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        # secure=True, 
        samesite="none"
    )

    return response


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


def filter_images_by_content_type(images: List[UploadFile]) -> List[tuple]:
    indexed_images = [
        (index, image)
        for index, image in enumerate(images)
        if image.headers.get('content-type') != 'application/x-empty'
    ]
    
    return indexed_images

# 이미지 분석 처리
@router.post("/analyze/")
async def analyze(request: Request,  images: List[UploadFile] = File(...) ):
    # result: resultBase, db:AsyncSession = Depends(get_db),
    
    # 평발 : Lmedi
    # 무지외반 : supe
    # 발목 불안 : ankl
    # 하지정렬 : bla
    
    filtered_images = filter_images_by_content_type(images)
    print(filtered_images)

    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    input_dir = 'D:/GitHub/FootABC/images/input/'
    os.makedirs(input_dir, exist_ok=True)
    output_dir = 'D:/GitHub/FootABC/images/output/'
    os.makedirs(output_dir, exist_ok=True)
    
    for directory in [input_dir, output_dir]:
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        
    for _, image in filtered_images:  # file -> image로 변경
        contents = await image.read()  # 이제 올바른 image 객체에 대해 read 호출
        filename = f'{current_date}_{random.randrange(999)}.jpg'
        file_path = os.path.join(input_dir, filename)
        with open(file_path, "wb") as f:
            f.write(contents)

    
    """ 
    이미지 전달 받을 때 리스트 형식으로 받고 content type이 empty인 것은 {} 빈 배열로 바꿔주고
    각 순서에 맞게 이미지 분석할 수 있도록 함
    학습시 오류가 날 수 있으므로 빈 배열로 온 것을 학습에 들어가지 않도록 셋팅
    """
    
    # 이미지 분석
    try:
        images_to_analyze = [image for index, image in enumerate(filtered_images) if index in [0, 1]]
        print(images_to_analyze)
        
        if images_to_analyze:
            await medi_predict(images_to_analyze, output_dir)
            uploaded_urls = await s3Upload(images, output_dir)
            # 데이터베이스 저장
            # await UserService.save_analysis_result(result, db)
            
            # 메모리에 분석 결과 저장
            analysis_result = {
                'in': uploaded_urls[0],
                'out': uploaded_urls[1],
                'in': uploaded_urls[2],
                'out': uploaded_urls[3]
            }
            memory_store.append(analysis_result)
            
            # return JSONResponse(status_code=200, content={
            #     'in': uploaded_urls[0],
            #     'out': uploaded_urls[1]
            # })
            return JSONResponse(status_code=200, content=analysis_result)
        else:
            return JSONResponse(status_code=400, content={'error': 'No input files provided'})
        # elif supe:
            # supe_predict(input_dir, output_dir)
        #     uploaded_urls = await s3Upload(medi, output_dir)
        #     return JSONResponse(status_code=200, content={
        #         'in': uploaded_urls[0],
        #         'out': uploaded_urls[1]
        #     })
        # else:
        #     return JSONResponse(status_code=400, content={'error': 'No input files provided'})
        # elif post:
            # supe_predict(input_dir, output_dir)
        # elif ante:
            # supe_predict(input_dir, output_dir)
    
    except Exception as e:
        print(e)
        return {'error': 'Image analysis failed'}, 500


# 결과 페이지
@router.post("/result/")
async def result(request: Request):
    # 데이터베이스에서 결과 조회
    # try:
    #     result = await UserService.get_analysis_result(result_id, db)
    #     if result:
    #         return JSONResponse(status_code=200, content={
    #             'result': result
    #         })
    #     else:
    #         raise HTTPException(status_code=404, detail='Result not found')
    
    # except Exception as e:
    #     print(e)
    #     return JSONResponse(status_code=500, content={'error': 'Failed to retrieve result'})
    
    # 메모리에서 결과 조회   
    if memory_store:
        latest_result = memory_store[-1]
        return JSONResponse(status_code=200, content={'results': latest_result})
    else:
        return JSONResponse(status_code=404, content={'error': 'No results found'})



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