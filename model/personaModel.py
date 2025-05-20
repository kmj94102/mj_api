from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class Persona3ScheduleTable(Base):
    __tablename__ = 'persona3_schedule'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer)
    day = Column(Integer)
    dayOfWeek = Column(String(100))
    title = Column(String(100))
    contents = Column(Text)
    rank = Column(Integer)
    isComplete = Column(Boolean)
    communityIdx = Column(Integer, ForeignKey('persona3_community.idx'))

    community = relationship("Persona3CommunityTable", foreign_keys=[communityIdx])


class Persona3Schedule(BaseModel):
    month: int = None
    day: int = None
    dayOfWeek: str = None
    title: str = None
    contents: str = None
    rank: int = None
    isComplete: bool = None
    communityIdx: int = None

    def toTable(self) -> Persona3ScheduleTable:
        return Persona3ScheduleTable(
            month=self.month,
            day=self.day,
            dayOfWeek=self.dayOfWeek,
            title=self.title,
            contents=self.contents,
            rank=self.rank,
            monisCompleteth=self.isComplete,
            communityIdx=self.communityIdx,
        )


class Persona3CommunityTable(Base):
    __tablename__ = 'persona3_community'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    arcana = Column(String(45))
    name = Column(String(200))
    image = Column(Text)
    rank = Column(Integer)


class Persona3Community(BaseModel):
    arcana: str = None
    name: str = None
    image: str = None
    rank: int = None

    def toTable(self) -> Persona3CommunityTable:
        return Persona3CommunityTable(
            arcana=self.arcana,
            name=self.name,
            image=self.image,
            rank=self.rank,
        )


class ScheduleParam(BaseModel):
    skip: int = 0
    limit: int = 100


class ScheduleUpdateParam(BaseModel):
    idxList: list[int]


class CommunityUpdateParam(BaseModel):
    idx: int
    rank: int