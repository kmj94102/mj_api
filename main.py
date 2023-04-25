from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon
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

@app.get("/test")
def test():
    return {"text":"page"}

@app.get("/test2")
def test2():
    pokemon = session.query(PokemonTable).filter().first()
    return pokemon