from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from pydantic import BaseModel
from db import Base
from db import ENGINE
from typing import List
from typing import Optional
from datetime import datetime


class UserTable(Base):
    __tablename__ = 'user'
    index = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(45))
    id = Column(String(200))
    password = Column(String(45))
    nickname = Column(String(45))
    gender = Column(String(45))
    birthday = Column(String(45))
    birthdayYear = Column(String(45))
    mobile = Column(String(45))
    address = Column(String(500))
    timestamp = Column(DateTime)


class User(BaseModel):
    type: str = None
    id: str = None
    password: str = None
    nickname: str = None
    gender: str = None
    birthday: str = None
    birthdayYear: str = None
    mobile: str = None
    address: str = None


class LoginInfo(BaseModel):
    id: str
    password: str


class SocialLoginInfo(BaseModel):
    id: str
    type: str


def create_user_table(item: User) -> UserTable:
    user = UserTable()
    user.type = item.type
    user.id = item.id
    user.password = item.password
    user.nickname = item.nickname
    user.gender = item.gender
    user.birthday = item.birthday
    user.birthdayYear = item.birthdayYear
    user.address = item.address
    user.mobile = item.mobile
    user.timestamp = datetime.now()

    return user

