from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from db import session
from model.userModel import *
from model.couponModel import *
import re

router = APIRouter()


def raise_http_exception(detail: str = "Eror", status_code: int = 400):
    raise HTTPException(status_code=status_code, detail=detail)


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
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$'

    # 비밀번호 패턴과 매치되는지 확인
    if re.match(pattern, password):
        return True
    else:
        return False


@router.post("/join/email")
async def join_email(item: User):
    """
    회원가입
    :param item:
    :return:
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

    try:
        session.rollback()
        session.begin()

        user = create_user_table(item)
        session.add(user)
        session.flush()

        coupon = create_new_user_coupon(user)
        session.add(coupon)

        lolketing_user = create_lolketing_user_table(user)
        session.add(lolketing_user)

        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise_http_exception(f"오류가 발생하였습니다. {e}")
    finally:
        session.close()

    return "회원가입 완료"


@router.post("/login/email")
async def email_login(item: LoginInfo):
    """
    이메일 로그인
    :param item:
    :return:
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
        return {
            'id': data.id,
            'nickname': data.nickname
        }


@router.post("/login/social")
async def social_login(item: SocialLoginInfo):
    """
    소셜 로그인
    :param item:
    :return:
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
        return {
            'id': data.id,
            'nickname': data.nickname
        }


@router.post("/select/myInfo")
async def select_my_info(user_id: str):
    """
        내 정보 조회
        :param user_id:
        :return:
    """
    session.commit()
    user_info_query = session.query(
        UserTable.nickname,
        UserTable.id,
        UserTable.mobile,
        UserTable.address,
        LolketingUserTable.grade,
        LolketingUserTable.point,
        LolketingUserTable.cash,
        func.count(CouponTable.id).label("total_coupons"),
        func.sum(func.cast(~CouponTable.isUsed, Integer)).label("unused_coupons")
    ).join(
        LolketingUserTable, UserTable.index == LolketingUserTable.user_id
    ).join(
        CouponTable, UserTable.index == CouponTable.user_id
    ).filter(
        UserTable.id == user_id,
    ).group_by(
        UserTable.nickname,
        UserTable.id,
        UserTable.mobile,
        UserTable.address,
        LolketingUserTable.grade,
        LolketingUserTable.point,
        LolketingUserTable.cash
    ).first()

    return user_info_query
