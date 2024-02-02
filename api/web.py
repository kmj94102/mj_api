from fastapi import APIRouter
from db import session
from model.webModel import WebTable

router = APIRouter()


@router.post("/select")
async def select_web():
    session.commit()
    data = session.query(WebTable).all()
    return data
