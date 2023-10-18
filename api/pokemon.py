from fastapi import APIRouter, HTTPException
from db import session
from model import PokemonTable, Pokemon, create_pokemon_table, \
    CharacteristicTable, Characteristic, create_characteristic_table, \
    UpdateIsCatch, UpdatePokemonImage, \
    EvolutionTable, Evolution, create_evolution_table, \
    EvolutionTypeTable, EvolutionType, create_evolution_type_table
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy import update, delete, text

router = APIRouter()


@router.post("/insert")
async def insert_pokemon(item: Pokemon):
    """
    포켓몬 등록
    - **index**: 인덱스
    - **number**: 포켓몬 번호
    - **name**: 이름
    - **status**: 스테이터스
    - **classification**: 분류
    - **characteristic**: 특성
    - **attribute**: 속성
    - **image**: 이미지
    - **shinyImage**: 이로치 이미지
    - **spotlight**: 스포트라이트
    - **shinySpotlight**: 이로치 스포트라이트
    - **description**: 설명
    - **generation**: 세대
    - **isCatch**: 잡은 여부
    """
    data = session.query(PokemonTable).filter(PokemonTable.name == item.name).first()
    if data is None:
        pokemon = create_pokemon_table(item)
        session.add(pokemon)
        session.commit()

    return f"{item.name} 추가 완료"


@router.get("/select")
async def read_pokemon_with_number(number: str):
    session.commit()

    return session.query(PokemonTable).filter(PokemonTable.number == number).first()


@router.get("/select/list")
async def read_pokemon_list(name: str = "", skip: int = 0, limit: int = 100):
    """
    포켓몬 리스트 조회
    - **name**: 포켓몬 이름
    - **skip**: 시작 인덱스 번호
    - **limit**: 한번 호출 시 불러올 개수
    """
    session.commit()

    pokemon_list = session.query(PokemonTable.index, PokemonTable.number, PokemonTable.name, PokemonTable.spotlight,
                                 PokemonTable.shinySpotlight, PokemonTable.isCatch) \
        .filter(PokemonTable.name.like(f"%{name}%")).offset(skip).limit(limit).all()
    total_size = session.query(PokemonTable).filter(PokemonTable.name.like(f"%{name}%")).count()
    return {
        "list": pokemon_list,
        "totalSize": total_size
    }


@router.get("/select/detail/{number}")
async def read_pokemon_detail(number: str):
    """
    포켓몬 상세 조회
    - **number**: 포켓몬 번호
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == number).first()
    beforeInfo = await read_pokemon_image(pokemon.index - 1)
    nextInfo = await read_pokemon_image(pokemon.index + 1)
    evolutionInfo = await read_pokemon_evolution(number)

    return {
        "pokemonInfo": pokemon,
        "beforeInfo": beforeInfo,
        "nextInfo": nextInfo,
        "evolutionInfo": evolutionInfo
    }


@router.get("/select/image/{index}")
async def read_pokemon_image(index: int):
    """
    포켓몬 이미지 조회
    - **index**: 포켓몬 인덱스
    """
    return session.query(PokemonTable.number, PokemonTable.image, PokemonTable.shinyImage).filter(
        PokemonTable.index == index).first()


@router.get("/select/evolution")
async def read_pokemon_evolution(number: str):
    """
    포켓몬 진화 조회
    - **number**: 포켓몬 번호
    """
    pokemon1 = aliased(PokemonTable)
    pokemon2 = aliased(PokemonTable)
    evolution = session.query(pokemon1.spotlight.label('beforeDot'), pokemon1.shinySpotlight.label('beforeShinyDot'),
                              pokemon2.spotlight.label('afterDot'), pokemon2.shinySpotlight.label('afterShinyDot'),
                              pokemon1.number.label('beforeNumber'), pokemon2.number.label('afterNumber'),
                              EvolutionTypeTable.image.label('evolutionImage'), EvolutionTable.evolutionCondition) \
        .filter(EvolutionTable.numbers.like(f"%{number}%"), EvolutionTable.beforeNum == pokemon1.number,
                EvolutionTable.afterNum == pokemon2.number,
                EvolutionTypeTable.name == EvolutionTable.evolutionType).all()

    return evolution


@router.post("/update/catch")
async def update_pokemon_is_catch(item: UpdateIsCatch):
    """
    포켓몬 잡은 상태 업데이트
    - **number**: 포켓몬 번호
    - **isCatch**: 잡은 상태
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == item.number).first()
    pokemon.isCatch = item.isCatch
    session.commit()
    return f"{item.number} 업데이트 완료"


@router.post("/insert/char")
async def create_characteristic(item: Characteristic):
    """
    특성 등록
    - **index**: 인덱스
    - **name**: 이름
    - **description**: 설명
    """
    char = session.query(CharacteristicTable).filter(CharacteristicTable.name == item.name).first()
    if char is None:
        charTable = create_characteristic_table(item)

        session.add(charTable)
        session.commit()
        result = f"{item.name} 추가완료"
    else:
        result = f"{item.name} 이미 추가된 특성입니다."
    return result


@router.get("/select/briefList/{search}")
async def read_brief_pokemon_list(search: str):
    """
    포켓몬 간략한 정보 리스트 조회 (진화 추가 용도)
    - **search**: 검색어, 숫자 형태일 경우 해당 번호의 정보 조회, 문자형일 경우 검색어에 해당하는 포켓몬 조회
    """
    if search.isdigit():
        sql = f"""
            SELECT *
            FROM pokemon
            WHERE pokemon.index >= (
                SELECT pokemon.index
                FROM pokemon
                WHERE pokemon.number = {search}
                LIMIT 1
            )
            LIMIT 10;
        """
        result = session.execute(text(sql)).fetchall()
    else:
        result = session.query(PokemonTable.spotlight, PokemonTable.number).filter(
            PokemonTable.name.like(f"%{search}%")).all()

    return result


@router.post("/insert/evolution")
async def insert_pokemon_evolutions(list: List[Evolution]):
    """
    포켓몬 진화 추가
    - **numbers**: 진화에 포함된 번호들
    - **beforeNum**: 진화 전 번호
    - **afterNum**: 진화 후 번호
    - **evolutionType**: 진화 타입
    - **evolutionCondition**: 진화 조건
    """
    try:
        session.rollback()
        session.begin()
        for item in list:
            history = session.query(EvolutionTable).filter(EvolutionTable.beforeNum == item.beforeNum,
                                                           EvolutionTable.afterNum == item.afterNum).first()

            if history is None:
                evolution = create_evolution_table(item)

                session.add(evolution)
                session.commit()
            else:
                raise ValueError(f"중복 데이터 {item.beforeNum}-{item.afterNum}")
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()
    return "데이터 추가를 완료하였습니다."


@router.post("/insert/evolutionType")
async def insert_pokemon_evolution_types(list: List[EvolutionType]):
    """
    포켓몬 진화 타입 추가
    - **name**: 타입 이름
    - **image**: 타입 이미지
    """
    try:
        session.rollback()
        session.begin()
        for item in list:
            evolution_type = create_evolution_type_table(item)

            session.add(evolution_type)
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"오류가 발생하였습니다. {e}")
    finally:
        session.close()
    return "데이터 추가를 완료하였습니다."


@router.post("/select/beforeImageInfo")
async def read_pokemon_before_imgae_info():
    session.commit()
    return session.query(PokemonTable.number, PokemonTable.spotlight).all()


@router.post("/update/image")
async def update_pokemon_image(item: UpdatePokemonImage):
    """
    포켓몬 이미지 업데이트
    - **number**: 포켓몬 번호
    - **image**: 이미지
    """
    pokemon = session.query(PokemonTable).filter(PokemonTable.number == item.number).first()
    pokemon.spotlight = item.spotlight
    session.commit()

    return f"{item.number} 업데이트 완료"
