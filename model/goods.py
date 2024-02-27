from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List
from model.userModel import UserTable

Base = declarative_base()


class GoodsTable(Base):
    __tablename__ = 'goods'
    goodsId = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String)
    name = Column(String)
    price = Column(Integer)


class GoodsImageTable(Base):
    __tablename__ = 'goods_image'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String)
    goodsId = Column(Integer)


class Goods(BaseModel):
    goodsId: int
    category: str
    name: str
    price: int


class GoodsImage(BaseModel):
    id: int
    url: str
    goodsId: int


class GoodsInsertParam(BaseModel):
    category: str
    name: str
    price: int
    urlList: List[str]


def create_goods_table(item: GoodsInsertParam) -> GoodsTable:
    goods = GoodsTable()
    goods.category = item.category
    goods.name = item.name
    goods.price = item.price

    return goods


def create_goods_image_table(url: str, goodsId: int) -> GoodsImageTable:
    goodsImage = GoodsImageTable()
    goodsImage.url = url
    goodsImage.goodsId = goodsId

    return goodsImage
