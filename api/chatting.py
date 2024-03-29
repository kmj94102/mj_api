from fastapi import APIRouter
from sqlalchemy.orm import aliased

from db import session
from model.chat import *
from model.ticket import *

router = APIRouter()


@router.post("/select/chattingList", summary="채팅 리스트 조회")
async def select_chatting_list(item: ChattingListParam) -> List[ChattingRoomInfo]:
    session.commit()

    input_date = datetime.strptime(item.date, "%Y.%m.%d")

    start_time = input_date.replace(hour=0, minute=0, second=0)
    end_time = input_date.replace(hour=23, minute=59, second=59)

    team1 = aliased(TeamTable)
    team2 = aliased(TeamTable)

    data = session.query(
        GameTable.gameId,
        GameTable.gameDate,
        team1.name.label("leftTeam"),
        team2.name.label("rightTeam")
    ).join(
        team1, team1.teamId == GameTable.leftTeamId
    ).join(
        team2, team2.teamId == GameTable.rightTeamId
    ).filter(
        GameTable.gameDate >= start_time, GameTable.gameDate <= end_time
    ).all()

    gameList = []
    for item in data:
        gameId, gameDate, leftTeam, rightTeam = item
        gameInfo = ChattingRoomInfo(gameId=gameId, gameTime=gameDate.strftime("%H:%M"), leftTeam=leftTeam,
                                    rightTeam=rightTeam)

        gameList.append(gameInfo)

    return gameList
