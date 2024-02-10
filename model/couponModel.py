from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from db import Base
from datetime import datetime
import random

from model.userModel import UserTable


class CouponTable(Base):
    __tablename__ = 'coupon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    rp = Column(Integer)
    number = Column(String(100))
    isUsed = Column(Boolean)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.index'))

    user = relationship("UserTable", foreign_keys=[user_id])


class Coupon(BaseModel):
    id: int = None
    name: str = None
    rp: int = None
    number: str = None
    isUsed: bool = None
    timestamp: datetime = None
    user_id: int = None


class RouletteCountUpdateItem(BaseModel):
    id: int = None
    count: int = None


class RouletteCoupon(BaseModel):
    id: int = None
    rp: int = None


def create_new_user_coupon(userId) -> CouponTable:
    coupon = CouponTable()
    coupon.name = "COUPON001"
    coupon.rp = 500
    coupon.number = create_coupon_number()
    coupon.isUsed = False
    coupon.timestamp = datetime.now()
    coupon.user_id = userId

    return coupon


def create_roulette_coupon(item: RouletteCoupon) -> CouponTable:
    coupon = CouponTable()
    coupon.name = "COUPON002"
    coupon.rp = item.rp
    coupon.number = create_coupon_number()
    coupon.isUsed = False
    coupon.timestamp = datetime.now()
    coupon.user_id = item.id

    return coupon


def create_coupon_number() -> str:
    coupon_number = ""
    choose_num = [
        "A", "B", "C", "D", "E", "F",
        "G", "H", "I", "J", "K", "L",
        "M", "N", "O", "P", "Q", "R",
        "S", "T", "U", "V", "W", "X",
        "Y", "Z", "0", "1", "2", "3",
        "4", "5", "6", "7", "8", "9"
    ]
    random.seed()
    for i in range(16):
        coupon_number += choose_num[random.randint(0, 35)]
        if i % 4 == 3 and i != 15:
            coupon_number += "-"
    return coupon_number
