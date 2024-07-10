from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.user_database import Base

from datetime import datetime


# 유저 정보
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, nullable=False)   
    username = Column(String, index=True)
    hased_password = Column(String, nullable=False)
    created_at = Column(str(datetime), nullable=False)

    # 컬럼 연결시 사용
    # items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.owner_id"))

#     owner = relationship("User", back_populates="items")
    