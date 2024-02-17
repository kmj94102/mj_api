from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from db import session
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


@router.post("/insert/ticket")
async def insert_ticket(item: Game):
    session.commit()

    game = create_game(item=item)
    session.add(game)
    session.commit()


@router.post("/select/ticket")
async def select_ticket():
    session.commit()

    data = session.query(GameTable).all()

    return data


@router.post("/insert/reservationTicket")
async def insert_reservation_ticket(item: ReservationTicketItem):
    session.commit()

    game = session.query(GameTable).filter(GameTable.gameId == item.gameId).first()
    user = session.query(UserTable).filter(UserTable.index == item.userId).first()

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
        for number in item.seatNumber.split(','):
            beforeSeatInfo = session.query(SeatTable)\
                .filter(SeatTable.gameId == item.gameId, SeatTable.seatNumber == number).first()
            if beforeSeatInfo:
                raise CustomException(500, "이미 예약된 좌석입니다.")

            seat = create_seat(gameId=item.gameId, seatNumber=number)
            session.add(seat)
            session.flush()

            reservation = createReservation(gameId=game.gameId, seatId=seat.seatId, userId=item.userId)
            session.add(reservation)
            session.commit()
    except CustomException as e:
        session.rollback()
        raise_http_exception(e.message, e.code)
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("티켓 예매 중 오류가 발생하였습니다.")
