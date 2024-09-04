import random
import boto3
from config import Config
from datetime import datetime
import os

async def s3Upload(mediAnalyze, output_dir, input_filenames, output_filenames):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    uploaded_files_urls = []  
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
    )
    
    try:
        for (index, image_path), input_filename in zip(mediAnalyze, input_filenames):
            if image_path:
                with open(image_path, 'rb') as f:
                    s3.upload_fileobj(
                        f, 
                        Config.S3_BUCKET, 
                        input_filename,
                        ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
                    )
                file_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{input_filename}"
                uploaded_files_urls.append(file_url)
                print(f"Uploaded input file: {file_url}")

        for output_filename in output_filenames:
            file_path = os.path.join(output_dir, output_filename)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    s3.upload_fileobj(
                        f, 
                        Config.S3_BUCKET, 
                        output_filename,
                        ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
                    )
                file_url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{output_filename}"
                uploaded_files_urls.append(file_url)
                print(f"Uploaded output file: {file_url}")
            else:
                print(f"File not found for output upload: {file_path}")

        print("파일 업로드 완료")
        
        input_urls = {}
        output_urls = {}
        
        for url in uploaded_files_urls:
                if 'input_' in url:
                    filename = url.split('/')[-1] 
                    index = filename.split('_')[-1].split('.')[0]  
                    input_urls[f'input_{index}'] = url
                elif 'result_' in url:
                    filename = url.split('/')[-1] 
                    index = filename.split('_')[-1].split('.')[0]
                    output_urls[f'output_{index}'] = url
                    
        analysis_result = {**input_urls, **output_urls}
        
        print(analysis_result)
        
        return analysis_result

    except Exception as e:
        print(f"S3 업로드 실패: {e}")
        return {'error': str(e)}, 500