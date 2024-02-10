from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


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
    index: int = None
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


class LolketingUserTable(Base):
    __tablename__ = 'lolketing_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cash = Column(Integer)
    point = Column(Integer)
    grade = Column(String(50))
    roulette = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.index'))

    user = relationship("UserTable", foreign_keys=[user_id])


class LolketingUser(BaseModel):
    id: int = None
    cash: int = None
    point: int = None
    grade: str = None
    user_id: int = None


def create_lolketing_user_table(item: UserTable) -> LolketingUserTable:
    user = LolketingUserTable()
    user.cash = 0
    user.point = 0
    user.grade = "USER001"
    user.user_id = item.index

    return user


class IdParam(BaseModel):
    id: str = None


class UserIdParam(BaseModel):
    id: int = None


class CashChargingItem(BaseModel):
    id: str = None
    cash: int = None


class CouponUseItem(BaseModel):
    id: str = None
    couponId: int = None


class UpdateMyInfoItem(BaseModel):
    id: str = None
    nickname: str = None
    mobile: str = None
    address: str = None
