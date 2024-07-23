from typing import Any, List, Union, Optional
from pydantic import BaseModel, field_validator, EmailStr, Field
from pydantic_core.core_schema import FieldValidationInfo
from datetime import datetime
from fastapi import HTTPException
from email_validator import EmailNotValidError, validate_email


class UserBase(BaseModel):
    userId: str
    email: EmailStr
    username: str
    phone: str
    password1: str
    password2: str

# 회원 가입
class UserCreate(UserBase):
    
    @field_validator('userId', 'email', 'username', 'phone', 'password1', 'password2')
    def check_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="빈 칸을 채워주세요")
        return v
        
    @field_validator('phone')
    def vailation_phone(cls, v):
        if len(v) != 11:
            raise HTTPException(status_code=422, detail="전화번호를 다시 확인해주세요.")
        return v
    
    @field_validator('password1')
    def validate_password(cls, v):
        if len(v) < 6:
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")        
        if not any(char.isdigit() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")        
        if not any(char.isalpha() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        password1 = info.data.get('password1')
        if password1 and v != password1:
            raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
        return v

    class Config:
        from_attributes = True
        
        
# 로그인
class LoginBase(UserBase):
    
    @field_validator('userId', 'password1')
    def check_empty(cls, v):
        if not v:
            raise HTTPException(status_code=422, detail="아이디와 비밀번호를 입력해주세요.")
        return v


# 토큰 처리
class Token(BaseModel):
    access_token: str
    token_type: str
    userId: str
    msg: str
    
class tokenData(BaseModel):
    username: str | None = None


# 인증 관련
class Verificationemail(BaseModel):
    email: EmailStr
    verify_code: str

class Verificationsms(BaseModel):
    phone: str
    verify_code: str


# 아이디 찾기
class idFindForm_email(BaseModel):
    username: str
    email: EmailStr
    
    @field_validator('username', 'email')
    def check_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="이름과 이메일 주소를 입력해주세요.")
        return v

class idFindform_sms(BaseModel):
    username: str
    phone: str
    
    @field_validator('username', 'phone')
    def check_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="이름과 휴대전화번호를 입력해주세요.")
        return v


# 비번 찾기
class pwFindForm_email(BaseModel):
    userId: str
    username: str
    email: EmailStr

    @field_validator('userId', 'username', 'email')
    def check_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="빈 칸을 채워주세요.")
        return v
        
        
class pwFindForm_sms(BaseModel):
    userId: str
    username: str
    phone: str
    
    @field_validator('userId', 'username', 'phone')
    def check_empty(cls, v):
        if not v or not v.strip():
            raise HTTPException(status_code=422, detail="빈 칸을 채워주세요.")
        return v


# 비번 찾기 -> 비번 변경
class setNewPw(UserBase):
    new_pw1 : str
    new_pw2 : str
    
    @field_validator('new_pw1')
    def validate_password(cls, v):
        if len(v) < 6:
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")        
        if not any(char.isdigit() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")        
        if not any(char.isalpha() for char in v):
            raise HTTPException(status_code=422, detail="비밀번호는 6자리 이상 영문과 숫자를 포함하여 작성해주세요.")
        return v
    
    @field_validator('new_pw2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        password1 = info.data.get('new_pw1')
        if password1 and v != password1:
            raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
        return v
    
    
# class resultBase(BaseModel):
#     userId: str
#     custom_id: str
#     custom_size: str
#     content: str