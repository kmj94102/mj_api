from fastapi import APIRouter, HTTPException
from db import session
from model import Calendar, CalendarItem, create_calendar, \
    Schedule, ScheduleItem, create_schedule, \
    Plan, PlanItem, create_plan, PlanTasks, \
    Task, TaskItem, create_task, TaskUpdateItem

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import update, delete

router = APIRouter()


# 달력 정보 추가
@router.post("/insert")
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
@router.get("/select/month")
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


@router.get("/select/week")
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
@router.post("/insert/schedule")
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

@router.get("/select/schedule")
async def read_schedule(date: datetime):
    session.commit()

    return session.query(Schedule).filter(
        Schedule.startTime >= date,
        Schedule.endTime <= date + timedelta(days=1)
    ).all()


@router.delete("/delete/schedule")
async def delete_schedule(id: int):
    schedule = session.query(Schedule).filter(Schedule.id == id).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(Schedule).filter(Schedule.recurrenceId == id).delete(synchronize_session=False)

    session.delete(schedule)
    session.commit()

    return "일정을 삭제하였습니다."


@router.post("/insert/plan")
async def insert_plan(title, date):
    plan = Plan()
    plan.title = title
    plan.planDate = date

    session.add(plan)
    session.flush()
    session.commit()
    session.refresh(plan)

    return plan.id


@router.post("/insert/task")
async def insert_task(item: TaskItem):
    task = create_task(item)
    session.add(task)
    session.commit()

    return f"{item.contents} 추가 완료"


@router.post("/update/task")
async def update_task(item: TaskUpdateItem):
    date_format = '%Y.%m.%d'
    task = session.query(Task).filter(Task.id == item.id).first()
    task.isCompleted = item.isCompleted
    session.commit()

    formatted_date = datetime.strptime(item.date, date_format)
    return await read_calendar(formatted_date)


@router.post("/insert/planTasks")
async def insert_plan_tasks(item: PlanTasks):
    planId = await insert_plan(item.title, item.planDate)

    for taskItem in item.taskList:
        taskItem.planId = planId
        await insert_task(taskItem)

    return f"{item.title} 등록 완료"


@router.delete("/delete/planTasks")
async def delete_plan_tasks(id: int):
    plan = session.query(Plan).filter(Plan.id == id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(Task).filter(Task.planId == id).delete(synchronize_session=False)

    session.delete(plan)
    session.commit()

    return "계획 삭제 완료"


@router.get("/select/plansTasks")
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