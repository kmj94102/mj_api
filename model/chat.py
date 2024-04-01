from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChattingListParam(BaseModel):
    date: str


class ChattingRoomInfo(BaseModel):
    gameId: int
    gameDate: str
    gameTime: str
    leftTeam: str
    rightTeam: str
