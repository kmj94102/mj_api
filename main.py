from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased, load_only
from sqlalchemy.sql import exists
from sqlalchemy import update, delete

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table, \
    CharacteristicTable, Characteristic, create_characteristic_table, \
    UpdateIsCatch, Schedule, ScheduleItem, create_schedule, \
    Calendar, CalendarItem, create_calendar, \
    Plan, PlanItem, create_plan, PlanTasks, \
    Task, TaskItem, create_task, \
    Elsword, ElswordItem, create_elsword, \
    Quest, QuestItem, create_quest, QuestUpdateItem, \
    QuestProgress, QuestProgressItem, create_init_quest_progress
from pydantic import BaseSettings
from datetime import datetime, timedelta
from typing import List


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
# 달력 정보 추가
@app.post("/insert/calendar")
async def insert_calendar(item: CalendarItem):
    calendar_date = item.calendarDate.strftime("%Y-%m-%d")
    exists_query = session.query(Calendar).filter(
        Calendar.calendarDate == calendar_date,
        Calendar.dateInfo == item.dateInfo
    ).exists()

    if not session.query(exists_query).scalar():
        calendar = create_calendar(item)
        session.add(calendar)
        session.commit()
        return f"{item.dateInfo} 추가 완료"
    else:
        return f"{item.dateInfo}는 이미 추가된 정보입니다."


# 달력 정보 조회 (월 정보)
@app.get("/select/calendar/month")
async def read_calendar_month(year: int, month: int):
    session.commit()
    start_date = datetime(year, month, 1)
    end_date = get_last_day_time(year, month)
    current_date = start_date

    result = []

    while current_date < end_date:
        format_date = current_date.strftime("%Y-%m-%d")
        calendar_info = await read_calendar_date(format_date)
        schedule_info = await read_schedule(current_date)
        plan_info = await read_plans_tasks(format_date)

        if calendar_info or schedule_info:
            day_data = {
                "date": format_date,
                "calendarInfo": [
                    {
                        "calendarDate": calendar.calendarDate,
                        "info": calendar.dateInfo,
                        "isHoliday": calendar.isHoliday,
                        "isSpecialDay": calendar.isSpecialDay
                    }
                    for calendar in calendar_info
                ],
                "scheduleInfo": [
                    {
                        "startTime": schedule.startTime,
                        "endTime": schedule.endTime,
                        "recurrenceType": schedule.recurrenceType,
                        "recurrenceEndDate": schedule.recurrenceEndDate,
                        "scheduleContent": schedule.scheduleContent,
                        "scheduleTitle": schedule.scheduleTitle,
                        "recurrenceId": schedule.recurrenceId
                    }
                    for schedule in schedule_info
                ],
                "planInfo": plan_info
            }
            result.append(day_data)
        current_date += timedelta(days=1)

    return result


# 달력 정보 조회 (일 정보)
@app.get("/select/calendar/date")
async def read_calendar_date(date: str) -> List[Calendar]:
    return session.query(Calendar).filter(Calendar.calendarDate == date).all()


# 신규 일정 등록
@app.post("/insert/schedule")
async def insert_schedule(item: ScheduleItem):
    schedule = create_schedule(item)
    if schedule.recurrenceType != "none" and schedule.recurrenceEndDate is None:
        raise HTTPException(status_code=400, detail="반복 종료 일 정보가 누락되었습니다.")
    result = await insert_schedule_item(schedule)

    if item.recurrenceType == "yearly":
        await yearly_schedule(item, result)
    elif item.recurrenceType == "monthly":
        await monthly_schedule(item, result)
    elif item.recurrenceType == "weekly":
        await weekly_schedule(item, result)
    elif item.recurrenceType == "daily":
        await daily_schedule(item, result)

    return "등록 완료"


async def insert_schedule_item(schedule: Schedule) -> int:
    session.add(schedule)
    session.flush()
    session.commit()
    session.refresh(schedule)

    return schedule.id


async def yearly_schedule(item: ScheduleItem, id: int):
    current = item.startTime.replace(year=item.startTime.year + 1)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime.replace(year=item.endTime.year + 1)
        await insert_schedule_item(create_schedule(item, id))
        current = current.replace(year=current.year + 1)


async def monthly_schedule(item: ScheduleItem, id: int):
    current = next_year_month(item.startTime)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime.replace(year=current.year, month=current.month)
        await insert_schedule_item(create_schedule(item, id))
        current = next_year_month(current_date=current)


def next_year_month(current_date: datetime):
    nextMonth = current_date.month + 1
    nextYear = current_date.year
    if nextMonth > 12:
        nextMonth = 1
        nextYear += 1

    return current_date.replace(year=nextYear, month=nextMonth)


async def weekly_schedule(item: ScheduleItem, id: int):
    current = item.startTime + timedelta(days=7)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + timedelta(days=7)
        await insert_schedule_item(create_schedule(item, id))
        current = current + timedelta(days=7)


async def daily_schedule(item: ScheduleItem, id: int):
    current = item.startTime + timedelta(days=1)
    while current <= item.recurrenceEndDate:
        item.startTime = current
        item.endTime = item.endTime + timedelta(days=1)
        await insert_schedule_item(create_schedule(item, id))
        current = current + timedelta(days=1)


# 일정 조회

@app.get("/schedule")
async def read_schedule(date: datetime):
    session.commit()

    return session.query(Schedule).filter(
        Schedule.startTime >= date,
        Schedule.endTime <= date + timedelta(days=1)
    ).all()


@app.post("/insert/plan")
async def insert_plan(title, date):
    plan = Plan()
    plan.title = title
    plan.planDate = date

    session.add(plan)
    session.flush()
    session.commit()
    session.refresh(plan)

    return plan.id


@app.post("/insert/task")
async def insert_task(item: TaskItem):
    task = create_task(item)
    session.add(task)
    session.commit()

    return f"{item.contents} 추가 완료"


@app.post("/insert/plan-tasks")
async def insert_plan_tasks(item: PlanTasks):
    planId = await insert_plan(item.title, item.planDate)

    print(f"\n\n\n{planId}\n\n\n")

    for taskItem in item.taskList :
        taskItem.planId = planId
        await insert_task(taskItem)

    return f"{item.title} 등록 완료"

@app.get("/select/plans-tasks")
async def read_plans_tasks(date: str):
    plan_list = session.query(Plan).filter(Plan.planDate == date).all()
    return [
        {
            "id": plan.id,
            "planDate": plan.planDate,
            "title": plan.title,
            "taskList": [
                {
                    "id": task.id,
                    "contents": task.contents,
                    "isCompleted": task.isCompleted
                }
                for task in session.query(Task).filter(Task.planId == plan.id).all()
            ]
        }
        for plan in plan_list
    ]


def get_last_day_time(year: int, month: int) -> datetime:
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    last_day = datetime(year=next_year, month=next_month, day=1, hour=23, minute=59, second=59) - timedelta(days=1)
    return last_day


def get_start_date_time(year: int, month: int) -> datetime:
    return datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)


@app.post("/insert/elsword")
async def insert_elsword(item: ElswordItem):
    elsword = create_elsword(item)

    session.add(elsword)
    session.commit()
    return f"{item.name} 추가 완료"


@app.post("/insert/elsword/quest")
async def insert_elsword_quest(item: QuestItem):
    quest = create_quest(item)
    result = ""

    history = session.query(Quest).filter(Quest.name == item.name).first()
    if history is None:
        session.add(quest)
        session.commit()
        result = f"{item.name}를 등록하였습니다."
    else:
        result = f"{item.name}은 이미 등록된 퀘스트입니다."
    return result


@app.get("/select/elsword/quest")
async def read_elsword_quest():
    session.commit()
    quest = session.query(Quest).all()

    return [
        {
            "progress": calculate_progress(item.complete),
            "id": item.id,
            "name": item.name
        }
        for item in quest
    ]


def calculate_progress(complete: str):
    list = complete.split(",")
    length = len(list) if list[0] != "" or list[-1] != "" else 0
    print(length)
    return (length / 56) * 100


@app.delete("/delete/elsword/quest")
async def delete_elsword_quest(id: int):
    session.execute(delete(Quest).where(Quest.id == id))
    session.commit()

    return "삭제 완료"


@app.get("/select/elsword/quest/detail")
async def read_elsword_quest_detail():
    session.commit()
    quest = session.query(Quest).all()
    allowed_fields = ["characterGroup", "name", "questImage"]
    elsword = session.query(Elsword).filter(Elsword.classType == "master").options(load_only(*allowed_fields)).all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "progress": calculate_progress(item.complete),
            "character": [
                {
                    "name": char.name,
                    "image": char.questImage,
                    "group": char.characterGroup,
                    "isComplete": char.name in item.complete,
                    "isOngoing": char.name in item.ongoing
                }
                for char in elsword
            ]
        }
        for item in quest
    ]


@app.post("/update/elsword/quest")
async def update_elsword_quest(item: QuestUpdateItem):
    quest = session.query(Quest).filter(Quest.id == item.id).first()
    if item.type == "complete":
        quest.complete = add_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)
    elif item.type == "ongoing":
        quest.ongoing = add_name_to_text(quest.ongoing, item.name)
        quest.complete = remove_name_to_text(quest.complete, item.name)
    elif item.type == "remove":
        quest.complete = remove_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)

    session.commit()
    return "업데이트 완료"


def add_name_to_text(text, name):
    if text:
        result = f"{text},{name}"
    else:
        result = name
    return result


def remove_name_to_text(text, name):
    result = text.replace(f"{name},", "").replace(f",{name}", "").replace(name, "")
    if result.endswith(","):
        result = result[:-1]
    return result


async def create_quest_progress(id, name):
    progress = create_init_quest_progress(id, name)
    session.add(progress)

    return f"{name} 추가 완료"
