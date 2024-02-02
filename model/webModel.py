from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel
from db import Base


class WebTable(Base):
    __tablename__ = 'web'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45))
    address = Column(Text)


class Web(BaseModel):
    id: int = None
    name: str = None
    address: str = None


def create_web_table(item: Web) -> WebTable:
    web = WebTable()
    web.name = item.name
    web.address = item.address

    return web