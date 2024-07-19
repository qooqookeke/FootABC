from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.future import select
from app.user_schema import UserCreate, LoginBase
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
    async def userLogin(cls, userId: str, hashed_pw: str, db: AsyncSession):
        async with db.begin():
            result = await db.execute(select(User).filter(User.userId == userId))
            return result.scalars().first()

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
    

