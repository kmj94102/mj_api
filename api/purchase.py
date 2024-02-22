from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from db import session
from sqlalchemy.orm import aliased
from model.userModel import *
from model.ticket import *

router = APIRouter()


def raise_http_exception(detail: str = "Error", status_code: int = 400):
    raise HTTPException(status_code=status_code, detail=detail)


@router.post("/select/teamList")
async def select_team_list():
    session.commit()

    teams = session.query(TeamTable).all()
    return teams


@router.post("/insert/game")
async def insert_game(item: Game):
    session.commit()
    data = session.query(GameTable).filter(GameTable.gameDate == item.gameDate).first()

    if data:
        raise_http_exception("해당 시간에 게임이 이미 등록되어 있습니다.")

    game = create_game(item=item)
    session.add(game)
    session.commit()


@router.post("/select/game")
async def select_game():
    session.commit()

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
    ).all()

    formatted_data = []
    for item in data:
        game_id, game_date, left_team, right_team = item
        formatted_item = {
            "gameId": game_id,
            "gameDate": game_date.strftime("%Y.%m.%d %H:%M"),
            "leftTeam": left_team,
            "rightTeam": right_team
        }
        formatted_data.append(formatted_item)

    return formatted_data


@router.post("/select/reservationInfo")
async def select_ticket_info(item: TicketInfoParam):
    session.commit()

    seatData = session.query(SeatTable.seatNumber).filter(SeatTable.gameId == item.gameId).all()
    seat_numbers = [item["seatNumber"] for item in seatData]

    team1 = aliased(TeamTable)
    team2 = aliased(TeamTable)

    gameId, gameDate, leftTeam, rightTeam = session.query(
        GameTable.gameId,
        GameTable.gameDate,
        team1.name.label("leftTeam"),
        team2.name.label("rightTeam"),
    ).join(
        team1, team1.teamId == GameTable.leftTeamId
    ).join(
        team2, team2.teamId == GameTable.rightTeamId
    ).where(
        GameTable.gameId == item.gameId
    ).first()

    userData = session.query(LolketingUserTable.cash).filter(LolketingUserTable.user_id == item.userId).first()

    return {
        "userId": item.userId,
        "gameId": item.gameId,
        "date": gameDate.strftime("%Y.%m.%d %H:%M"),
        "gameTitle": f"{leftTeam} VS {rightTeam}",
        "cash": userData.cash,
        "reservedSeats": seat_numbers
    }


@router.post("/insert/reservationTicket")
async def insert_reservation_ticket(item: ReservationTicketItem):
    session.commit()

    game = session.query(GameTable).filter(GameTable.gameId == item.gameId).first()
    user = session.query(UserTable).filter(UserTable.index == item.userId).first()
    idList = []

    if not game:
        raise_http_exception("게임 정보가 없습니다.")
    elif not user:
        raise_http_exception("유저 정보가 없습니다.")
    elif not item.seatNumber:
        raise_http_exception("좌석을 선택해 주세요.")
    elif len(item.seatNumber.split(',')) != item.count:
        raise_http_exception("인원수에 맞게 좌석을 선택해주세요.")

    try:
        session.rollback()
        session.begin()
        date = datetime.now()
        for number in item.seatNumber.split(','):
            beforeSeatInfo = session.query(SeatTable) \
                .filter(SeatTable.gameId == item.gameId, SeatTable.seatNumber == number).first()
            if beforeSeatInfo:
                raise CustomException(500, "이미 예약된 좌석입니다.")
            # 좌석 업데이트
            seat = create_seat(gameId=item.gameId, seatNumber=number)
            session.add(seat)
            session.flush()
            # 예약 정보 추가
            reservation = createReservation(gameId=game.gameId, seatId=seat.seatId, userId=item.userId, date=date)
            session.add(reservation)
            session.flush()
            idList.append(reservation.reservationId)
        # 캐시 차감 및 룰렛 횟수 증가
        userData = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == item.userId).first()
        userData.cash -= 11_000 * item.count
        userData.roulette += item.count

        session.commit()
    except CustomException as e:
        session.rollback()
        raise_http_exception(e.message, e.code)
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("티켓 예매 중 오류가 발생하였습니다.")

    return idList


@router.post("/select/ticketInfo")
def select_ticket_info(item: TicketIdList):
    session.commit()

    if not item.idList:
        raise_http_exception("티켓 정보가 없습니다.")

    reservation = session.query(ReservationTable).filter(ReservationTable.reservationId.in_(item.idList)).all()

    if not reservation:
        raise_http_exception("예매 정보가 없습니다.")

    team1 = aliased(TeamTable)
    team2 = aliased(TeamTable)

    game = session.query(
        GameTable.gameDate,
        team1.name.label("leftTeam"),
        team2.name.label("rightTeam")
    ).join(
        team1, team1.teamId == GameTable.leftTeamId
    ).join(
        team2, team2.teamId == GameTable.rightTeamId
    ).filter(
        GameTable.gameId == reservation[0].gameId
    ).first()

    seatIds = [item.seatId for item in reservation]

    seat = session.query(SeatTable).filter(SeatTable.seatId.in_(seatIds)).all()
    seatIds = ", ".join([item.seatNumber for item in seat])

    return {
        "leftTeam": game["leftTeam"],
        "rightTeam": game["rightTeam"],
        "time": game["gameDate"].strftime("%Y.%m.%d %H:%M"),
        "seats": seatIds
    }


@router.post("/select/history")
async def select_purchase_history(item: IdParam):
    session.commit()

    team1 = aliased(TeamTable)
    team2 = aliased(TeamTable)
    data = session.query(
        func.group_concat(ReservationTable.reservationId).label('reservationIds'),
        GameTable.gameDate,
        team1.name.label("leftTeam"),
        team2.name.label("rightTeam")
    ).filter(
        ReservationTable.userId == item.id
    ).group_by(
        ReservationTable.reservationDate
    ).join(
        GameTable, GameTable.gameId == ReservationTable.gameId
    ).join(
        team1, team1.teamId == GameTable.leftTeamId
    ).join(
        team2, team2.teamId == GameTable.rightTeamId
    ).all()

    formatted_data = []
    for item in data:
        reservationIds, gameDate, leftTeam, rightTeam = item
        formatted_item = {
            "reservationIds": reservationIds,
            "date": gameDate.strftime("%Y.%m.%d"),
            "time": gameDate.strftime("%H:%M"),
            "leftTeam": leftTeam,
            "rightTeam": rightTeam
        }
        formatted_data.append(formatted_item)

    return formatted_data

