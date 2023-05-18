from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased
from sqlalchemy import update

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table, \
    CharacteristicTable, Characteristic, create_characteristic_table, \
    UpdateIsCatch, Schedule, ScheduleItem, create_schedule
from pydantic import BaseSettings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

# 포켓몬 잡은 상태 업데이트
@app.post("/update/pokemon/catch")
async def update_pokemon_is_catch(item: UpdateIsCatch):
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == item.number).first()
    pokemon.isCatch = item.isCatch
    session.commit()
    return f"{item.number} 업데이트 완료"

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




######### 달력 ###########
# 신규 일정 등록
@app.post("/insert/schedule")
async def insert_schedule(item: ScheduleItem):
    schedule = create_schedule(item)
    result = await insert_schedule_item(schedule)

    if item.recurrenceType == "yearly":
        await yearly_schedule(item, result)
    elif item.recurrenceType == "monthly":
        await monthly_schedule(item, result)
    elif item.recurrenceType == "weekly":
        await weekly_schedule(item, result)
    elif item.recurrenceType == "daily":
        await daily_schedule(item, result)

    return f"{result} / {result == 5}"

async def insert_schedule_item(schedule: Schedule) -> int:
    session.add(schedule)
    session.flush()
    session.commit()
    session.refresh(schedule)

    return schedule.id

async def yearly_schedule(item: ScheduleItem, id: int):
    current = item.startTime + relativedelta(years=1)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + relativedelta(years=1)
        await insert_schedule_item(create_schedule(item, id))
        current = current  + relativedelta(years=1)

async def monthly_schedule(item: ScheduleItem, id: int):
    current = item.startTime + relativedelta(months=1)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + relativedelta(months=1)
        await insert_schedule_item(create_schedule(item, id))
        current = current  + relativedelta(months=1)

async def weekly_schedule(item: ScheduleItem, id: int):
    current = item.startTime + timedelta(days = 7)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + timedelta(days = 7)
        await insert_schedule_item(create_schedule(item, id))
        current = current + timedelta(days = 7)

async def daily_schedule(item: ScheduleItem, id: int):
    current = item.startTime + timedelta(days = 1)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + timedelta(days = 1)
        await insert_schedule_item(create_schedule(item, id))
        current = current + timedelta(days = 1)
