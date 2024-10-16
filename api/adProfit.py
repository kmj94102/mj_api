from fastapi import APIRouter
from db import session
from model.adProfitModel import *

router = APIRouter()


@router.get("/insert/tokenInfo", summary="게시글 등록")
async def insert_board(email: str, refreshToken: str, accessToken: str, device: str) -> str:
    print(f"\n\n\n+++++ email: {email}\n refreshToken: {refreshToken}\n"
          f"accessToken: {accessToken}\n device: {device}\n \n\n\n")
    adProfit = AdProfit(email=email, refreshToken=refreshToken, accessToken=accessToken, device=device).toTable()
    session.add(adProfit)
    session.commit()

    return "등록 완료"
