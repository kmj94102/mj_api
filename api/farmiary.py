from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete

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
    session.add(item.toTable())
    session.commit()


@router.post("/plant/delete", summary="식물 삭제")
def delete_plant(item: IdParam):
    plant = session.query(PlantTable).filter(PlantTable.idx == item.idx).all()

    if not plant:
        raise HTTPException(status_code=400, detail="잘못된 요청입니다.")

    session.execute(delete(PlantTable).where(PlantTable.idx == item.idx))
    session.commit()
    return f"{plant.name} 삭제 완료"


@router.post("/schedule/insert")
def insert_schedule(item: ScheduleParam):
    session.commit()


@router.get("/schedule/select")
async def read_calendar_month(year: int, month: int):
    session.commit()
    start_date = datetime(year, month, 1)
    end_date = get_last_day_time(year, month)
    current_date = start_date

    result = []

    while current_date < end_date:
        day_data = await read_schedule(current_date)
        result.append(day_data)
        current_date += timedelta(days=1)

    return result


async def read_schedule(current_date: datetime):
    session.query()
