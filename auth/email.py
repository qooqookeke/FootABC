import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from typing import Dict
import random
import string
import os

# Gmail 계정 설정
gmail_user = Config.GMAILADDRESS  
gmail_password = Config.GMAILAPPPW 

verification_codes: Dict[str, str] = {}

def generate_verification_token() -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# 이메일 보내는 함수
def send_email(email: str):
    verification_token = generate_verification_token()
    verification_codes[email] = verification_token

    # 이메일 내용 설정
    sender_email = gmail_user
    receiver_email = email
    subject = '이메일 인증'
    body = f'인증 코드: {verification_token}'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        # SMTP 서버 설정 (Gmail)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f'이메일 전송 성공 : {body}')

    except Exception as e:
        print(f'이메일 전송 실패. 오류 메시지: {str(e)}')
            

    # 테스트용 이메일 주소
    # test_email = 'recipient@example.com'  # 수신자 이메일 주소
    # send_email(test_email)

# 인증번호 확인하는 함수
def verify_code(email: str, code: str) -> bool:
    return verification_codes.get(email) == code