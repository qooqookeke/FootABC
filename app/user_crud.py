from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.future import select
from app.user_schema import UserCreate, LoginBase, idFindForm_email, idFindform_sms, pwFindForm_email, pwFindForm_sms, setNewPw
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
            result = await db.execute(select(User).filter(User.userId == login_base.username))
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
        
    
    # 비번 찾기 -> 비번 변경  
    @classmethod
    async def settingpw(cls, set_newpw: setNewPw, db: AsyncSession):
        db_user = User(
            hashed_pw = pwd_context.hash(set_newpw.new_pw1))
        db.commit()
        db.refresh(db_user)
        return db_user
    
    
    # @classmethod
    # async def gpt_result(cls, userId: str, gpt_result: gptScript, db:AsyncSession):
    #     db_result = gptScript(
    #         userId = 
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
    

