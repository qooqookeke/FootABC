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

    # # 테이블간 연결 생성
    # userId = relationship("result", back_populates="owner")


# 분석 결과
class result(Base):
    __tablename__ = "result"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, primary_key=True)
    LtSupe = Column(String)
    RtSupe = Column(String)
    LtSupeInUrl = Column(String)
    LtSupeOutUrl = Column(String)
    RtSupeInUrl = Column(String)
    RtsupeOutUrl = Column(String)
    LtMedi = Column(String)
    RtMedi = Column(String)
    LtMediInUrl = Column(String)
    LtMediOutUrl = Column(String)
    RtMediInUrl = Column(String)
    RtMediOutUrl = Column(String)
    LtAnkl = Column(String)
    RtAnkl = Column(String)
    LtAnklInUrl = Column(String)
    LtAnklOutUrl = Column(String)
    RtAnklInUrl = Column(String)
    RtAnklOutUrl = Column(String)
    Bla = Column(String)
    blaInUrl = Column(String)
    blaOutUrl = Column(String)
    created_at = Column(DateTime, default=datetime.now)


# gpt 분석
# class gptScript(Base):
#     content: str

# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.owner_id"))

#     owner = relationship("User", back_populates="items")
    