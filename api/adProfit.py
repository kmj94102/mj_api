from fastapi import APIRouter
from db import session
from model.adProfitModel import *

router = APIRouter()


@router.post("/insert/tokenInfo", summary="게시글 등록")
async def insert_board(item: AdProfit) -> str:
    print(f"\n\n\n+++++ {item}\n\n\n")
    adProfit = item.toTable()
    session.add(adProfit)
    session.commit()

    return "등록 완료"
