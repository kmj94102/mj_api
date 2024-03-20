from fastapi import APIRouter
from sqlalchemy import func
from db import session
from sqlalchemy.orm import aliased
from model.userModel import *
from model.ticket import *
from model.goods import *
from model.common import *
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/select/teamList", summary="팀 리스트 조회")
async def select_team_list() -> List[Team]:
    session.commit()

    teams = session.query(TeamTable.teamId, TeamTable.name, TeamTable.image).all()
    team_list = []
    for team_tuple in teams:
        team = Team(teamId=team_tuple.teamId, name=team_tuple.name, image=team_tuple.image)
        team_list.append(team)
    return team_list


@router.post("/insert/game", summary="경기 추가")
async def insert_game(item: Game) -> str:
    """
    - **gameDate**: 경기 시간
    - **leftTeamId**: 왼쪽 팀 Id
    - **rightTeamId**: 오른쪽 팀 Id
    """
    session.commit()
    data = session.query(GameTable).filter(GameTable.gameDate == item.gameDate).first()

    if data:
        raise_http_exception("해당 시간에 경기가 이미 등록되어 있습니다.")

    game = create_game(item=item)
    session.add(game)
    session.commit()
    return f"{item.gameDate} 등록 완료"


@router.post("/select/game", summary="경기 조회")
async def select_game() -> List[TicketInfo]:
    session.commit()

    today = datetime.now().date()
    five_days_later = today + timedelta(days=5)

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
        GameTable.gameDate >= today, GameTable.gameDate <= five_days_later
    ).all()

    ticketList = []
    for item in data:
        gameId, gameDate, leftTeam, rightTeam = item
        count = session.query(func.count(SeatTable.seatId)).filter(SeatTable.gameId == gameId).scalar()
        ticketInfo = TicketInfo(gameId=gameId, gameDate=gameDate.strftime("%Y.%m.%d %H:%M"), leftTeam=leftTeam,
                                rightTeam=rightTeam, isSoldOut=count == 64)

        ticketList.append(ticketInfo)

    return ticketList


@router.post("/select/reservationInfo", summary="예매 정보 조회")
async def select_ticket_info(item: TicketInfoParam) -> ReservationInfo:
    """
    - **gameId**: 경기 아이디
    - **userId**: 유저 인덱스
    """
    session.commit()

    seatData = session.query(SeatTable.seatNumber).filter(SeatTable.gameId == item.gameId)\
        .order_by(SeatTable.seatNumber).all()
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

    return ReservationInfo(userId=item.userId, gameId=item.gameId, date=gameDate.strftime("%Y.%m.%d %H:%M"),
                           gameTitle=f"{leftTeam} VS {rightTeam}", cash=userData.cash, reservedSeats=seat_numbers)


@router.post("/insert/reservationTicket", summary="티켓 예매")
async def insert_reservation_ticket(item: ReservationTicketItem) -> List[int]:
    """
    - **gameId**: 경기 아이디
    - **userId**: 유저 인덱스
    - **count**: 좌석 갯수
    - **seatNumber**: 좌석 번호 ex) A1,A2
    """
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


@router.post("/select/ticketInfo", summary="티켓 정보 조회")
def select_ticket_info(item: TicketIdList) -> ReservationTicketInfo:
    """
    - **idList**: ReservationId
    """
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

    return ReservationTicketInfo(leftTeam=game["leftTeam"], rightTeam=game["rightTeam"],
                                 time=game["gameDate"].strftime("%Y.%m.%d %H:%M"), seats=seatIds)


@router.post("/select/ticketHistory", summary="티켓 구매 내역 조회")
async def select_purchase_history(item: UserIdParam) -> List[TicketHistoryInfo]:
    """
    - **id**: 유저 인덱스
    """
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

    infoList = []
    for item in data:
        reservationIds, seatIds, gameDate, leftTeam, rightTeam = item

        seatData = session.query(SeatTable.seatNumber).filter(SeatTable.seatId.in_(seatIds.split(",")))
        seatNumbers = ', '.join(name for name, in seatData)
        infoList.append(
            TicketHistoryInfo(
                reservationIds=reservationIds,
                seatNumbers=seatNumbers,
                date=gameDate.strftime("%Y.%m.%d"),
                time=gameDate.strftime("%H:%M"),
                leftTeam=leftTeam,
                rightTeam=rightTeam
            )
        )

    return infoList


@router.post("/insert/goods", summary="쇼핑 아이템 추가")
def insert_goods_item(item: GoodsInsertParam) -> str:
    """
    - **category**: 카테고리
    - **name**: 이름
    - **price**: 가격
    - **urlList**: 이미지 Url 리스트
    """
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

    return f"{item.name} 추가 완료"


@router.post("/select/goodsItems", summary="쇼핑 아이템 조회")
def select_goods_items() -> List[ShopItem]:
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


@router.post("/select/goodsItemDetail", summary="쇼핑 아이템 상세 조회")
def select_goods_item_detail(item: DetailParam) -> ShopDetail:
    """
    - **id**: 상품 아이디
    """
    session.commit()

    imageList = session.query(GoodsImageTable.url).filter(GoodsImageTable.goodsId == item.id).all()
    goods = session.query(GoodsTable).filter(GoodsTable.goodsId == item.id).first()

    return ShopDetail(
        goodsId=goods.goodsId,
        category=goods.category,
        name=goods.name,
        price=goods.price,
        imageList=[image["url"] for image in imageList]
    )


@router.post("/select/purchaseInfo", summary="결제에 필요한 유저 정보 조회")
def select_purchase_info(item: UserIdParam) -> PurchaseInfo:
    """
    - **id**: 유저 인덱스
    """
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


@router.post("/insert/items", summary="쇼핑 구매 내역 추가")
def insert_purchase(items: List[Purchase]) -> str:
    """
    - **userId**: 유저 인덱스
    - **goodsId**: 상품 아이디
    - **amount**: 상품 갯수
    - **productsPrice**: 상품 가격
    """
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


@router.post("/select/GoodsHistory", summary="쇼핑 구매 내역")
def select_purchase_history(item: UserIdParam) -> List[ShopPurchaseHistory]:
    """
    - **id**: 유저 인덱스
    """
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

    historyList = []
    for item in data:
        amount, datetime_, category, name, price, url = item
        historyList.append(
            ShopPurchaseHistory(
                amount=amount,
                category=category,
                name=name,
                price=price,
                image=url,
                date=datetime_.strftime("%Y.%m.%d")
            )
        )

    return historyList
