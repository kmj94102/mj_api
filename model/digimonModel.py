from typing import List

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from db import Base


class DigimonTable(Base):
    __tablename__ = 'digimon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    type = Column(String(100))
    property = Column(String(100))
    field = Column(String(100))
    lethalMove = Column(Text)
    description = Column(Text)
    image = Column(Text)
    sprites = Column(Text)
    levelId = Column(Integer, ForeignKey('digimon_level.id'))

    user = relationship("DigimonLevelTable", foreign_keys=[levelId])


class Digimon(BaseModel):
    name: str = None
    type: str = None
    property: str = None
    field: str = None
    lethalMove: str = None
    description: str = None
    image: str = None
    sprites: str = None
    levelId: int = None


def create_digimon(item: Digimon) -> DigimonTable:
    digimon = DigimonTable()
    digimon.name = item.name
    digimon.levelId = item.levelId
    digimon.type = item.type
    digimon.property = item.property
    digimon.field = item.field
    digimon.lethalMove = item.lethalMove
    digimon.description = item.description
    digimon.image = item.image
    digimon.sprites = item.sprites

    return digimon


class DigimonLevelTable(Base):
    __tablename__ = 'digimon_level'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(100))


class DigimonLevel(BaseModel):
    level: str = None


class DmoDigimonGroupTable(Base):
    __tablename__ = "dmo_digimon_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    digimons = relationship("DmoDigimonTable", back_populates="group")


class DmoDigimonTable(Base):
    __tablename__ = "dmo_digimon"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    isOpen = Column(Boolean, default=False)
    isTranscend = Column(Boolean, default=False)
    level = Column(Integer)
    image = Column(String(255))
    groupId = Column(Integer, ForeignKey("dmo_digimon_group.id"))

    group = relationship("DmoDigimonGroupTable", back_populates="digimons")
    unions = relationship("DmoUnionTable", back_populates="digimon")


class DmoUnionGroupTable(Base):
    __tablename__ = "dmo_union_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    unions = relationship("DmoUnionTable", back_populates="union_group")
    conditions = relationship("DmoUnionConditionsTable", back_populates="union_group")


class DmoUnionTable(Base):
    __tablename__ = "dmo_union"

    digimonId = Column(Integer, ForeignKey("dmo_digimon.id"), primary_key=True)
    unionId = Column(Integer, ForeignKey("dmo_union_group.id"), primary_key=True)

    digimon = relationship("DmoDigimonTable", back_populates="unions")
    union_group = relationship("DmoUnionGroupTable", back_populates="unions")


class DmoConditionTypeTable(Base):
    __tablename__ = "dmo_condition_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)

    conditions = relationship("DmoUnionConditionsTable", back_populates="condition_type")


class DmoRewardTypeTable(Base):
    __tablename__ = "dmo_reward_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)

    rewards = relationship("DmoUnionConditionsTable", back_populates="reward_type")


class DmoUnionConditionsTable(Base):
    __tablename__ = "dmo_union_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conditionId = Column(Integer, ForeignKey("dmo_condition_type.id"))
    conditionValue = Column(Integer)
    rewardId = Column(Integer, ForeignKey("dmo_reward_type.id"))
    rewardValue = Column(Integer)
    unionId = Column(Integer, ForeignKey("dmo_union_group.id"))

    union_group = relationship("DmoUnionGroupTable", back_populates="conditions")
    condition_type = relationship("DmoConditionTypeTable", back_populates="conditions")
    reward_type = relationship("DmoRewardTypeTable", back_populates="rewards")
    progresses = relationship("DmoUnionProgressTable", back_populates="condition")


class DmoUnionProgressTable(Base):
    __tablename__ = "dmo_union_progress"

    userId = Column(Integer, primary_key=True, autoincrement=True)
    unionConditionId = Column(Integer, ForeignKey("dmo_union_conditions.id"), primary_key=True)
    isComplete = Column(Boolean, default=False)

    condition = relationship("DmoUnionConditionsTable", back_populates="progresses")


class DmoDigimonGroup(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class DmoDigimon(BaseModel):
    id: int
    name: str
    isOpen: bool
    isTranscend: bool
    level: int
    image: str = None
    groupId: int = None


class DmoUnionGroup(BaseModel):
    id: int
    name: str


class DmoUnion(BaseModel):
    digimonId: int
    unionId: int


class DmoConditionType(BaseModel):
    id: int
    type: str


class DmoRewardType(BaseModel):
    id: int
    type: str


class DmoUnionConditions(BaseModel):
    id: int
    conditionId: int
    conditionValue: int
    rewardId: int
    rewardValue: int
    unionId: int


class DmoUnionProgress(BaseModel):
    userId: int
    unionConditionId: int
    isComplete: bool


class DmoDigimonCreate(BaseModel):
    name: str
    isOpen: bool
    isTranscend: bool
    level: int


class DmoDigimonGroupCreate(BaseModel):
    groupName: str
    list: List[DmoDigimonCreate]


class DmoSearch(BaseModel):
    name: str


class UnionRewardNConditions(BaseModel):
    rewardType: int
    rewardValue: int
    conditionType: int
    conditionValue: int


class UnionDigimon(BaseModel):
    digimonId: int


class DigimonUnionInsertParam(BaseModel):
    unionName: str
    rewardNConditions: list[UnionRewardNConditions]
    digimonList: list[UnionDigimon]
