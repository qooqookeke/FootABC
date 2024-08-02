from datetime import datetime
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.future import select
from app.user_schema import UserCreate, LoginBase, idFindForm_email, idFindform_sms, pwFindForm_email, pwFindForm_sms, updatePw, gptBase, UserIdForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_models import User
from sqlalchemy.orm import Session
from sqlalchemy import or_

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    # 이메일 중복 확인
    @classmethod
    async def get_existing_user(cls, db: AsyncSession, userId: str, email: str, phone: str):
        result = await db.execute(select(User).filter(or_(User.userId == userId, User.email == email, User.phone == phone)))
        return result.scalar_one_or_none()
    
    # 회원 가입
    @classmethod
    async def userCreate(cls, db: AsyncSession, user_create: UserCreate):
        
        db_user = User(
            userId=user_create.userId,
            email=user_create.email, 
            hashed_pw=pwd_context.hash(user_create.password1),
            phone=user_create.phone,
            username=user_create.username,
            created_at=datetime.now()
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)        
        return db_user
        
    # 로그인
    @classmethod
    async def userLogin(cls, login_base: LoginBase, db: AsyncSession):
        async with db.begin():
            result = await db.execute(select(User).filter(User.userId == login_base.userId))
            return result.scalars().first()
        

    # 아이디 찾기
    @classmethod
    async def userIdFind_email(cls, id_find: idFindForm_email, db: AsyncSession):
        async with db.begin():
            emailVerify = await db.execute(select(User).filter(User.username == id_find.username, User.email == id_find.email))
            return emailVerify.scalars().first()
            
    @classmethod
    async def userIdFind_sms(cls, id_find: idFindform_sms, db: AsyncSession):
        async with db.begin():
            phoneVerify = await db.execute(select(User).filter(User.username == id_find.username, User.phone == id_find.phone))
            return phoneVerify.scalars().first()
    
    
    # 비번 찾기
    @classmethod
    async def userPwFind_email(cls, pw_find: pwFindForm_email, db:AsyncSession):
        async with db.begin():
            emailVerify = await db.execute(select(User).filter(User.userId == pw_find.userId, User.username == pw_find.username, User.email == pw_find.email))
            return emailVerify.scalars().first()
    
    @classmethod
    async def userPwFind_sms(cls, pw_find: pwFindForm_sms, db:AsyncSession):
        async with db.begin():
            phoneVerify = await db.execute(select(User).filter(User.userId == pw_find.userId, User.username == pw_find.username, User.phone == pw_find.phone))
            return phoneVerify.scalars().first()
        
    
    # 이메일 아이디 찾기 결과
    @classmethod
    async def userIdFind_email(cls, id_find: UserIdForm, db: AsyncSession):
        async with db.begin():
            stmt = select(User).filter(User.username == id_find.username, User.email == id_find.email)
            user = await db.execute(stmt)
            return user.scalars().first()
    
    # sms 아이디 찾기 결과
    @classmethod
    async def userIdFind_phone(cls, id_find: UserIdForm, db: AsyncSession):
        async with db.begin():
            stmt = select(User).filter(User.username == id_find.username, User.phone == id_find.phone)
            user = await db.execute(stmt)
            return user.scalars().first()
    
    # 이메일 비번 찾기 -> 비번 변경  
    @classmethod
    async def updatePw_email(cls, pwForm: pwFindForm_email, set_newpw: updatePw, db: AsyncSession):
        async with db.begin():
            stmt = select(User).filter(User.userId == pwForm.userId, User.username == pwForm.username, User.email == pwForm.email)
            result = await db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="일치하는 계정을 찾을 수 없습니다.")
            user.hashed_pw = pwd_context.hash(set_newpw.new_pw1)
            await db.commit()
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    
    # sms 비번 찾기 -> 비번 변경  
    @classmethod
    async def updatePw_sms(cls, pwReset: pwFindForm_sms, set_newpw: updatePw, db: AsyncSession):
        async with db.begin():
            stmt = select(User).filter(User.userId == pwReset.userId, User.username == pwReset.username, User.phone == pwReset.phone)
            result = await db.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="일치하는 계정을 찾을 수 없습니다.")
            user.hashed_pw = pwd_context.hash(set_newpw.new_pw1)
            await db.commit()
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    
    # gpt 분석 (데이터베이스 저장 여부 확인, 데이터베이스 모델 필요)
    # @classmethod
    # async def gpt_result(cls, userId: str, gpt_result: gptBase, db:AsyncSession):
    #     db_result = gpt_result(
    #         userId = gpt_result.userId,
    #         custom_id = gpt_result.custom_id,
    #         custom_size = gpt_result.custom_size,
    #         content = gpt_result.content
    #     )
    #     db.commit()
    #     db.refresh(db_result)
    #     return db_result
    
    
    # # 회원 인증
    # @classmethod
    # def userAuthenticate(cls, db: AsyncSession, userId: str, password: str):
    #     user = db.query(user.User).filter(
    #         (user.User.userId == userId | user.User.password == password)).first()
    #     if not user or not pwd_context.verify(password, user.password):
    #         return None
    #     return user


    # #회원 정보 업데이트
    # @classmethod
    # def userUpdate(cls, db: Session, user_id: int, new_data: UserCreate):
    #     user = db.query(User).filter(User.id == user_id).first()
    #     if not user:
    #         return None
    #     user.username = new_data.username
    #     user.email = new_data.email
    #     db.commit()
    #     return user
    
    
    # # 회원 정보 삭제
    # @classmethod
    # def userDelete(cls, db: Session, user_id: int):
    #     user = db.query(User).filter(User.id == user_id).first()
    #     if not user:
    #         return None
    #     db.delete(user)
    #     db.commit()
    #     return True
    

