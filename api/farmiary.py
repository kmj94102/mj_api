import calendar
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from sqlalchemy.orm import selectinload

from api.common import get_last_day_time
from db import session
from model.farmiaryModel import *

router = APIRouter()


@router.post("/user/newUser", summary="회원가입")
def insert_new_user(item: FarmiaryUser):
    """
    회원가입
    - **loginType**: 로그인 타입, ["KAKAO", "GOOGLE", "NAVER"] 중 택 1
    - **email**: 이메일
    - **name**: 이름
    - **profileImage**: 프로필 이미지
    """

    loginType = {"KAKAO", "GOOGLE", "NAVER"}

    if not(item.loginType in loginType):
        raise HTTPException(status_code=400, detail="회원가입 방식을 확인해주세요.")
    if not(1 <= len(item.name) <= 10):
        raise HTTPException(status_code=400, detail="이름을 확인해주세요.")

    data = session.query(FarmiaryUserTable).filter(FarmiaryUserTable.email == item.email).all()

    if data:
        raise HTTPException(status_code=400, detail="이미 회원가입한 이메일입니다.")

    session.add(item.toTable())
    session.commit()
    return f"${item.name}님, 환영합니다"


@router.post("/user/withdrawal", summary="회원탈퇴")
def withdrawal(item: IdParam):
    """
    회원탈퇴
    - **idx**: 유저 idx
    """
    session.commit()

    data = session.query(FarmiaryUserTable).filter(FarmiaryUserTable.idx == item.idx).all()
    if data is None:
        raise HTTPException(status_code=400, detail="아이디를 확인해주세요.")

    session.execute(delete(FarmiaryUserTable).where(FarmiaryUserTable.idx == item.idx))
    session.commit()
    return "회원 탈퇴하였습니다."


@router.post("/user/login", summary="로그인")
def login(item: LoginParam):
    """"
    로그인
    - **email**: 이메일
    - **loginType**: 로그인 타입
    """
    session.commit()
    user = session.query(FarmiaryUserTable).filter(FarmiaryUserTable.email == item.email).first()

    if user is None:
        raise HTTPException(status_code=400, detail="회원가입 후 이용해주세요.")

    if user.login_type != item.loginType:
        raise HTTPException(status_code=401, detail="다른 방식으로 가입하셨습니다.")

    farmCount = session.query(
        FarmTable.idx, FarmTable.name, FarmTable.address, FarmTable.info, FarmTable.qr, FarmGroupTable.role
    ).filter(FarmGroupTable.user_idx == user.idx, FarmTable.idx == FarmGroupTable.farm_idx).count()

    return {
        "idx": user.idx,
        "email": user.email,
        "name": user.name,
        "profileImage": user.profile_image,
        "isJoinFarm": farmCount != 0
    }


@router.post("/farm/newFarm", summary="신규 팜 등록")
def insert_new_farm(item: NewAddFarm):
    try:
        session.begin()
        farm = item.toFarmTable()
        session.add(farm)
        session.flush()

        farmGroup = item.toFarmGroupTable(farmIdx=farm.idx)
        session.add(farmGroup)
        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()

    return f"'{item.name}' 등록 완료"


@router.post("/farm/join", summary="팜 가입")
def join_farm(item: JoinFarm):
    farm = session.query(FarmTable).filter(FarmTable.qr == item.qr).first()
    if farm is None:
        raise HTTPException(status_code=400, detail="잘못된 qr코드 입니다.")

    group = session.query(FarmGroupTable)\
        .filter(FarmGroupTable.farm_idx == farm.idx, FarmGroupTable.user_idx == item.userIdx)\
        .all()

    if group:
        raise HTTPException(status_code=400, detail="이미 가입된 팜입니다.")

    session.add(item.toTable(farmIdx=farm.idx))
    session.commit()

    return f"'{farm.name}' 가입 완료"


@router.post("/farm/withdrawal", summary="팜 탈퇴")
def withdrawal_farm(item: WithdrawalFarm):
    session.commit()

    group = session.query(FarmGroupTable)\
        .filter(FarmGroupTable.farm_idx == item.farmIdx, FarmGroupTable.user_idx == item.userIdx)\
        .first()

    if group is None:
        raise HTTPException(status_code=400, detail="잘못된 팜입니다.")

    print(f"\n\n\nrole = {group.role}\n\n\n")

    if group.role == "MASTER":
        raise HTTPException(status_code=401, detail="팜 관리자는 탈퇴할 수 업습니다. 팜 해제를 이용해주세요.")

    session.execute(delete(FarmGroupTable)
                    .where(FarmGroupTable.farm_idx == item.farmIdx, FarmGroupTable.user_idx == item.userIdx))
    session.commit()
    return "팜 탈퇴 완료"


@router.post("/farm/delete", summary="팜 삭제")
def delete_farm(item: WithdrawalFarm):
    session.commit()

    group = session.query(FarmGroupTable) \
        .filter(FarmGroupTable.farm_idx == item.farmIdx, FarmGroupTable.user_idx == item.userIdx) \
        .first()

    if group is None:
        raise HTTPException(status_code=400, detail="잘못된 팜입니다.")

    if group.role != "MASTER":
        raise HTTPException(status_code=401, detail="팜 삭제는 관리자만 이용 가능합니다.")

    session.execute(delete(FarmTable).where(FarmTable.idx == item.farmIdx))
    session.commit()
    return "팜 삭제 완료"


@router.post("/farm/select", summary="팜 조회")
def select_farm(item: IdParam):
    session.commit()

    farmList = session.query(
        FarmTable.idx, FarmTable.name, FarmTable.address, FarmTable.info, FarmTable.qr, FarmGroupTable.role
    ).filter(FarmGroupTable.user_idx == item.idx, FarmTable.idx == FarmGroupTable.farm_idx).all()

    return farmList


@router.post("/plant/insert", summary="식물 등록")
def insert_plant(item: Plant):
    plant = item.toTable()
    session.add(plant)
    session.commit()

    return f"{item.name} 등록 완료"


@router.post("/plant/delete", summary="식물 삭제")
def delete_plant(item: IdParam):
    plant = session.query(PlantTable).filter(PlantTable.idx == item.idx).all()

    if not plant:
        raise HTTPException(status_code=400, detail="잘못된 요청입니다.")

    session.execute(delete(PlantTable).where(PlantTable.idx == item.idx))
    session.commit()
    return f"{plant.name} 삭제 완료"


@router.post("/schedule/insert", summary="일정 등록")
def insert_schedule(item: ScheduleParam):
    session.commit()

    try:
        session.begin()
        schedule = item.toScheduleTable()
        session.add(schedule)
        session.flush()

        for plantIdx in item.plantList:
            plant = SchedulePlantTable(
                schedule_idx=schedule.idx,
                plant_idx=plantIdx
            )
            session.add(plant)

        for workerIdx in item.workerList:
            worker = ScheduleWorkerTable(
                schedule_idx=schedule.idx,
                user_idx=workerIdx
            )
            session.add(worker)

        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()

    return "등록 완료"


def get_schedules(
    start: datetime,
    end: datetime,
    userIdx: int
):
    schedules = (
        session.query(ScheduleTable)
        .join(FarmGroupTable, FarmGroupTable.farm_idx == ScheduleTable.farm_idx)
        .filter(FarmGroupTable.user_idx == userIdx)
        .filter(ScheduleTable.scheduled_at.between(start, end))
        .options(
            selectinload(ScheduleTable.plants).selectinload(SchedulePlantTable.plant),
            selectinload(ScheduleTable.workers).selectinload(ScheduleWorkerTable.user),
        )
        .order_by(ScheduleTable.scheduled_at)
        .all()
    )

    return schedules


@router.post("/schedule/select/month", summary="일정 조회(월)")
async def read_calendar_month(item: MonthScheduleParam):
    first_day = datetime(item.year, item.month, 1)
    last_day_num = calendar.monthrange(item.year, item.month)[1]
    last_day = datetime(item.year, item.month, last_day_num)

    weekday = first_day.weekday()
    start_index = (weekday + 1) % 7

    rows = get_schedules(first_day, last_day, item.userIdx)

    data_map = {}

    for row in rows:
        date_key = row.scheduled_at.strftime("%Y.%m.%d")

        if date_key not in data_map:
            data_map[date_key] = []

        data_map[date_key].append(row)

    result = []

    for _ in range(start_index):
        result.append(None)

    for day in range(1, last_day_num + 1):
        date_str = f"{item.year}.{item.month:02d}.{day:02d}"

        result.append({
            "date": date_str,
            "data": data_map.get(date_str, [])
        })

    return result


async def read_schedule(current_date: datetime):
    session.query()
