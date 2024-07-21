from config import Config
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

message = client.messages.create(
    from_="+15017122661", # 보내는 번호 (발급받은 trial number)
    to="+15558675310", # 문자 받을 번호 +821012341234
    body="문자 보낼 내용", # 문자 보낼 내용
)

print(message.body)