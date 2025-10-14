from fastapi import APIRouter, HTTPException
from db import session
from model.common import raise_http_exception
from model.digimonModel import *
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy import text

router = APIRouter()


@router.post("/insert", summary="디지몬 등록")
async def insert_digimon(item: Digimon):
    """
    디지몬 등록
    - **name**: 디지몬 이름
    - **level**: 레벨
    - **type**: 타입
    - **property**: 속성
    - **field**: 소속 필드
    - **lethalMove**: 필사기
    - **description**: 설명
    - **image**: 이미지
    - **sprites**: sprites
    """
    data = session.query(DigimonTable).filter(DigimonTable.name == item.name).first()
    if data is None:
        digimon = create_digimon(item)
        session.add(digimon)
        session.commit()

    return f"{item.name} 추가 완료"


@router.post("/select", summary="디지몬 조회")
async def select_digimon():
    """
    디지몬 조회
    """
    return session\
        .query(DigimonTable.id, DigimonTable.name, DigimonLevelTable.level, DigimonTable.type, DigimonTable.field,
               DigimonTable.description, DigimonTable.sprites, DigimonTable.property,
               DigimonTable.lethalMove, DigimonTable.image)\
        .join(DigimonLevelTable, DigimonLevelTable.id == DigimonTable.levelId)\
        .all()


@router.post("/insert/dmo", summary="DMO 디지몬 추가")
async def insert_dmo(data: DmoDigimonGroupCreate):
    """
    - ** groupName**: 디지몬 그룹 이름
    - ** list**: 디지몬 리스트
    - ** name**: 디지몬 이름
    - ** isOpen**: 오픈 여부
    - ** isTranscend**: 초월 여부
    - ** level**: 레벨
    """
    new_group = DmoDigimonGroupTable(name=data.groupName)
    session.add(new_group)
    session.commit()
    session.refresh(new_group)

    try:
        for digimon_data in data.list:
            new_digimon = DmoDigimonTable(
                name=digimon_data.name,
                isOpen=digimon_data.isOpen,
                isTranscend=digimon_data.isTranscend,
                level=digimon_data.level,
                image="default.png",
                groupId=new_group.id
            )
            session.add(new_digimon)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("등록에 실패하였습니다")

    return {
        "groupId": new_group.id,
        "groupName": new_group.name,
        "insertedDigimonCount": len(data.list)
    }
