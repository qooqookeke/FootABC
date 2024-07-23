from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
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

    # 컬럼 연결시 사용
    # items = relationship("Item", back_populates="owner")



# class gptScript(Base):
#     content: str

# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.owner_id"))

#     owner = relationship("User", back_populates="items")
    