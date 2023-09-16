from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from model import HomeParam

from pydantic import BaseSettings
from api import pokemon, calendar, elsword, accountBook
from api.calendar import read_calendar_week
from api.elsword import read_elsword_quest_progress


class Settings(BaseSettings):
    pwd: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()

app.include_router(pokemon.router, prefix="/pokemon", tags=["pokemon"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(elsword.router, prefix="/elsword", tags=["elsword"])
app.include_router(accountBook.router, prefix="/accountBook", tags=["accountBook"])


@app.get("/")
async def root():
    return {"message": settings.pwd}


@app.post("/homeInfo/select")
async def select_home_info(param: HomeParam):
    calendar_item = await read_calendar_week(param.startDate, param.endDate)
    quest = await read_elsword_quest_progress()

    return {
        "calendarInfo": calendar_item,
        "questInfo": quest
    }
