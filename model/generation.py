from sqlalchemy import Column, String, Integer, Boolean
from pydantic import BaseModel
from db import Base


class GenerationTable(Base):
    __tablename__ = 'generation'
    idx = Column(Integer, primary_key=True)
    code = Column(Integer)
    name = Column(String(100))


class Generation(BaseModel):
    code: int = None
    name: str = None


class GenerationDexTable(Base):
    __tablename__ = 'generation_dex'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    pokemonIdx = Column(Integer)
    generationIdx = Column(Integer)
    isCatch = Column(Boolean)


class GenerationDex(BaseModel):
    pokemonIdx: int = None
    generationIdx: int = None
    isCatch: bool = False


def createDexTable(item: GenerationDex) -> GenerationDexTable:
    dex = GenerationDexTable()
    dex.pokemonIdx = item.pokemonIdx
    dex.generationIdx = item.generationIdx
    dex.isCatch = item.isCatch

    return dex
