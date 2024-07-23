from config import Config
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)
service_sid = Config.TWILIO_VERIFY_SERVICE_SID

class verify_send_sms:
    #검증 문자 전송
    def send_verification(phone: str):
        send_verification = client.verify \
            .v2 \
            .services(service_sid) \
            .verifications \
            .create(to=phone, channel='sms')  # to = 받는 사람 번호
        print(send_verification.sid)

class verify_sms:
    #검증 문자 확인
    def check_verification(phone: str, code: str):
        check_verification = client.verify \
            .v2 \
            .services(service_sid) \
            .verification_checks \
            .create(to=phone, code=code)
        print(check_verification.status)