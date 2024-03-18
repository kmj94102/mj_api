from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from db import session
from model.userModel import *
from model.couponModel import *
from model.common import *
import re

router = APIRouter()


def check_duplicate_id(id_: str):
    data = session.query(UserTable).filter(UserTable.id == id_).first()
    return data


def check_duplicate_nickname(nickname: str):
    data = session.query(UserTable).filter(UserTable.nickname == nickname).first()
    return data


def check_email(email):
    # 이메일 주소를 검사하는 정규 표현식
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 이메일 주소 패턴과 매치되는지 확인
    if re.match(pattern, email):
        return True
    else:
        return False


def check_password(password):
    # 비밀번호를 검사하는 정규 표현식
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()])([A-Za-z\d!@#$%^&*()]{4,})$'

    # 비밀번호 패턴과 매치되는지 확인
    if re.match(pattern, password):
        return True
    else:
        return False


@router.post("/join/email", summary="회원가입")
async def join_email(item: User) -> int:
    """
    - **type**: 로그인 타입 (필수)
    - **id**: 유저 이메일 (필수)
    - **password**: 비밀번호 (이메일 회원가입 시 필수)
    - **nickname**: 닉네임 (필수)
    - **gender**: 성별
    - **birthday** 생일
    - **birthdayYear** 태어난 년도
    - **mobile**: 핸드폰 번호
    - **address**: 주소
    """
    session.commit()

    if not check_email(item.id):
        raise_http_exception("이메일 형식에 맞지 않는 아이디입니다.")

    data = check_duplicate_id(item.id)
    if data:
        messages = {
            "email": "이미 가입된 아이디입니다.",
            "kakao": "카카오 아이디로 가입된 아이디입니다.",
            "naver": "네이버 아이디로 가입된 아이디입니다."
        }
        detail = messages.get(data.type, "이미 가입된 아이디입니다.")
        raise_http_exception(detail)

    if item.type == 'email':
        if not item.password:
            raise_http_exception("비밀번호가 비어 있습니다.")
        elif not check_password(item.password):
            raise_http_exception("비밀번호가 조건을 만족하지 않습니다.")

    if not item.nickname:
        raise_http_exception("닉네임을 입력해 주세요.")
    elif check_duplicate_nickname(item.nickname):
        raise_http_exception("중복된 닉네임입니다.")

    userId = 0
    try:
        session.rollback()
        session.begin()

        user = create_user_table(item)
        session.add(user)
        session.flush()

        lolketing_user = create_lolketing_user_table(user)
        session.add(lolketing_user)

        session.commit()
        userId = user.index
    except SQLAlchemyError as e:
        session.rollback()
        raise_http_exception(f"오류가 발생하였습니다. {e}")
    finally:
        session.close()

    return userId


@router.post("/login/email", summary="이메일 로그인")
async def email_login(item: LoginInfo) -> LoginResponse:
    """
    - **id**: 유저 이메일
    - **password**: 비밀번호
    """
    session.commit()

    data = check_duplicate_id(item.id)
    if data is None:
        raise_http_exception("아이디 또는 비밀번호를 확인해 주세요.")
    elif data.type != "email":
        raise_http_exception("카카오 또는 네이버 아이디로 가입된 계정입니다.")
    elif data.password != item.password:
        raise_http_exception("아이디 또는 비밀번호를 확인해 주세요.")
    else:
        return LoginResponse(id=data.index, email=data.id, nickname=data.nickname)


@router.post("/login/social", summary="소셜 로그인")
async def social_login(item: SocialLoginInfo) -> LoginResponse:
    """
    - **id**: 유저 이메일
    - **type**: 로그인 타입
    """
    session.commit()

    data = check_duplicate_id(item.id)
    if data is None:
        raise_http_exception("회원 가입 필요", 501)
    elif data.type == 'email':
        raise_http_exception("이메일로 가입된 아이디입니다.")
    elif data.type != item.type:
        raise_http_exception("다른 로그인 방식으로 가입된 아이디입니다.")
    else:
        return LoginResponse(id=data.index, email=data.id, nickname=data.nickname)


@router.post("/withdrawal", summary="회원 탈퇴")
async def withdrawal(item: IdParam) -> TypeResponse:
    """
    - **id**: 유저 이메일
    """
    session.commit()
    data = session.query(UserTable).filter(UserTable.id == item.id).first()
    if data is None:
        raise_http_exception("회원 정보가 없습니다.")

    session.execute(delete(UserTable).where(UserTable.id == item.id))
    session.commit()
    return TypeResponse(type=data.type)


@router.post("/select/myInfo", summary="내 정보 조회")
async def select_my_info(item: UserIdParam) -> MyInfoResponse:
    """
    - **id**: 유저 인덱스
    """
    session.commit()
    user_info_query = session.query(
        UserTable.index,
        UserTable.nickname,
        UserTable.id,
        UserTable.mobile,
        UserTable.address,
        LolketingUserTable.id.label("lolketingId"),
        LolketingUserTable.grade,
        LolketingUserTable.point,
        LolketingUserTable.cash,
        func.coalesce(func.count(CouponTable.id), 0).label("totalCoupons"),
        func.coalesce(func.sum(func.cast(~CouponTable.isUsed, Integer)), 0).label("availableCoupons")
    ).join(
        LolketingUserTable, UserTable.index == LolketingUserTable.user_id
    ).outerjoin(
        CouponTable, UserTable.index == CouponTable.user_id
    ).filter(
        UserTable.index == item.id,
    ).group_by(
        UserTable.nickname,
        UserTable.id,
        UserTable.mobile,
        UserTable.address,
        LolketingUserTable.grade,
        LolketingUserTable.point,
        LolketingUserTable.cash
    ).first()

    # user_info_query를 딕셔너리로 변환
    user_info_dict = dict(user_info_query)
    couponList = session.query(CouponTable).filter(CouponTable.user_id == user_info_dict['index']).all()

    return convert_to_my_info_response(user_info_dict=user_info_dict, coupon_list=couponList)


# 현재 미사용
@router.post("/select/cash", summary="내 캐시 조회")
async def select_cash(item: IdParam) -> int:
    session.commit()

    user = session.query(UserTable).filter(UserTable.id == item.id).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")
    cash = session.query(LolketingUserTable.cash).filter(LolketingUserTable.user_id == user.index).first()
    if not cash:
        raise_http_exception("유저 정보가 없습니다.")
    return cash


@router.post("/update/charging", summary="캐시 충전")
async def cash_charging(item: CashChargingItem) -> MyInfoResponse:
    """
    - **id**: 유저 인덱스
    - **cash**: 충전할 금액
    """
    session.commit()

    user = session.query(UserTable).filter(UserTable.index == item.id).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")

    lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == user.index).first()
    if not lolketingUser:
        raise_http_exception("유저 정보가 없습니다.")

    chargedCash, remainder = calculate_charging(lolketingUser.cash, item.cash)
    lolketingUser.cash = chargedCash

    totalPoint = lolketingUser.point + (remainder / 10)
    if totalPoint <= 999_999:
        lolketingUser.point = totalPoint
    else:
        lolketingUser.point = 999_999

    if lolketingUser.grade != 'USER005':
        lolketingUser.grade = getUserGrade(totalPoint)

    return await select_my_info(item=UserIdParam(id=item.id))


def calculate_charging(cash, chargingCash):
    totalCash = cash + chargingCash
    if totalCash <= 100_000_000:
        chargedCash = totalCash
        remainder = chargingCash
    else:
        chargedCash = 100_000_000
        remainder = totalCash - 100_000_000

    return chargedCash, remainder


def getUserGrade(point):
    if point < 3_000:
        return 'USER001'
    elif point < 30_000:
        return 'USER002'
    elif point < 300_000:
        return 'USER003'
    else:
        return 'USER004'


async def select_coupon_list(user_id):
    session.commit()

    user = session.query(UserTable).filter(UserTable.id == user_id).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")

    couponList = session.query(CouponTable).filter(CouponTable.user_id == user.index).all()
    return couponList


# 수정 필요
@router.post("/select/newUserCoupon", summary="신규 유저 쿠폰 발급 여부 조회")
async def select_new_user_coupon(item: IdParam) -> bool:
    """
    - **id**: 유저 이메일
    """
    session.commit()

    user = session.query(UserTable).filter(UserTable.id == item.id).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")

    data = session.query(CouponTable) \
        .filter(CouponTable.user_id == user.index, CouponTable.name == "COUPON001").first()

    return bool(data)


@router.post("/insert/newUserCoupon", summary="신규 유저 쿠폰 발급")
async def insert_new_user_coupon(item: UserIdParam):
    """
    - **id**: 유저 인덱스
    """
    session.commit()

    data = session.query(CouponTable) \
        .filter(CouponTable.user_id == item.id, CouponTable.name == "COUPON001").first()

    if data:
        raise_http_exception("신규 가입 쿠폰을 이미 발급받으셨습니다.")

    coupon = create_new_user_coupon(item.id)
    session.add(coupon)
    session.commit()


@router.post("/insert/rouletteCoupon", summary="룰렛 쿠폰 발급")
async def insert_roulette_coupon(item: RouletteCoupon) -> RouletteCount:
    """
    - **id**: 유저 인덱스
    - **rp**: 당첨된 RP
    """
    session.commit()

    lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == item.id).first()
    if lolketingUser.roulette <= 0:
        raise_http_exception("룰렛 횟수를 모두 소진하였습니다.")

    coupon = create_roulette_coupon(item)
    session.add(coupon)
    lolketingUser.roulette = lolketingUser.roulette - 1
    session.commit()

    return RouletteCount(count=lolketingUser.roulette)


@router.post("/update/usingCoupon", summary="쿠폰 사용 업데이트")
async def using_coupon(item: CouponUseItem) -> MyInfoResponse:
    """
    - **id**: 유저 이메일
    - **couponId**: 쿠폰 아이디
    """
    session.commit()

    coupon = session.query(CouponTable).filter(CouponTable.id == item.couponId).first()
    if not coupon:
        raise_http_exception("쿠폰 정보가 없습니다.")
    if coupon.isUsed:
        raise_http_exception("이미 사용한 쿠폰입니다.")

    coupon.isUsed = True
    await update_point(coupon.rp, item.id)

    return await select_my_info(UserIdParam(id=item.id))


async def update_point(point, id_):
    user = session.query(UserTable).filter(UserTable.id == id_).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")

    lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == user.index).first()
    if not lolketingUser:
        raise_http_exception("유저 정보가 없습니다.")

    totalPoint = lolketingUser.point + point
    if totalPoint <= 999_999:
        lolketingUser.point = totalPoint
    else:
        lolketingUser.point = 999_999

    lolketingUser.grade = getUserGrade(totalPoint)
    session.commit()


@router.post("/update/myInfo", summary="내 정보 업데이트")
async def update_my_info(item: UpdateMyInfoItem) -> str:
    """
    - **id**: 유저 이메일 (필수)
    - **nickname**: 닉네임 (필수)
    - **mobile**: 핸드폰 번호
    - **address**: 주소
    """
    user = session.query(UserTable).filter(UserTable.id == item.id).first()
    if not user:
        raise_http_exception("유저 정보가 없습니다.")

    if user.nickname != item.nickname and check_duplicate_nickname(item.nickname):
        raise_http_exception("중복된 닉네임입니다.")

    user.nickname = item.nickname
    user.mobile = item.mobile
    user.address = item.address

    session.commit()
    return "업데이트 완료"


@router.post("/select/roulette", summary="룰렛 횟수 조회")
async def select_roulette(item: UserIdParam) -> RouletteCount:
    session.commit()

    lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == item.id).first()
    return RouletteCount(count=lolketingUser.roulette)


@router.post("/update/roulette", summary="룰렛 횟수 업데이트")
async def update_roulette(item: RouletteCountUpdateItem) -> RouletteCount:
    session.commit()

    lolketingUser = session.query(LolketingUserTable).filter(LolketingUserTable.user_id == item.id).first()
    lolketingUser.roulette = lolketingUser.roulette + item.count

    session.commit()
    return RouletteCount(count=lolketingUser.roulette)
