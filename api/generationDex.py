from fastapi import APIRouter
from db import session
from model.generation import *
from model.model import PokemonTable

router = APIRouter()


@router.get("/select/generation")
async def read_generation():
    """
    포켓몬 타이틀 도감 종류 조회
    """
    session.commit()
    quest = session.query(GenerationTable).all()

    return quest


@router.get("/insert")
async def insert_dex(pokemonIdx: int, generationIdx: int, name: str):
    """
    포켓몬 타이틀 도감에 포켓몬 등록
    :param pokemonIdx: 포켓몬 인덱스
    :param generationIdx: 타이틀 도감 인덱스
    :param name: 이름
    """
    result = session.query(GenerationDexTable).where(GenerationDexTable.pokemonIdx == pokemonIdx,
                                                     generationIdx == GenerationDexTable.generationIdx).first()

    if result is None:
        dex = createDexTable(GenerationDex(pokemonIdx=pokemonIdx, generationIdx=generationIdx, isCatch=False))
        session.add(dex)
        session.commit()
        return f"{name} 등록 완료"
    else:
        return f"{name} 중복 등록"


async def read_dex_count(item: Generation):
    totalCount = session.query(GenerationDexTable).where(GenerationDexTable.generationIdx == item.code).count()
    isCatchCount = session.query(GenerationDexTable).where(GenerationDexTable.generationIdx == item.code, GenerationDexTable.isCatch == 1).count()

    return totalCount, isCatchCount


@router.get("/select/count")
async def read_all_dex_count():
    """
    포케못 타이틀 도감 별 카운트
    """
    data = session.query(GenerationTable).all()

    _list = []
    for item in data:
        (totalCount, isCatchCount) = await read_dex_count(item)
        _list.append(
            {
                "totalCount": totalCount,
                "isCatchCount": isCatchCount,
                "generationIdx": item.code,
                "name": item.name
            }
        )

    return _list


@router.get("/select/list")
async def read_generation_list(generationIdx: int):
    """
    선택한 타이틀 도감 포켓몬 리스트
    :param generationIdx: 타이틀 도감 인덱스
    """
    session.commit()

    result = session\
        .query(PokemonTable.name, PokemonTable.number, GenerationDexTable.idx, GenerationDexTable.generationIdx, GenerationDexTable.isCatch, PokemonTable.spotlight)\
        .filter(GenerationDexTable.generationIdx == generationIdx)\
        .join(PokemonTable, GenerationDexTable.pokemonIdx == PokemonTable.index)\
        .all()
    return result


@router.post("/update/isCatch")
async def update_is_catch(param: IdxParam):
    """
    잡은 상태 업데이트
    :param param: 타이틀 도감 인덱스
    :return:
    """
    item = session.query(GenerationDexTable).filter(GenerationDexTable.idx == param.idx).first()
    item.isCatch = not item.isCatch
    session.commit()
    return item.isCatch
