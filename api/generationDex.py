from fastapi import APIRouter
from db import session
from model.generation import *

router = APIRouter()


@router.get("/select/generation")
async def read_generation():
    """
    포켓몬 도감 종류 조회
    """
    session.commit()
    quest = session.query(GenerationTable).all()

    return quest


@router.get("/insert/dex")
async def insert_dex(pokemonIdx: int, generationIdx: int, name: str):
    result = session.query(GenerationDexTable).where(GenerationDexTable.pokemonIdx == pokemonIdx,
                                                     generationIdx == GenerationDexTable.generationIdx).first()

    if result is None:
        dex = createDexTable(GenerationDex(pokemonIdx=pokemonIdx, generationIdx=generationIdx, isCatch=False))
        session.add(dex)
        session.commit()
        return f"{name} 등록 완료"
    else:
        return f"{name} 중복 등록"
