from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import aliased, load_only, joinedload
from sqlalchemy.sql import exists
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, delete, text

from starlette.middleware.cors import CORSMiddleware
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table, \
    CharacteristicTable, Characteristic, create_characteristic_table, \
    UpdateIsCatch, UpdatePokemonImage, \
    Schedule, ScheduleItem, create_schedule, \
    EvolutionTable, Evolution, create_evolution_table, \
    EvolutionTypeTable, EvolutionType, create_evolution_type_table, \
    Calendar, CalendarItem, create_calendar, \
    Plan, PlanItem, create_plan, PlanTasks, \
    Task, TaskItem, create_task, \
    Elsword, ElswordItem, create_elsword, \
    Quest, QuestItem, create_quest, QuestUpdateItem, \
    QuestProgress, QuestProgressItem, create_init_quest_progress, QuestProgressUpdateItem, \
    AccountBook, AccountBookItem, create_account_book, DateConfiguration

from pydantic import BaseSettings
from datetime import datetime, timedelta
from typing import List
from datetime import datetime


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
@app.post("/insert/pokemon")
async def insert_pokemon(item: Pokemon):
    """
    포켓몬 등록
    - **index**: 인덱스
    - **number**: 포켓몬 번호
    - **name**: 이름
    - **status**: 스테이터스
    - **classification**: 분류
    - **characteristic**: 특성
    - **attribute**: 속성
    - **image**: 이미지
    - **shinyImage**: 이로치 이미지
    - **spotlight**: 스포트라이트
    - **shinySpotlight**: 이로치 스포트라이트
    - **description**: 설명
    - **generation**: 세대
    - **isCatch**: 잡은 여부
    """
    data = session.query(PokemonTable).filter(PokemonTable.name == item.name).first()
    if data is None:
        pokemon = create_pokemon_table(item)
        session.add(pokemon)
        session.commit()

    return f"{item.name} 추가 완료"


@app.get("/pokemonList")
async def read_pokemon_list(name: str = "", skip: int = 0, limit: int = 100):
    """
    포켓몬 리스트 조회
    - **name**: 포켓몬 이름
    - **skip**: 시작 인덱스 번호
    - **limit**: 한번 호출 시 불러올 개수
    """
    session.commit()

    list = session.query(PokemonTable.index, PokemonTable.number, PokemonTable.name, PokemonTable.spotlight,
                         PokemonTable.shinySpotlight, PokemonTable.isCatch) \
        .filter(PokemonTable.name.like(f"%{name}%")).offset(skip).limit(limit).all()
    total_size = session.query(PokemonTable).filter(PokemonTable.name.like(f"%{name}%")).count()
    return {
        "list": list,
        "totalSize": total_size
    }


@app.get("/pokemon/detail/{number}")
async def read_pokemon_detail(number: str):
    """
    포켓몬 상세 조회
    - **number**: 포켓몬 번호
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == number).first()
    beforeInfo = await read_pokemon_image(pokemon.index - 1)
    nextInfo = await read_pokemon_image(pokemon.index + 1)
    evolutionInfo = await read_pokemon_evolution(number)

    return {
        "pokemonInfo": pokemon,
        "beforeInfo": beforeInfo,
        "nextInfo": nextInfo,
        "evolutionInfo": evolutionInfo
    }


@app.get("/pokemon/image/{index}")
async def read_pokemon_image(index: int):
    """
    포켓몬 이미지 조회
    - **index**: 포켓몬 인덱스
    """
    return session.query(PokemonTable.number, PokemonTable.image, PokemonTable.shinyImage).filter(
        PokemonTable.index == index).first()


@app.get("/pokemon/select/evolution")
async def read_pokemon_evolution(number: str):
    """
    포켓몬 진화 조회
    - **number**: 포켓몬 번호
    """
    pokemon1 = aliased(PokemonTable)
    pokemon2 = aliased(PokemonTable)
    evolution = session.query(pokemon1.spotlight.label('beforeDot'), pokemon1.shinySpotlight.label('beforeShinyDot'),
                              pokemon2.spotlight.label('afterDot'), pokemon2.shinySpotlight.label('afterShinyDot'),
                              EvolutionTypeTable.image.label('evolutionImage'), EvolutionTable.evolutionCondition) \
        .filter(EvolutionTable.numbers.like(f"%{number}%"), EvolutionTable.beforeNum == pokemon1.number,
                EvolutionTable.afterNum == pokemon2.number,
                EvolutionTypeTable.name == EvolutionTable.evolutionType).all()

    return evolution


@app.post("/update/pokemon/catch")
async def update_pokemon_is_catch(item: UpdateIsCatch):
    """
    포켓몬 잡은 상태 업데이트
    - **number**: 포켓몬 번호
    - **isCatch**: 잡은 상태
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == item.number).first()
    pokemon.isCatch = item.isCatch
    session.commit()
    return f"{item.number} 업데이트 완료"


@app.post("/insert/char")
async def create_characteristic(item: Characteristic):
    """
    특성 등록
    - **index**: 인덱스
    - **name**: 이름
    - **description**: 설명
    """
    char = session.query(CharacteristicTable).filter(CharacteristicTable.name == item.name).first()
    if char is None:
        charTable = create_characteristic_table(item)

        session.add(charTable)
        session.commit()
        result = f"{item.name} 추가완료"
    else:
        result = f"{item.name} 이미 추가된 특성입니다."
    return result


@app.get("/select/pokemon/brief-list/{search}")
async def read_brief_pokemon_list(search: str):
    """
    포켓몬 간략한 정보 리스트 조회 (진화 추가 용도)
    - **search**: 검색어, 숫자 형태일 경우 해당 번호의 정보 조회, 문자형일 경우 검색어에 해당하는 포켓몬 조회
    """
    if search.isdigit():
        sql = f"""
            SELECT *
            FROM pokemon
            WHERE pokemon.index >= (
                SELECT pokemon.index
                FROM pokemon
                WHERE pokemon.number = {search}
                LIMIT 1
            )
            LIMIT 10;
        """
        result = session.execute(text(sql)).fetchall()
    else:
        result = session.query(PokemonTable.spotlight, PokemonTable.number).filter(
            PokemonTable.name.like(f"%{search}%")).all()

    return result


@app.post("/insert/pokemon/evolution")
async def insert_pokemon_evolutions(list: List[Evolution]):
    """
    포켓몬 진화 추가
    - **numbers**: 진화에 포함된 번호들
    - **beforeNum**: 진화 전 번호
    - **afterNum**: 진화 후 번호
    - **evolutionType**: 진화 타입
    - **evolutionCondition**: 진화 조건
    """
    try:
        session.rollback()
        session.begin()
        for item in list:
            history = session.query(EvolutionTable).filter(EvolutionTable.beforeNum == item.beforeNum,
                                                           EvolutionTable.afterNum == item.afterNum).first()

            if history is None:
                evolution = create_evolution_table(item)

                session.add(evolution)
                session.commit()
            else:
                raise ValueError(f"중복 데이터 {item.beforeNum}-{item.afterNum}")
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()
    return "데이터 추가를 완료하였습니다."


@app.post("/insert/pokemon/evolution-type")
async def insert_pokemon_evolution_types(list: List[EvolutionType]):
    """
    포켓몬 진화 타입 추가
    - **name**: 타입 이름
    - **image**: 타입 이미지
    """
    try:
        session.rollback()
        session.begin()
        for item in list:
            evolution_type = create_evolution_type_table(item)

            session.add(evolution_type)
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()
    return "데이터 추가를 완료하였습니다."


@app.post("/select/pokemon/before-image-info")
async def read_pokemon_before_imgae_info():
    session.commit()
    return session.query(PokemonTable.number, PokemonTable.spotlight).all()


@app.post("/update/pokemon/image")
async def update_pokemon_image(item: UpdatePokemonImage):
    """
    포켓몬 이미지 업데이트
    - **number**: 포켓몬 번호
    - **image**: 이미지
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == item.number).first()
    pokemon.spotlight = item.spotlight
    session.commit()
    return f"{item.number} 업데이트 완료"


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
        day_data = await read_calendar(current_date)
        if day_data:
            result.append(day_data)
        current_date += timedelta(days=1)

    return result


@app.get("/select/calendar/week")
async def read_calendar_week(start: str, end: str):
    date_format = "%Y.%m.%d"
    start_date = datetime.strptime(start, date_format)
    end_date = datetime.strptime(end, date_format)

    current_date = start_date

    result = []

    while current_date < end_date:
        day_data = await read_calendar(current_date)
        if day_data:
            result.append(day_data)
        current_date += timedelta(days=1)

    return result


# 달력 정보 조회 (일 정보)
@app.get("/select/calendar/date")
async def read_calendar_date(year: int, month: int, date: int):
    return await read_calendar(datetime(year, month, date))


async def read_calendar(current_date: datetime):
    format_date = current_date.strftime("%Y-%m-%d")
    calendar_info = await read_calendar_info(format_date)
    schedule_info = await read_schedule(current_date)
    plan_info = await read_plans_tasks(format_date)

    if calendar_info or schedule_info or plan_info:
        return {
            "date": format_date,
            "calendarInfoList": [
                {
                    "id": calendar.id,
                    "calendarDate": calendar.calendarDate,
                    "info": calendar.dateInfo,
                    "isHoliday": calendar.isHoliday,
                    "isSpecialDay": calendar.isSpecialDay
                }
                for calendar in calendar_info
            ],
            "scheduleInfoList": [
                {
                    "id": schedule.id,
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
            "planInfoList": plan_info
        }


# 달력 날짜 정보 조회
async def read_calendar_info(date: str) -> List[Calendar]:
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


@app.delete("/delete/schedule")
async def delete_schedule(id: int):
    schedule = session.query(Schedule).filter(Schedule.id == id).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(Schedule).filter(Schedule.recurrenceId == id).delete(synchronize_session=False)

    session.delete(schedule)
    session.commit()

    return "일정을 삭제하였습니다."


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

    for taskItem in item.taskList:
        taskItem.planId = planId
        await insert_task(taskItem)

    return f"{item.title} 등록 완료"


@app.delete("/delete/plan-tasks")
async def delete_plan_tasks(id: int):
    plan = session.query(Plan).filter(Plan.id == id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(Task).filter(Task.planId == id).delete(synchronize_session=False)

    session.delete(plan)
    session.commit()

    return "계획 삭제 완료"


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
    """
    엘소드 캐릭터 정보 등록
    - **characterGroup**: 케릭터 그룹 ex) 엘소드
    - **line**: 전직 라인 ex) 1
    - **classType**: 전직 등급, [first, second, third, master] 중 택 1
    - **name**: 전직 이름
    - **engName: 전직 영어 이름
    - **attackType**: 공격 타입, [magic, physics] 중 택 1
    - **story**: 전직 스토리
    - **bigImage**: 전체 이미지
    - **questImage**: 퀘스트 이미지 (선택)
    - **progressImage**: 퀘스트 진행 이미지 (선택)
    - **circleImage**: 원형 이미지
    """
    elsword = create_elsword(item)

    session.add(elsword)
    session.commit()
    return f"{item.name} 추가 완료"


@app.post("/insert/elsword/quest")
async def insert_elsword_quest(item: QuestItem):
    """
    엘소드 퀘스트 정보 등록
    - name: 퀘스트 이름
    - max: 퀘스트 개수
    - complete: 퀘스트를 완료한 캐릭터 이름들
    - ongoing: 퀘스트를 진행하고 있는 캐릭터 이름들
    """
    quest = create_quest(item)

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
    """
    엘소드 퀘스트 리스트 조회
    """
    session.commit()
    quest = session.query(Quest).all()

    return [
        {
            "progress": calculate_task_progress(item.complete),
            "id": item.id,
            "name": item.name
        }
        for item in quest
    ]


def calculate_task_progress(complete: str):
    list = complete.split(",")
    length = len(list) if list[0] != "" or list[-1] != "" else 0
    print(length)
    return (length / 56) * 100


@app.delete("/delete/elsword/quest")
async def delete_elsword_quest(id: int):
    """
    엘소드 퀘스트 삭제
    - **id**: 삭제하려고 하는 퀘스트 id
    """
    session.execute(delete(Quest).where(Quest.id == id))
    session.commit()

    return "삭제 완료"


@app.get("/select/elsword/quest/detail")
async def select_elsword_quest_detail():
    """
    엘소드 퀘스트 상세 정보 조회
    """
    session.commit()
    quest = session.query(Quest).all()
    allowed_fields = ["characterGroup", "name", "questImage"]
    elsword = session.query(Elsword).filter(Elsword.classType == "master").options(load_only(*allowed_fields)).all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "max": item.max,
            "character": [
                {
                    "name": char.name,
                    "image": char.questImage,
                    "group": char.characterGroup,
                    "isComplete": char.name in item.complete,
                    "isOngoing": char.name in item.ongoing,
                    "progress": get_character_progress(item.id, char.name) if char.name in item.ongoing else 0
                }
                for char in elsword
            ]
        }
        for item in quest
    ]


def get_character_progress(quest_id: int, name: str):
    try:
        result = session.query(QuestProgress).filter(QuestProgress.quest_id == quest_id,
                                                     QuestProgress.name == name).first().progress
    except:
        result = 0

    return result


@app.post("/update/elsword/quest")
async def update_elsword_quest(item: QuestUpdateItem):
    """
    퀘스트 상태 업데이트
    - id: 퀘스트 id
    - name: 캐릭터 이름
    - type: 변경할 퀘스트 상태 [complete, ongoing, remove] 중 택 1
    """
    quest = session.query(Quest).filter(Quest.id == item.id).first()
    if item.type == "complete":
        quest.complete = add_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)
        await delete_quest_progress(item.id, item.name)
    elif item.type == "ongoing":
        quest.ongoing = add_name_to_text(quest.ongoing, item.name)
        quest.complete = remove_name_to_text(quest.complete, item.name)
        await create_quest_progress(item.id, item.name, item.progress)
    elif item.type == "remove":
        quest.complete = remove_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)
        await delete_quest_progress(item.id, item.name)

    session.commit()
    return "업데이트 완료"


# 텍스트에 캐릭터 추가
def add_name_to_text(text, name):
    if text:
        result = f"{text},{name}"
    else:
        result = name
    return result


# 텍스트에 캐릭터 삭제
def remove_name_to_text(text, name):
    result = text.replace(f"{name},", "").replace(f",{name}", "").replace(name, "")
    if result.endswith(","):
        result = result[:-1]
    return result


# 퀘스트 진행 추가
async def create_quest_progress(id, name, progress_value):
    progress = create_init_quest_progress(id, name, progress_value)
    session.add(progress)

    return f"{name} 추가 완료"


# 퀘스트 진행 삭제
async def delete_quest_progress(id, name):
    session.query(QuestProgress).filter(QuestProgress.quest_id == id, QuestProgress.name == name).delete(
        synchronize_session=False)
    session.commit()

    return f"{name} 삭제 완료"


@app.get("/select/elsword/counter")
async def read_elsword_quest_progress():
    """
    퀘스트 진행 조회
    """
    session.commit()

    sql = """
        SELECT quest_progress.id, quest_progress.name, quest_progress.quest_id, quest_progress.progress, quest.max, elsword.progressImage, elsword.characterGroup 
        FROM quest, quest_progress, elsword 
        WHERE quest_progress.quest_id = quest.id AND elsword.name = quest_progress.name and elsword.classType = 'master'
    """

    result = session.execute(text(sql)).fetchall()

    formatted_result = [
        {
            "id": row[0],
            "name": row[1],
            "quest_id": row[2],
            "progress": row[3],
            "max": row[4],
            "image": row[5],
            "characterGroup": row[6],
        }
        for row in result
    ]

    return formatted_result


@app.post("/update/elsword/counter")
async def update_elsword_quest_progress(item: QuestProgressUpdateItem):
    """
    퀘스트 상태 업데이트
    - **id**: 퀘스트 진행 id
    - **max**: 퀘스트 개수
    """
    progressItem = session.query(QuestProgress).filter(QuestProgress.id == item.id).first()
    progressItem.progress += 1
    session.commit()

    if progressItem.progress >= item.max:
        await update_elsword_quest(QuestUpdateItem(id=progressItem.quest_id, name=progressItem.name, type="complete"))
        return 0

    return progressItem.progress


########## 가계부
@app.post("/insert/accountBook")
async def insert_account_book(item: AccountBookItem):
    """
    가계부 등록

    param
    - **date**: 사용일
    - **dateOfWeek**: 사용 요일
    - **amount**: 금액
    - **usageType**: 사용 타입
    - **whereToUse**: 사용 내용
    """
    data = session.query(AccountBook).filter(AccountBook.date == item.date, AccountBook.whereToUse == item.whereToUse,
                                             AccountBook.amount == item.amount).first()

    if data is None:
        account_book = create_account_book(item)
        session.add(account_book)
        session.commit()

    return f"{item.whereToUse} 등록 완료"


def calculate_start_date(date: datetime, base_date: int):
    current_month = date.month
    current_year = date.year
    current_day = date.day

    if current_day > base_date:
        start_date = datetime(current_year, current_month, base_date + 1)
    elif current_month > 1:
        start_date = datetime(current_year, current_month - 1, base_date + 1)
    else:
        start_date = datetime(current_year - 1, 12, base_date + 1)

    return start_date


def calculate_end_date(date: datetime, base_date: int):
    current_month = date.month
    current_year = date.year
    current_day = date.day

    if current_day <= base_date:
        end_date = datetime(current_year, current_month, base_date)
    elif current_month < 12:
        end_date = datetime(current_year, current_month + 1, base_date)
    else:
        end_date = datetime(current_year + 1, 1, base_date)

    return end_date


async def select_account_book_this_month(config: DateConfiguration):
    session.commit()

    date_format = "%Y.%m.%d"
    start_date = calculate_start_date(config.date, config.baseDate)
    end_date = calculate_end_date(config.date, config.baseDate)

    data = session.query(AccountBook).filter(AccountBook.date.between(start_date, end_date)).all()

    return {
        "startDate": start_date.strftime(date_format),
        "endDate": end_date.strftime(date_format),
        "list": data
    }


@app.post("/select/accountBook/summaryThisMonth")
async def select_account_summary_this_month(config: DateConfiguration):
    income = 0
    expenditure = 0

    month_info = await select_account_book_this_month(config)

    for item in month_info["list"]:
        if item.amount > 0:
            income += item.amount
        elif item.amount < 0:
            expenditure += item.amount

    return {
        "startDate": month_info["startDate"],
        "endDate": month_info["endDate"],
        "income": income,
        "expenditure": expenditure,
        "difference": expenditure + income
    }


@app.post("/select/accountBook/thisMonthDetail")
async def select_account_this_month_detail(config: DateConfiguration):
    income = 0
    expenditure = 0

    month_info = await select_account_book_this_month(config)

    for item in month_info["list"]:
        if item.amount > 0:
            income += item.amount
        elif item.amount < 0:
            expenditure += item.amount

    month_info["income"] = income
    month_info["expenditure"] = expenditure

    return month_info
