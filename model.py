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


class EvolutionTable(Base):
    __tablename__ = 'evolution'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    numbers = Column(String(100))
    beforeNum = Column(String(45))
    afterNum = Column(String(45))
    evolutionType = Column(String(100))
    evolutionCondition = Column(String(100))


class Evolution(BaseModel):
    numbers: str
    beforeNum: str
    afterNum: str
    evolutionType: str
    evolutionCondition: str


def create_evolution_table(item: Evolution) -> EvolutionTable:
    evolution = EvolutionTable()
    evolution.numbers = item.numbers
    evolution.beforeNum = item.beforeNum
    evolution.afterNum = item.afterNum
    evolution.evolutionType = item.evolutionType
    evolution.evolutionCondition = item.evolutionCondition

    return evolution


class EvolutionTypeTable(Base):
    __tablename__ = 'evolution_type'
    name = Column(String(45), primary_key=True)
    image = Column(Text)


class EvolutionType(BaseModel):
    name: str
    image: str


def create_evolution_type_table(item: EvolutionType):
    evolution_type = EvolutionTypeTable()
    evolution_type.name = item.name
    evolution_type.image = item.image

    return evolution_type


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


class UpdatePokemonImage(BaseModel):
    number: str
    spotlight: str


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


class PlanTasks(BaseModel):
    title: str
    planDate: datetime
    taskList: List[TaskItem]


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
    if recurrence_id is not None:
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


def create_init_quest_progress(id: int, name: str, progress_value: Optional[int] = 1):
    progress = QuestProgress()
    progress.quest_id = id
    progress.progress = progress_value
    progress.name = name

    return progress


class QuestUpdateItem(BaseModel):
    id: int
    name: str
    type: str
    progress: int


class QuestProgressUpdateItem(BaseModel):
    id: int
    max: int


class AccountBook(Base):
    __tablename__ = 'account_book'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    dateOfWeek = Column(String(50))
    amount = Column(Integer)
    usageType = Column(String(100))
    whereToUse = Column(Text)


class AccountBookItem(BaseModel):
    id: int
    date: datetime
    dateOfWeek: str
    amount: int
    usageType: str
    whereToUse: str


class AccountBookInsertItem(BaseModel):
    id: int
    date: datetime
    dateOfWeek: str
    amount: int
    usageType: str
    whereToUse: str
    isAddFrequently: bool


def create_account_book(item: AccountBookInsertItem) -> AccountBook:
    accountBook = AccountBook()
    accountBook.id = item.id
    accountBook.date = item.date
    accountBook.dateOfWeek = item.dateOfWeek
    accountBook.amount = item.amount
    accountBook.usageType = item.usageType
    accountBook.whereToUse = item.whereToUse

    return accountBook


class DateConfiguration(BaseModel):
    date: datetime
    baseDate: int


class FrequentlyAccountBook(Base):
    __tablename__ = "frequently_account_book"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    usageType = Column(String(100))
    whereToUse = Column(Text)


class FrequentlyAccountBookItem(BaseModel):
    id: int
    amount: int
    usageType: str
    whereToUse: str


def create_frequently_account_book(item: AccountBookInsertItem) -> FrequentlyAccountBook:
    frequentlyAccountBook = FrequentlyAccountBook()
    frequentlyAccountBook.id = item.id
    frequentlyAccountBook.amount = item.amount
    frequentlyAccountBook.usageType = item.usageType
    frequentlyAccountBook.whereToUse = item.whereToUse

    return frequentlyAccountBook


class FixedAccountBook(Base):
    __tablename__ = "fixed_account_book"

    id = Column(Integer, primary_key=True)
    date = Column(String(10))
    amount = Column(Integer)
    usageType = Column(String(100))
    whereToUse = Column(Text)
    isIncome = Column(Boolean)


class FixedAccountBookItem(BaseModel):
    id: int
    date: str
    amount: int
    usageType: str
    whereToUse: str
    isIncome: bool


def create_fixed_account_book(item: FixedAccountBookItem) -> FixedAccountBook:
    fixedAccountBook = FixedAccountBook()
    fixedAccountBook.id = item.id
    fixedAccountBook.date = item.date
    fixedAccountBook.amount = item.amount
    fixedAccountBook.usageType = item.usageType
    fixedAccountBook.whereToUse = item.whereToUse
    fixedAccountBook.isIncome = item.isIncome

    return fixedAccountBook


class HomeParam(BaseModel):
    startDate: str
    endDate: str


def main():
    # Table 없으면 생성
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
