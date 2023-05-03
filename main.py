from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table
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

@app.post("/insert/pokemon")
async def insert_pokemon(item: Pokemon):
    pokemon = create_pokemon_table(item)
    session.add(pokemon)
    session.commit()

    return f"{item.name} 추가 완료"

@app.get("/test2")
def test2():
    pokemon = session.query(PokemonTable).filter().first()
    return pokemon