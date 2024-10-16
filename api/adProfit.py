from fastapi import APIRouter
from db import session
from model.adProfitModel import *

router = APIRouter()


@router.get("/insert/tokenInfo", summary="게시글 등록")
async def insert_board(email: str, refreshToken: str, accessToken: str, device: str) -> str:
    adProfit = AdProfit(email=email, refreshToken=refreshToken, accessToken=accessToken, device=device).toTable()
    session.add(adProfit)
    session.commit()

    return "등록 완료"
