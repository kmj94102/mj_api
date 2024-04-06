from fastapi import APIRouter
from sqlalchemy import func, and_
from db import session
from model.boardModel import *
from model.ticket import *

from typing import List

router = APIRouter()


@router.post("/insert/board", summary="게시글 등록")
async def insert_board(item: BoardWriteParam) -> str:
    board = item.toTable()
    session.add(board)
    session.commit()

    return "등록 완료"


@router.post("/select/boards", summary="게시글 조회")
async def select_boards(item: BoardSelectParam) -> List[BoardItem]:
    session.commit()
    boards = session.query(
        BoardTable.id,
        BoardTable.contents,
        BoardTable.image,
        BoardTable.timestamp,
        TeamTable.name,
        UserTable.nickname,
        func.coalesce(func.count(BoardLikeTable.id), 0).label("likeCount"),
        func.coalesce(func.count(CommentTable.id), 0).label("commentCount"),
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).outerjoin(
        BoardLikeTable, BoardLikeTable.boardId == BoardTable.id
    ).outerjoin(
        CommentTable, CommentTable.boardId == BoardTable.id
    ).group_by(
        BoardTable.id
    ).offset(item.skip).limit(item.limit).all()

    result = []
    for board in boards:
        boardId, contents, image, timestamp, name, nickname, likeCount, commentCount = board

        isLike = session.query(BoardLikeTable).filter(
            and_(BoardLikeTable.userId == item.userId, BoardLikeTable.boardId == boardId)
        ).first() is not None

        boardItem = BoardItem(id=boardId, contents=contents, image=image,
                              timestamp=timestamp.strftime("%Y.%m.%d %H:%M"), name=name, nickname=nickname,
                              likeCount=likeCount, isLike=isLike, commentCount=commentCount)
        result.append(boardItem)

    return result


async def select_board(boardId: int, userId: int) -> BoardItem:
    session.commit()
    board = session.query(
        BoardTable.id,
        BoardTable.contents,
        BoardTable.image,
        BoardTable.timestamp,
        TeamTable.name,
        UserTable.nickname,
        func.coalesce(func.count(BoardLikeTable.id), 0).label("likeCount"),
        func.coalesce(func.count(CommentTable.id), 0).label("commentCount"),
    ).filter(
        BoardTable.id == boardId
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).outerjoin(
        BoardLikeTable, BoardLikeTable.boardId == BoardTable.id
    ).outerjoin(
        CommentTable, CommentTable.boardId == BoardTable.id
    ).group_by(
        BoardTable.id
    ).first()

    id_, contents, image, timestamp, name, nickname, likeCount, commentCount = board
    isLike = session.query(BoardLikeTable).filter(
        and_(BoardLikeTable.userId == userId, BoardLikeTable.boardId == boardId)
    ).first() is not None

    boardItem = BoardItem(id=boardId, contents=contents, image=image,
                          timestamp=timestamp.strftime("%Y.%m.%d %H:%M"), name=name, nickname=nickname,
                          likeCount=likeCount, isLike=isLike, commentCount=commentCount)

    return boardItem


@router.post("/insert/comment", summary="댓글 등록")
async def insert_comment(item: CommentWriteParam) -> str:
    comment = item.toTable()
    session.add(comment)
    session.commit()

    return "등록 완료"


@router.post("/select/commentList", summary="댓글 조회")
async def select_comments(boardId: int) -> List[Comment]:
    session.commit()
    comments = session.query(CommentTable).filter(CommentTable.boardId == boardId).all()
    return [comment.mapper() for comment in comments]


@router.post("/select/boardDetail", summary="게시글 상세 조회")
async def select_board_detail(item: BoardDetailParam) -> BoardDetail:
    session.commit()
    board = session.query(
        BoardTable.id,
        BoardTable.contents,
        BoardTable.image,
        BoardTable.timestamp,
        TeamTable.name,
        UserTable.nickname,
        func.coalesce(func.count(BoardLikeTable.id), 0).label("likeCount"),
    ).filter(
        BoardTable.id == item.boardId
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).outerjoin(
        BoardLikeTable, BoardLikeTable.boardId == BoardTable.id
    ).outerjoin(
        CommentTable, CommentTable.boardId == BoardTable.id
    ).group_by(
        BoardTable.id
    ).first()

    id_, contents, image, timestamp, name, nickname, likeCount = board
    isLike = session.query(BoardLikeTable).filter(
        and_(BoardLikeTable.userId == item.userId, BoardLikeTable.boardId == item.boardId)
    ).first() is not None
    commentList = await select_comments(boardId=item.boardId)

    boardItem = BoardDetail(id=item.boardId, contents=contents, image=image,
                            timestamp=timestamp.strftime("%Y.%m.%d %H:%M"), name=name, nickname=nickname,
                            likeCount=likeCount, isLike=isLike, commentList=commentList)

    return boardItem


@router.post("/delete/comment", summary="댓글 삭제")
async def delete_comment(item: CommentDeleteParam) -> List[Comment]:
    session.commit()
    comment = session.query(CommentTable).filter(
        CommentTable.id == item.commentId, CommentTable.userId == item.userId
    ).first()

    if comment:
        session.delete(comment)
        session.commit()

    return await select_comments(item.boardId)


@router.post("/update/boardLike", summary="게시글 좋아요 업데이트")
async def update_board_like(item: BoardLike) -> BoardItem:
    session.commit()

    boardLike = session.query(BoardLikeTable).filter(
        BoardLikeTable.boardId == item.boardId, BoardLikeTable.userId == item.userId
    ).first()

    if boardLike:
        session.delete(boardLike)
        session.commit()
    else:
        boardLike = item.toTable()
        session.add(boardLike)
        session.commit()

    return await select_board(item.boardId, item.userId)
