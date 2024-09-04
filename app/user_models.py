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
class AnalysisResult(Base):
    __tablename__ = "result"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer)
    LtSupe = Column(String(45))
    RtSupe = Column(String(45))
    LtSupeInUrl = Column(String(255))
    LtSupeOutUrl = Column(String(255))
    RtSupeInUrl = Column(String(255))
    RtsupeOutUrl = Column(String(255))
    LtMedi = Column(String(45))
    RtMedi = Column(String(45))
    LtMediInUrl = Column(String(255))
    LtMediOutUrl = Column(String(255))
    RtMediInUrl = Column(String(255))
    RtMediOutUrl = Column(String(255))
    LtAnkl = Column(String(45))
    RtAnkl = Column(String(45))
    LtAnklInUrl = Column(String(255))
    LtAnklOutUrl = Column(String(255))
    RtAnklInUrl = Column(String(255))
    RtAnklOutUrl = Column(String(255))
    Bla = Column(String(45))
    blaInUrl = Column(String(255))
    blaOutUrl = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)


# gpt 분석
# class gptScript(Base):
#     content: str

# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.owner_id"))

#     owner = relationship("User", back_populates="items")
    