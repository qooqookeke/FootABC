from fastapi import HTTPException, logger
from config import Config
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)
service_sid = Config.TWILIO_VERIFY_SERVICE_SID

# 검증 문자 전송
def send_verification(phone: str):
    send_verification = client.verify.v2.services(
        service_sid).verifications.create(
            to='+82'+phone, channel="sms")
        
    print(send_verification.sid)
    print(send_verification.send_code_attempts)
    print(send_verification.status)
    

# 검증 문자 확인
def check_verification(phone: str, code: str) -> bool:
    verification_check = client.verify.v2.services(
    service_sid
    ).verification_checks.create(to='+82'+phone, code=code)
    
    if verification_check.status == 'approved':
        print('본인인증 완료')
        return 
    else: 
        print('본인인증 실패')
