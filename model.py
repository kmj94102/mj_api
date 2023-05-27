from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from pydantic import BaseModel
from db import Base
from db import ENGINE
from typing import List
from typing import Optional
from datetime import datetime


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
    shinySpotlight = Column(String(500))
    description = Column(String(500))
    generation = Column(Integer)
    isCatch = Column(Boolean)


class Pokemon(BaseModel):
    index: int = None
    number: str = None
    name: str = None
    status: str = None
    classification: str = None
    characteristic: str = None
    attribute: str = None
    image: str = None
    shinyImage: str = None
    spotlight: str = None
    shinySpotlight: str = None
    description: str = None
    generation: int = None
    isCatch: bool = False


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
    pokemon.shinySpotlight = item.shinySpotlight
    pokemon.shinyImage = item.shinyImage
    pokemon.description = item.description
    pokemon.generation = item.generation
    pokemon.isCatch = item.isCatch

    return pokemon


class CharacteristicTable(Base):
    __tablename__ = 'characteristic'
    index = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45))
    description = Column(String(200))


class Characteristic(BaseModel):
    index: int = None
    name: str = None
    description: str = None


def create_characteristic_table(item: Characteristic) -> CharacteristicTable:
    charTable = CharacteristicTable()
    charTable.name = item.name
    charTable.description = item.description
    return charTable


class UpdateIsCatch(BaseModel):
    number: str
    isCatch: bool


class Calendar(Base):
    __tablename__ = "calendar"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendarDate = Column(DateTime)
    dateInfo = Column(String(255))
    isHoliday = Column(Boolean)
    isSpecialDay = Column(Boolean)


class CalendarItem(BaseModel):
    calendarDate: datetime
    dateInfo: str
    isHoliday: Optional[bool] = False
    isSpecialDay: bool = False


def create_calendar(item: CalendarItem) -> Calendar:
    calendar = Calendar()
    calendar.calendarDate = item.calendarDate
    calendar.dateInfo = item.dateInfo
    calendar.isHoliday = item.isHoliday
    calendar.isSpecialDay = item.isSpecialDay

    return calendar


class Plan(Base):
    __tablename__ = "plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    planDate = Column(DateTime)


class PlanItem(BaseModel):
    title: str
    planDate: datetime


def create_plan(item: PlanItem) -> Plan:
    plan = Plan()
    plan.title = item.title
    plan.planDate = item.planDate

    return plan


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    planId = Column(Integer)
    contents = Column(String(255))
    isCompleted = Column(Boolean)


class TaskItem(BaseModel):
    planId: int
    contents: str
    isCompleted: bool


def create_task(item: TaskItem) -> Task:
    task = Task()
    task.planId = item.planId
    task.contents = item.contents
    task.isCompleted = item.isCompleted

    return task


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, autoincrement=True)
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    recurrenceType = Column(String(50))
    recurrenceEndDate = Column(DateTime)
    scheduleContent = Column(String(255))
    scheduleTitle = Column(String(255))
    recurrenceId = Column(Integer, nullable=True)


class ScheduleItem(BaseModel):
    startTime: datetime
    endTime: datetime
    recurrenceType: str
    recurrenceEndDate: Optional[datetime]
    scheduleContent: str
    scheduleTitle: str


def create_schedule(item: ScheduleItem, recurrence_id: Optional[int] = None) -> Schedule:
    schedule = Schedule()
    schedule.startTime = item.startTime
    schedule.endTime = item.endTime
    schedule.recurrenceType = item.recurrenceType
    schedule.recurrenceEndDate = item.recurrenceEndDate
    schedule.scheduleContent = item.scheduleContent
    schedule.scheduleTitle = item.scheduleTitle
    schedule.recurrenceId = recurrence_id

    return schedule


class Elsword(Base):
    __tablename__ = 'elsword'

    id = Column(Integer, primary_key=True, autoincrement=True)
    characterGroup = Column(String(255))
    line = Column(Integer)
    classType = Column(String(255))
    name = Column(String(255))
    engName = Column(String(255))
    attackType = Column(String(255))
    story = Column(Text)
    bigImage = Column(Text)
    questImage = Column(Text)
    progressImage = Column(Text)
    circleImage = Column(Text)


class ElswordItem(BaseModel):
    characterGroup: str
    line: int
    classType: str
    name: str
    engName: str
    attackType: str
    story: str
    bigImage: str
    questImage: str
    progressImage: str
    circleImage: str


def create_elsword(item: ElswordItem) -> Elsword:
    elsword = Elsword()
    elsword.characterGroup = item.characterGroup
    elsword.line = item.line
    elsword.classType = item.classType
    elsword.name = item.name
    elsword.engName = item.engName
    elsword.attackType = item.attackType
    elsword.story = item.story
    elsword.bigImage = item.bigImage
    elsword.questImage = item.questImage
    elsword.progressImage = item.progressImage
    elsword.circleImage = item.circleImage

    return elsword


class Quest(Base):
    __tablename__ = 'quest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    max = Column(Integer)
    complete = Column(Text)
    ongoing = Column(Text)


class QuestItem(BaseModel):
    name: str
    max: int
    complete: str
    ongoing: str


def create_quest(item: QuestItem) -> Quest:
    quest = Quest()
    quest.name = item.name
    quest.max = item.max
    quest.complete = item.complete
    quest.ongoing = item.ongoing

    return quest


class QuestProgress(Base):
    __tablename__ = 'quest_progress'

    id = Column(Integer, primary_key=True)
    quest_id = Column(Integer)
    progress = Column(Integer)
    name = Column(String(255))


class QuestProgressItem(BaseModel):
    quest_id: int
    progress: int
    name: str


def create_init_quest_progress(id: int, name: str):
    progress = QuestProgress()
    progress.quest_id = id
    progress.progress = 1
    progress.name = name

    return progress


class QuestUpdateItem(BaseModel):
    id: int
    name: str
    type: str


def main():
    # Table 없으면 생성
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
