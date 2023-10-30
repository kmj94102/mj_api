from fastapi import APIRouter, HTTPException
from db import session
from model import AccountBook, AccountBookItem, create_account_book, DateConfiguration, AccountBookInsertItem, \
    FrequentlyAccountBook, FrequentlyAccountBookItem, create_frequently_account_book, \
    FixedAccountBook, FixedAccountBookItem, create_fixed_account_book

from datetime import datetime
from typing import List

from sqlalchemy import update, delete
from sqlalchemy import func

router = APIRouter()


@router.post("/insert")
async def insert_account_book(item: AccountBookInsertItem):
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

    if item.isAddFrequently:
        await insert_frequently_account_book(create_frequently_account_book(item))

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


@router.post("/select/summaryThisMonth")
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


@router.post("/select/lastMonthAnalysis")
async def select_last_month_analysis(config: DateConfiguration):
    session.commit()

    date = config.date
    lastMonth = datetime(date.year, date.month - 1, date.day)

    date_format = "%Y.%m.%d"
    start_date = calculate_start_date(lastMonth, config.baseDate)
    end_date = calculate_end_date(lastMonth, config.baseDate)

    result = session.query(
        AccountBook.usageType,
        func.sum(AccountBook.amount).label("amount")
    ).filter(
        AccountBook.date >= start_date,
        AccountBook.date <= end_date
    ).group_by(
        AccountBook.usageType
    ).order_by(
        func.sum(AccountBook.amount).desc()
    ).all()

    return {
        "start": start_date.strftime("%Y.%m.%d"),
        "end": end_date.strftime("%Y.%m.%d"),
        "result": result
    }


@router.post("/select/thisYearSummary")
async def select_this_year_summary(config: DateConfiguration):
    date_ranges = []
    currentDate = config.date

    for month in range(1, 13):
        new_date = datetime(currentDate.year, month, config.baseDate)
        start_date = calculate_start_date(new_date, config.baseDate)
        end_date = calculate_end_date(new_date, config.baseDate)
        info = session.query(
            func.sum(AccountBook.amount).label("amount")
        ).filter(
            AccountBook.date >= start_date,
            AccountBook.date <= end_date
        ).first()

        if info["amount"] is None:
            sum = 0
        else:
            sum = info["amount"]

        date_ranges.append({"month": end_date.month, "startDate": start_date.strftime("%Y.%m.%d"),
                            "endDate": end_date.strftime("%Y.%m.%d"), "info": sum})
        date = start_date
    return date_ranges


@router.post("/select/info")
async def select_account_book(config: DateConfiguration):
    this_month = await select_account_summary_this_month(config)
    last_month = await select_last_month_analysis(config)
    this_year = await select_this_year_summary(config)
    return {
        "thisMonthSummary": this_month,
        "lastMonthAnalysis": last_month,
        "thisYearSummary": this_year
    }


@router.post("/select/thisMonthDetail")
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


@router.post("/insert/frequently")
async def insert_frequently_account_book(item: FrequentlyAccountBookItem):
    data = session.query(FrequentlyAccountBook).filter(FrequentlyAccountBook.whereToUse == item.whereToUse,
                                                       FrequentlyAccountBook.amount == item.amount).first()

    if data is None:
        frequently = create_frequently_account_book(item)
        session.add(frequently)
        session.commit()

    return f"{item.whereToUse} 추가 완료"


@router.post("/insert/fixed")
async def insert_fixed_account_book(item: FixedAccountBookItem):
    data = session.query(FixedAccountBook).filter(FixedAccountBook.whereToUse == item.whereToUse,
                                                  FixedAccountBook.amount == item.amount).first()

    if data is None:
        fixed = create_fixed_account_book(item)
        session.add(fixed)
        session.commit()

    return f"{item.whereToUse} 추가 완료"


@router.delete("/delete/fixed")
async def delete_fixed_account_book(id: int):
    fixed = session.query(FixedAccountBook).filter(FixedAccountBook.id == id).first()

    if not fixed:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(FixedAccountBook).filter(FixedAccountBook.id == id).delete(synchronize_session=False)
    session.commit()


@router.post("/select/fixed")
async def select_fixed_account_book():
    return session.query(FixedAccountBook).all()


@router.delete("/delete/frequently")
async def delete_frequently_account_book(id: int):
    frequently = session.query(FrequentlyAccountBook).filter(FrequentlyAccountBook.id == id).first()

    if not frequently:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.delete(frequently)
    session.commit()


@router.post("/select/frequently")
async def select_frequently_account_book():
    return session.query(FrequentlyAccountBook).all()