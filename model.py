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
    image : str = None
    shinyImage : str = None
    spotlight: str = None
    description : str = None
    generation : int = None

def create_pokemon_table(item: Pokemon) -> PokemonTable:
    pokemon = PokemonTable()
    pokemon.number = item.number
    pokemon.name = item.name
    pokemon.status = item.status
    pokemon.classification = item.classification
    pokemon.characteristic = item.characteristic
    pokemon.attribute = item.attribute
    pokemon.image = item.image
    pokemon.spotlight = item.spotlight
    pokemon.shinyImage = item.shinyImage
    pokemon.description = item.description
    pokemon.generation = item.generation

    return pokemon

def main():
    # Table 없으면 생성
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    main()