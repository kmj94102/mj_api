from fastapi import APIRouter

from db import session
from model.personaModel import *

router = APIRouter()


@router.post("/3/insert/schedule", summary="스캐줄 등록")
async def insert_persona3_schedule(item: Persona3Schedule):
    """
    스캐줄 등록
    - **month**: 월
    - **day**: 일
    - **dayOfWeek**: 요일
    - **title**: 제목
    - **contents**: 내용
    - **rank**: 랭크
    - **isComplete**: 완료 여부
    - **communityIdx**: 커뮤니티 아이디
    """

    schedule = item.toTable()
    session.add(schedule)
    session.commit()
    return f"{item.title} 추가 완료"


@router.post("/3/select/schedule", summary="스케줄 조회")
async def select_persona3_schedule(item: ScheduleParam):
    """
    ***skip: 마지막 번호***
    ***limit: 조회 개수***
    """
    _list = session.query(Persona3ScheduleTable)\
        .filter(not Persona3ScheduleTable.isComplete == False)\
        .offset(item.skip).limit(item.limit).all()

    return _list


@router.post("/3/update/schedule", summary="스케줄 상태 업데이트")
async def update_persona3_update(item: ScheduleUpdateParam):
    """"
    ***idxList: 스케줄 아이디 리스트***
    """
    session.query(Persona3ScheduleTable)\
        .filter(Persona3ScheduleTable.idx.in_(item.idxList))\
        .update({Persona3ScheduleTable.isComplete: True})

    session.commit()
    return "업데이트 완료"


@router.post("/3/select/community", summary="커뮤니티 조회")
async def select_persona3_community():
    session.commit()
    _list = session.query(Persona3CommunityTable).all()
    return _list


@router.post("/3/update/community", summary="커뮤니티 랭크 업데이트")
async def update_persona3_community(item: CommunityUpdateParam):
    """
    ***idx: 아이디***
    ***rank: 랭크***
    """
    session.query(Persona3CommunityTable)\
        .filter(Persona3CommunityTable.idx == item.idx)\
        .update({Persona3CommunityTable.rank: item.rank})

    session.commit()
    return "업데이트 완료"
