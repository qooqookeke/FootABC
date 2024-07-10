from typing import List, Union
from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo
from datetime import datetime


# 회원 가입
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password1: str
    password2: str

    @field_validator('username', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 칸을 채워주세요')
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v



# 로그인
class UserBase(BaseModel):
    id: int
    email = EmailStr
    username = str
    password:str

    @field_validator('email', 'password')
    def not_empty(cls, v):
        if not v:
            raise ValueError('이메일 또는 패스워드를 입력해주세요')
        return v
    
    class Config:
        from_attribute = True

# 토큰 처리
class Token(BaseModel):
    access_token: str
    token_type: str
    email:str
    
class tokenData(BaseModel):
    username: str | None = None



