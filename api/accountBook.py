from fastapi import APIRouter, HTTPException
from db import session
from model.model import AccountBook, create_account_book, DateConfiguration, AccountBookInsertItem, \
    FrequentlyAccountBook, FrequentlyAccountBookItem, create_frequently_account_book, \
    FixedAccountBook, FixedAccountBookItem, create_fixed_account_book

from datetime import datetime

from sqlalchemy import func

router = APIRouter()


@router.post("/insert", summary="가계부 등록")
async def insert_account_book(item: AccountBookInsertItem):
    """
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


@router.post("/select/summaryThisMonth", summary="이번달 내역 조회")
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


@router.post("/select/lastMonthAnalysis", summary="지난달 내역 조회")
async def select_last_month_analysis(config: DateConfiguration):
    session.commit()

    lastMonth = calculate_last_month(config)

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

    result_with_percentages = add_percentages(result)

    return {
        "start": start_date.strftime("%Y.%m.%d"),
        "end": end_date.strftime("%Y.%m.%d"),
        "result": result_with_percentages
    }


def add_percentages(result):
    # 음수와 양수를 분리
    positive_entries = [entry for entry in result if entry["amount"] >= 0]
    negative_entries = [entry for entry in result if entry["amount"] < 0]

    # 각각의 총합 계산
    total_positive = sum(entry["amount"] for entry in positive_entries) if positive_entries else 0
    total_negative = sum(entry["amount"] for entry in negative_entries) if negative_entries else 0

    # 결과에 퍼센트 추가
    result_with_percentages = []
    for entry in sorted(positive_entries, key=lambda x: x["amount"], reverse=True):
        percentage = 0
        if entry["amount"] >= 0 and total_positive != 0:
            percentage = round((entry["amount"] / total_positive) * 100, 2)

        result_with_percentages.append({
            "usageType": entry["usageType"],
            "amount": entry["amount"],
            "percentage": percentage
        })

    for entry in sorted(negative_entries, key=lambda x: x["amount"]):
        percentage = 0
        if entry["amount"] < 0 and total_negative != 0:
            percentage = round((entry["amount"] / total_negative) * 100, 2)

        result_with_percentages.append({
            "usageType": entry["usageType"],
            "amount": entry["amount"],
            "percentage": percentage
        })

    return result_with_percentages


def calculate_last_month(config: DateConfiguration):
    date = config.date
    baseDate = config.baseDate

    if date.day > baseDate:
        lastMonth = date.replace(day=baseDate + 1)
    else:
        lastMonth = date

    if date.month > 1:
        lastMonth = lastMonth.replace(month=date.month - 1)
    else:
        lastMonth = lastMonth.replace(year=date.year - 1, month=12)

    return lastMonth


@router.post("/select/thisYearSummary", summary="올해 내역 조회")
async def select_this_year_summary(config: DateConfiguration):
    date_ranges = []
    currentDate = config.date

    for month in range(1, 13):
        new_date = datetime(currentDate.year, month, config.baseDate)
        start_date = calculate_start_date(new_date, config.baseDate)
        end_date = calculate_end_date(new_date, config.baseDate)
        item = session.query(
            func.sum(AccountBook.amount).label("amount")
        ).filter(
            AccountBook.date >= start_date,
            AccountBook.date <= end_date
        ).first()

        if item["amount"] is None:
            info = 0
        else:
            info = item["amount"]

        date_ranges.append({"month": end_date.month, "startDate": start_date.strftime("%Y.%m.%d"),
                            "endDate": end_date.strftime("%Y.%m.%d"), "info": info})
    return date_ranges


@router.post("/select/info", summary="가계부 전체 조회")
async def select_account_book(config: DateConfiguration):
    this_month = await select_account_summary_this_month(config)
    last_month = await select_last_month_analysis(config)
    this_year = await select_this_year_summary(config)
    return {
        "thisMonthSummary": this_month,
        "lastMonthAnalysis": last_month,
        "thisYearSummary": this_year
    }


@router.post("/select/thisMonthDetail", summary="이번달 내역 상세 조회")
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


# 미사용
@router.post("/insert/frequently")
async def insert_frequently_account_book(item: FrequentlyAccountBookItem):
    data = session.query(FrequentlyAccountBook).filter(FrequentlyAccountBook.whereToUse == item.whereToUse,
                                                       FrequentlyAccountBook.amount == item.amount).first()

    if data is None:
        frequently = create_frequently_account_book(item)
        session.add(frequently)
        session.commit()

    return f"{item.whereToUse} 추가 완료"


@router.post("/insert/fixed", summary="고정 내역 추가")
async def insert_fixed_account_book(item: FixedAccountBookItem):
    data = session.query(FixedAccountBook).filter(FixedAccountBook.whereToUse == item.whereToUse,
                                                  FixedAccountBook.amount == item.amount).first()

    if data is None:
        fixed = create_fixed_account_book(item)
        session.add(fixed)
        session.commit()

    return f"{item.whereToUse} 추가 완료"


@router.delete("/delete/fixed", summary="고정 내역 삭제")
async def delete_fixed_account_book(id_: int):
    fixed = session.query(FixedAccountBook).filter(FixedAccountBook.id == id_).first()

    if not fixed:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.query(FixedAccountBook).filter(FixedAccountBook.id == id_).delete(synchronize_session=False)
    session.commit()


@router.post("/select/fixed", summary="고정 내역 조회")
async def select_fixed_account_book():
    return session.query(FixedAccountBook).all()


@router.delete("/delete/frequently", summary="즐겨찾기 삭제")
async def delete_frequently_account_book(id_: int):
    frequently = session.query(FrequentlyAccountBook).filter(FrequentlyAccountBook.id == id_).first()

    if not frequently:
        raise HTTPException(status_code=404, detail="존재하지 않는 id입니다.")

    session.delete(frequently)
    session.commit()


@router.post("/select/frequently", summary="즐겨찾기 조회")
async def select_frequently_account_book():
    return session.query(FrequentlyAccountBook).all()
