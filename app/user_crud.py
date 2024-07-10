from passlib.context import CryptContext
from app.user_schema import UserCreate
from app.user_models import User    
from sqlalchemy.orm import Session


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:

    # 회원 가입
    @classmethod
    def userCreate(cls, db: Session, user_create: UserCreate):
        db_user = User(email=user_create.email, 
                       password=bcrypt_context.hash(user_create.password1),
                       username=user_create.username)
        db.add(db_user)
        db.commit()
    
    # 이메일 중복값에 대한 조회
    def get_existing_user(db: Session, user_create: UserCreate):
        return db.query(User).filter(
            (User.email == user_create.email)).first()


    # 회원 인증
    @classmethod
    def userAuthenticate(cls, db: Session, email: str, password: str):
        user = db.query(user.User).filter(
            (user.User.email == email | user.User.password == password)).first()
        if not user or not bcrypt_context.verify(password, user.password):
            return None
        return user
    
    # 로그인
    @classmethod
    def userLogin(cls, db: Session, email: str, password: str):
        return db.query(User).filter(User.email == email).first()


    #회원 정보 업데이트
    @classmethod
    def userUpdate(cls, db: Session, user_id: int, new_data: UserCreate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.username = new_data.username
        user.email = new_data.email
        db.commit()
        return user
    
    
    # 회원 정보 삭제
    @classmethod
    def userDelete(cls, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        db.delete(user)
        db.commit()
        return True
    

