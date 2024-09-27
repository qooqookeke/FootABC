import os
import time
from datetime import datetime
from typing import List

from fastapi import (APIRouter, Depends, File, HTTPException,
                    Request, UploadFile)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analysis_inference_medi import predict_and_save as medi_predict
from app.ai.gpt import create_prompt
from app.s3 import s3Upload
from app.user_database import get_db
from app.user_schema import (gptBase)

router = APIRouter()

# 메모리 저장
memory_store = []


def filter_images_by_content_type(images: List[UploadFile]) -> List[tuple]:
    indexed_images = [
        (index, image)
        for index, image in enumerate(images)
        if image.headers.get('content-type') != 'application/x-empty'
    ]
    
    return indexed_images


# 이미지 분석 처리
@router.post("/analyze/")
async def analyze(request: Request, images: List[UploadFile] = File(...), db: AsyncSession = Depends(get_db)):
    
    start_time = time.time()
    print(start_time)
    
    # 평발 : Lmedi
    # 무지외반 : supe
    # 발목 불안 : ankl
    # 하지정렬 : bla
    
    filtered_images = filter_images_by_content_type(images)

    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    input_dir = '../FootABC/images/input/'
    os.makedirs(input_dir, exist_ok=True)
    output_dir = '../FootABC/images/output/'
    os.makedirs(output_dir, exist_ok=True)
    
    for directory in [input_dir, output_dir]:
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print("폴더 삭제 완료")
                    
                    
                    
    input_filenames = []
    output_filenames = []
    for index, image in filtered_images:
        contents = await image.read()
        filename = f'{current_date}_{index}.jpg'
        file_path = os.path.join(input_dir, filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        input_filenames.append(f'input_{current_date}_{index}.jpg')
        
    middle_time = time.time()
    print(start_time - middle_time)
    
    # 이미지 분석
    try:
        mediAnalyze = [
            (index, os.path.join(input_dir, f"{current_date}_{index}.jpg"))
            for index, _ in filtered_images
            if index in [0, 1]
        ]
        # supeAnalyze = [
        #     (index, os.path.join(input_dir, f"{current_date}_{index}.jpg"))
        #     for index, _ in filtered_images
        #     if index in [2, 3]
        # ]
        # anklAnalyze = [
        #     (index, os.path.join(input_dir, f"{current_date}_{index}.jpg"))
        #     for index, _ in filtered_images
        #     if index in [4, 5]
        # ]
        # blaAnalyze = [
        #     (index, os.path.join(input_dir, f"{current_date}_{index}.jpg"))
        #     for index, _ in filtered_images
        #     if index in [6]
        # ]
        
        if mediAnalyze:
            await medi_predict(mediAnalyze, output_dir) 
            
            for output_filename in os.listdir(output_dir):
                output_filenames.append(output_filename)
            uploaded_urls = await s3Upload(mediAnalyze, output_dir, input_filenames, output_filenames)
            
            memory_store.append(uploaded_urls)
            
        # elif supeAnalyze:
            # await supe_predict(supeAnalyze, output_dir)
        #     uploaded_urls = await s3Upload(supeAnalyze, output_dir, input_filenames, output_filenames)

        # elif anklAnalyze:
            # ankl_predict(anklAnalyze, output_dir)
            
        # elif ante:
            # supe_predict(input_dir, output_dir)
    
            # 데이터베이스 저장
            # await UserService.save_analysis_result(username, userResult, db)
        
        # s3 한번에 저장
        # for output_filename in os.listdir(output_dir):
        #         output_filenames.append(output_filename)
        #     uploaded_urls = await s3Upload(mediAnalyze, output_dir, input_filenames, output_filenames)

            end_time = time.time()
            print(middle_time - end_time)
        
            return JSONResponse(status_code=200, content=uploaded_urls)
        else:
            return JSONResponse(status_code=400, content={'error': 'No input files provided'})
        
    except Exception as e:
        print(e)
        return {'error': 'Image analysis failed'}, 500


# 결과 페이지 사용 여부 확인(데이터베이스 적용 여부)
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