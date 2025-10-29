from fastapi import APIRouter
from db import session
from model.common import raise_http_exception
from model.digimonModel import *

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
    return session \
        .query(DigimonTable.id, DigimonTable.name, DigimonLevelTable.level, DigimonTable.type, DigimonTable.field,
               DigimonTable.description, DigimonTable.sprites, DigimonTable.property,
               DigimonTable.lethalMove, DigimonTable.image) \
        .join(DigimonLevelTable, DigimonLevelTable.id == DigimonTable.levelId) \
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


@router.post("/select/search/dmo", summary="DMO 디지몬 검색")
async def select_search_dmo(data: DmoSearch):
    session.commit()
    result = session.query(
        DmoDigimonTable.id.label("digimonId"),
        DmoDigimonTable.name.label("digimonName"),
        DmoDigimonGroupTable.name.label("groupName")
    ).join(DmoDigimonGroupTable, DmoDigimonTable.groupId == DmoDigimonGroupTable.id).filter(
        DmoDigimonTable.name.like(f"%{data.name}%")).all()

    return result


@router.post("/insert/dmo/union", summary="DMO 유니온 등록")
async def insert_dmo_union(item: DigimonUnionInsertParam):
    new_group = DmoUnionGroupTable(name=item.unionName)
    session.add(new_group)
    session.commit()
    session.refresh(new_group)

    try:
        for digimon in item.digimonList:
            newUnion = DmoUnionTable(digimonId=digimon.digimonId, unionId=new_group.id)
            session.add(newUnion)

        for data in item.rewardNConditions:
            condition = DmoUnionConditionsTable(conditionId=data.conditionType, conditionValue=data.conditionValue,
                                                rewardId=data.rewardType, rewardValue=data.rewardValue,
                                                unionId=new_group.id)
            session.add(condition)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("등록에 실패하였습니다")


@router.post('/select/dmo/union/list', summary="DMO 유니온 리스트 조회")
async def select_dmo_union_list():
    session.commit()

    groupList = session.query(DmoUnionGroupTable).order_by(
        DmoUnionGroupTable.isFavorite.desc()
    ).all()

    return [
        {
            "unionId": group.id,
            "groupName": group.name,
            "isFavorite": group.isFavorite,
            "conditions": session.query(
                DmoUnionConditionsTable.id, DmoRewardTypeTable.type.label('rewardType'),
                DmoUnionConditionsTable.rewardValue, DmoConditionTypeTable.type.label('conditionType'),
                DmoUnionConditionsTable.conditionValue, DmoUnionProgressTable.isComplete
            ).where(
                DmoUnionConditionsTable.unionId == group.id
            ).join(
                DmoUnionProgressTable, isouter=True
            ).join(
                DmoConditionTypeTable
            ).join(
                DmoRewardTypeTable
            ).all()
        }
        for group in groupList
    ]


@router.post("/select/union/detail", summary="DMO 유니온 상세 조회")
async def select_dmo_union_detail(item: IdParam):
    session.commit()

    unionGroupName = session.query(DmoUnionGroupTable.name).where(DmoUnionGroupTable.id == item.id).first()

    conditionInfo = session.query(
        DmoUnionConditionsTable.id, DmoRewardTypeTable.type.label('rewardType'), DmoUnionConditionsTable.rewardId,
        DmoUnionConditionsTable.rewardValue, DmoConditionTypeTable.type.label('conditionType'),
        DmoUnionConditionsTable.conditionId, DmoUnionConditionsTable.conditionValue,
        DmoUnionProgressTable.isComplete
    ).where(
        DmoUnionConditionsTable.unionId == item.id
    ).join(
        DmoUnionProgressTable, isouter=True
    ).join(
        DmoConditionTypeTable
    ).join(
        DmoRewardTypeTable
    ).all()

    digimonInfo = session.query(
        DmoUnionTable.unionId, DigimonTable.id, DmoDigimonTable.name, DmoDigimonTable.level, DmoDigimonTable.image,
        DmoDigimonTable.isOpen, DmoDigimonTable.isTranscend
    ).where(
        DmoUnionTable.unionId == item.id
    ).join(
        DmoDigimonTable, DmoDigimonTable.id == DmoUnionTable.digimonId
    ).all()

    return {
        "name": unionGroupName.name,
        "conditionInfo": conditionInfo,
        "digimonInfo": digimonInfo
    }


@router.post('/select/union/digimon', summary='DMO 유니온 디지몬 정보 조회')
async def select_union_digimon(item: IdParam):
    session.commit()

    selectDigimon = session.query(DmoDigimonTable).where(DmoDigimonTable.id == item.id).first()
    return session.query(DmoDigimonTable).where(DmoDigimonTable.groupId == selectDigimon.groupId).all()


@router.post('/update/union/digimon', summary='DMO 유니온 디지몬 정보 업데이트')
async def update_union_digimon(item: UnionDigimonUpdateParam):
    session.query()
    try:
        session.query(
            DmoDigimonTable
        ).filter(
            DmoDigimonTable.groupId == item.groupId
        ).update(
            {DmoDigimonTable.level: item.level, DmoDigimonTable.isTranscend: item.isTranscend}
        )

        for digimon in item.isOpenInfo:
            session.query(
                DmoDigimonTable
            ).filter(
                DmoDigimonTable.id == digimon.id
            ).update(
                {DmoDigimonTable.isOpen: digimon.isOpen}
            )

        session.commit()
    except Exception as e:
        session.rollback()
        return f"업데이트 실패: {e}"

    return "업데이트 성공"


@router.post('/update/union/favorite', summary="DMO 유니온 그룹 즐겨찾기 업데이트")
async def update_union_group_favorite(item: UnionGroupFavoriteUpdateParam):
    try:
        session.query(
            DmoUnionGroupTable
        ).filter(
            DmoUnionGroupTable.id == item.groupId
        ).update(
            {DmoUnionGroupTable.isFavorite: item.isFavorite}
        )
        session.commit()
    except Exception as e:
        return f"업데이트 실패: {e}"

    return "업데이트 성공"
