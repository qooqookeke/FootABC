from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.user_database import Base

from datetime import datetime


# 유저 정보
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, unique=True) 
    email = Column(String, unique=True)   
    username = Column(String)
    phone = Column(String)
    hashed_pw = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    # 속성과 연관된 다른 테이블의 속성값 연결
    # items = relationship("Item", back_populates="owner")


# 분석 결과
# class result(Base):
#     __tablename__ = "result"
#     id = Column(Integer, primary_key=True, index=True)
#     Ltsup = Column(Integer)
#     Rtsup = Column(Integer)
#     LtMed = Column(Integer)
#     RtMed = Column(Integer)
#     LtAnk = Column(Integer)
#     RtAnk = Column(Integer)
#     Bla = Column(Integer)
#     created_at = Column(DateTime, default=datetime.now)


# gpt 분석
# class gptScript(Base):
#     content: str

# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.owner_id"))

#     owner = relationship("User", back_populates="items")
    