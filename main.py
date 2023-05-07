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
    pokemon = create_pokemon_table(item)
    session.add(pokemon)
    session.commit()

    return f"{item.name} 추가 완료"

# 포켓몬 리스트 조회
@app.get("/pokemonList")
async def read_pokemon_list(skip: int = 0, limit: int = 100):
    list = session.query(PokemonTable.index, PokemonTable.number, PokemonTable.name, PokemonTable.spotlight, PokemonTable.shinySpotlight)\
        .offset(skip).limit(limit).all()
    total_size = session.query(PokemonTable).count()
    return {
        "list": list,
        "totalSize": total_size
    }

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