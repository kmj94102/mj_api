from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from db import session
from sqlalchemy.orm import aliased
from model.userModel import *
from model.ticket import *
from model.goods import *

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


@router.post("/select/ticketHistory")
async def select_purchase_history(item: IdParam):
    session.commit()

    team1 = aliased(TeamTable)
    team2 = aliased(TeamTable)
    data = session.query(
        func.group_concat(ReservationTable.reservationId).label('reservationIds'),
        func.group_concat(ReservationTable.seatId).label('seatIds'),
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
        reservationIds, seatIds, gameDate, leftTeam, rightTeam = item

        seatData = session.query(SeatTable.seatNumber).filter(SeatTable.seatId.in_(seatIds.split(",")))
        seatNumbers = ', '.join(name for name, in seatData)

        formatted_item = {
            "reservationIds": reservationIds,
            "seatNumbers": seatNumbers,
            "date": gameDate.strftime("%Y.%m.%d"),
            "time": gameDate.strftime("%H:%M"),
            "leftTeam": leftTeam,
            "rightTeam": rightTeam
        }
        formatted_data.append(formatted_item)

    return formatted_data


@router.post("/insert/goods")
def insert_goods_item(item: GoodsInsertParam):
    session.commit()

    try:
        session.rollback()
        session.begin()
        goods = create_goods_table(item=item)
        session.add(goods)
        session.flush()

        for url in item.urlList:
            goodsImage = create_goods_image_table(url=url, goodsId=goods.goodsId)
            session.add(goodsImage)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("굿즈 상품 추가 중 오류가 발생하였습니다.")


@router.post("/select/goodsItems")
def select_goods_items():
    session.commit()

    sub = session.query(
        GoodsImageTable.goodsId,
        func.min(GoodsImageTable.url).label("url")
    ).group_by(GoodsImageTable.goodsId).subquery()

    data = session.query(
        GoodsTable.goodsId,
        GoodsTable.category,
        GoodsTable.name,
        GoodsTable.price,
        sub.c.url
    ).join(
        sub, sub.c.goodsId == GoodsTable.goodsId
    ).all()

    return data


@router.post("/select/goodsItemDetail")
def select_goods_item_detail(item: DetailParam):
    session.commit()

    imageList = session.query(GoodsImageTable.url).filter(GoodsImageTable.goodsId == item.id).all()
    goods = session.query(GoodsTable).filter(GoodsTable.goodsId == item.id).first()

    return {
        "goodsId": goods.goodsId,
        "category": goods.category,
        "name": goods.name,
        "price": goods.price,
        "imageList": [image["url"] for image in imageList]
    }


@router.post("/select/purchaseInfo")
def select_purchase_info(item: UserIdParam):
    session.commit()

    data = session.query(
        UserTable.nickname,
        UserTable.mobile,
        UserTable.address,
        LolketingUserTable.cash
    ).filter(
        UserTable.index == item.id
    ).join(
        LolketingUserTable, LolketingUserTable.user_id == item.id
    ).first()

    return data


@router.post("/insert/items")
def insert_purchase(items: List[Purchase]):
    try:
        session.rollback()
        session.begin()
        time = datetime.now()
        totalPrice = 0
        for item in items:
            data = create_purchase_table(item=item, time=time)
            if data.amount <= 0:
                raise CustomException(400, "상품의 수량을 확인해 주세요.")
            session.add(data)
            totalPrice += item.productsPrice

        lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == items[0].userId).first()
        lolketingUser.cash -= totalPrice
        session.add(lolketingUser)

        session.commit()
    except CustomException as e:
        session.rollback()
        raise_http_exception(e.message, e.code)
    except Exception as e:
        session.rollback()
        print(e)
        raise_http_exception("상품 구매 중 오류가 발생하였습니다.")

    return "구입 성공"


@router.post("/select/GoodsHistory")
def select_purchase_history(item: UserIdParam):
    session.commit()

    sub = session.query(
        GoodsImageTable.goodsId,
        func.min(GoodsImageTable.url).label("url")
    ).group_by(GoodsImageTable.goodsId).subquery()

    data = session.query(
        PurchaseTable.amount,
        PurchaseTable.datetime,
        GoodsTable.category,
        GoodsTable.name,
        (PurchaseTable.amount * GoodsTable.price).label("price"),
        sub.c.url
    ).filter(
        PurchaseTable.userId == item.id
    ).join(
        GoodsTable, GoodsTable.goodsId == PurchaseTable.goodsId
    ).join(
        sub, sub.c.goodsId == GoodsTable.goodsId
    ).all()

    formatted_data = []
    for item in data:
        amount, datetime_, category, name, price, url = item
        formatted_item = {
            "amount": amount,
            "category": category,
            "name": name,
            "price": price,
            "image": url,
            "date": datetime_.strftime("%Y.%m.%d"),
        }
        formatted_data.append(formatted_item)

    return formatted_data
