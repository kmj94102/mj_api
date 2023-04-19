from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from db import Base
from db import ENGINE
from typing import List

class PokemonTable(Base):
    __tablename__ = 'pokemon'
    index = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(45))
    name = Column(String(45))
    status = Column(String(45))
    classification = Column(String(45))
    characteristic = Column(String(45))
    attribute = Column(String(45))
    dotImage = Column(String(500))
    dotShinyImage = Column(String(500))
    image = Column(String(500))
    shinyImage = Column(String(500))
    spotlight = Column(String(500))
    description = Column(String(500))
    generation = Column(Integer)

class Pokemon(BaseModel):
    index : int = None
    number: str = None
    name : str = None
    status : str = None
    classification : str = None
    characteristic : str = None
    attribute : str = None
    dotImage : str = None
    dotShinyImage : str = None
    image : str = None
    shinyImage : str = None
    spotlight: str = None
    description : str = None
    generation : int = None

def main():
    # Table 없으면 생성
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    main()