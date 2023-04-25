from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon

app = FastAPI()
# app.mount("/", StaticFiles(directory="public", html = True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test():
    return {"text":"page"}

@app.get("/test2")
def test2():
    pokemon = session.query(PokemonTable).filter().first()
    return pokemon