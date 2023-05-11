from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table, \
    CharacteristicTable, Characteristic, create_characteristic_table
from pydantic import BaseSettings


class Settings(BaseSettings):
    pwd: str


app = FastAPI()
# app.mount("/", StaticFiles(directory="public", html = True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()


@app.get("/")
async def root():
    return {"message": settings.pwd}


######### 포켓몬 ###########
# 포켓몬 등록
@app.post("/insert/pokemon")
async def insert_pokemon(item: Pokemon):
    data = session.query(PokemonTable).filter(PokemonTable.name == item.name).first()
    if data is None:
        pokemon = create_pokemon_table(item)
        session.add(pokemon)
        session.commit()

    return f"{item.name} 추가 완료"


# 포켓몬 리스트 조회
@app.get("/pokemonList")
async def read_pokemon_list(name: str = "", skip: int = 0, limit: int = 100):
    session.commit()

    list = session.query(PokemonTable.index, PokemonTable.number, PokemonTable.name, PokemonTable.spotlight,
                         PokemonTable.shinySpotlight, PokemonTable.isCatch) \
        .filter(PokemonTable.name.like(f"%{name}%")).offset(skip).limit(limit).all()
    total_size = session.query(PokemonTable).filter(PokemonTable.name.like(f"%{name}%")).count()
    return {
        "list": list,
        "totalSize": total_size
    }


# 포켓몬 상세 조회
@app.get("/pokemon/detail/{number}")
async def read_pokemon_detail(number: str):
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == number).first()
    beforeInfo = await read_pokemon_image(pokemon.index - 1)
    nextInfo = await read_pokemon_image(pokemon.index + 1)

    return {
        "pokemonInfo": pokemon,
        "beforeInfo": beforeInfo,
        "nextInfo": nextInfo
    }


# 포켓몬 이미지 조회
@app.get("/pokemon/image/{index}")
async def read_pokemon_image(index: int):
    return session.query(PokemonTable.number, PokemonTable.image, PokemonTable.shinyImage).filter(
        PokemonTable.index == index).first()


# 특성 등록
@app.post("/insert/char")
async def create_characteristic(item: Characteristic):
    result = item.name
    char = session.query(CharacteristicTable).filter(CharacteristicTable.name == item.name).first()
    if char is None:
        charTable = create_characteristic_table(item)

        session.add(charTable)
        session.commit()
        result = f"{item.name} 추가완료"
    else:
        result = f"{item.name} 이미 추가된 특성입니다."
    return result
