import random
import boto3
from config import Config
from datetime import datetime
import os

# S3에 파일을 업로드하는 비동기 함수
async def s3Upload(medi, output_dir):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    uploaded_files_urls = []  # 업로드된 파일의 URL을 저장할 리스트
    
    # S3 클라이언트 설정
    s3 = boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )
    
    try:
        # 입력 파일을 S3에 업로드
        for image in medi:
            if image:
                image.file.seek(0)
                input_filename = f'input_{current_date}_{random.randint(0, 999)}.jpg'
                s3.upload_fileobj(
                    image.file, 
                    Config.S3_BUCKET, 
                    input_filename,
                    ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
                )
                # 업로드한 파일의 URL을 생성하여 리스트에 추가
                file_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{input_filename}"
                uploaded_files_urls.append(file_url)

        # 결과 파일을 S3에 업로드
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                output_filename = f'result_{current_date}_{random.randint(0, 999)}.jpg'
                s3.upload_file(
                    file_path, 
                    Config.S3_BUCKET, 
                    output_filename,
                    ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
                )
                # 업로드한 파일의 URL을 생성하여 리스트에 추가
                file_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{output_filename}"
                uploaded_files_urls.append(file_url)

        print("파일 업로드 완료")
        return uploaded_files_urls

    except Exception as e:
        print(f"S3 업로드 실패: {e}")
        return {'error': str(e)}, 500
