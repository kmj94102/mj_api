from fastapi import APIRouter
from sqlalchemy import and_
from db import session
from model.boardModel import *
from model.ticket import *
from model.common import raise_http_exception

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

    if item.teamId == 0:
        tableIds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    else:
        tableIds = [item.teamId]

    boards = session.query(
        BoardTable.id,
        BoardTable.contents,
        BoardTable.image,
        BoardTable.timestamp,
        BoardTable.userId,
        TeamTable.name,
        UserTable.nickname,
    ).filter(
        BoardTable.teamId.in_(tableIds)
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).group_by(
        BoardTable.id
    ).order_by(
        BoardTable.timestamp.desc()
    ).offset(item.skip).limit(item.limit).all()

    result = []
    for board in boards:
        boardId, contents, image, timestamp, userId, name, nickname = board

        likeCount = session.query(BoardLikeTable).filter(BoardLikeTable.boardId == boardId).count()
        commentCount = session.query(CommentTable).filter(CommentTable.boardId == boardId).count()
        isLike = session.query(BoardLikeTable).filter(
            and_(BoardLikeTable.userId == item.userId, BoardLikeTable.boardId == boardId)
        ).first() is not None
        isAuthor = item.userId == userId

        boardItem = BoardItem(id=boardId, contents=contents, image=image, isAuthor=isAuthor,
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
        BoardTable.userId,
        BoardTable.timestamp,
        TeamTable.name,
        UserTable.nickname
    ).filter(
        BoardTable.id == boardId
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).first()

    id_, contents, image, boardUserId, timestamp, name, nickname = board

    likeCount = session.query(BoardLikeTable).filter(BoardLikeTable.boardId == boardId).count()
    commentCount = session.query(CommentTable).filter(CommentTable.boardId == boardId).count()
    isLike = session.query(BoardLikeTable).filter(
        and_(BoardLikeTable.userId == userId, BoardLikeTable.boardId == boardId)
    ).first() is not None
    isAuthor = boardUserId == userId

    boardItem = BoardItem(id=boardId, contents=contents, image=image, isAuthor=isAuthor,
                          timestamp=timestamp.strftime("%Y.%m.%d %H:%M"), name=name, nickname=nickname,
                          likeCount=likeCount, isLike=isLike, commentCount=commentCount)

    return boardItem


@router.post("/select/boardDetail", summary="게시글 상세 조회")
async def select_board_detail(item: BoardDetailParam) -> BoardDetail:
    session.commit()

    board = session.query(
        BoardTable.contents,
        BoardTable.image,
        BoardTable.userId,
        BoardTable.timestamp,
        TeamTable.name,
        UserTable.nickname,
    ).filter(
        BoardTable.id == item.boardId
    ).join(
        TeamTable, TeamTable.teamId == BoardTable.teamId
    ).join(
        UserTable, UserTable.index == BoardTable.userId
    ).first()

    contents, image, userId, timestamp, name, nickname = board

    likeCount = session.query(BoardLikeTable).filter(BoardLikeTable.boardId == item.boardId).count()
    isLike = session.query(BoardLikeTable).filter(
        and_(BoardLikeTable.userId == item.userId, BoardLikeTable.boardId == item.boardId)
    ).first() is not None
    commentList = await select_comments(boardId=item.boardId, userId=item.userId)
    isAuthor = item.userId == userId

    boardItem = BoardDetail(id=item.boardId, contents=contents, image=image, isAuthor=isAuthor,
                            timestamp=timestamp.strftime("%Y.%m.%d %H:%M"), name=name, nickname=nickname,
                            likeCount=likeCount, isLike=isLike, commentList=commentList)

    return boardItem


@router.post("/update/board", summary="게시글 수정")
async def updateBoard(item: Board) -> str:
    board = session.query(BoardTable).filter(BoardTable.id == item.id).first()

    if board is None:
        raise_http_exception("게시글 정보가 없습니다.")
    elif item.userId != board.userId:
        raise_http_exception("게시글 수정은 작성자만 가능합니다.")

    board.contents = item.contents
    board.image = item.image
    board.teamId = item.teamId
    session.commit()

    return "게시글 수정 완료"


@router.post("/delete/board", summary="게시글 삭제")
async def deleteBoard(item: BoardIdInfoParam) -> str:
    session.commit()
    board = session.query(BoardTable).filter(BoardTable.id == item.boardId).first()

    if board is None:
        raise_http_exception("게시글 정보가 없습니다.")
    elif board.userId != item.userId:
        raise_http_exception("게시글 삭제는 작성자만 가능합니다.")
    else:
        session.delete(board)
        session.commit()

    return "삭제 완료"


@router.post("/insert/comment", summary="댓글 등록")
async def insert_comment(item: CommentWriteParam) -> List[Comment]:
    comment = item.toTable()
    session.add(comment)
    session.commit()

    return await select_comments(item.boardId, item.userId)


@router.post("/select/commentList", summary="댓글 조회")
async def select_comments(boardId: int, userId: int) -> List[Comment]:
    session.commit()

    comments = session.query(
        CommentTable.id.label("commentId"),
        CommentTable.contents,
        CommentTable.timestamp,
        CommentTable.boardId,
        CommentTable.userId,
        UserTable.nickname
    ).filter(
        CommentTable.boardId == boardId
    ).join(
        UserTable, UserTable.index == CommentTable.userId
    ).all()

    result = []
    for comment in comments:
        commentId, contents, timestamp, boardId, commentUserId, nickname = comment
        isAuthor = commentUserId == userId
        result.append(
            Comment(commentId=commentId, contents=contents, timestamp=timestamp.strftime("%Y.%m.%d %H:%M"),
                    boardId=boardId, userId=commentUserId, nickname=nickname, isAuthor=isAuthor)
        )

    return result


@router.post("/update/comment", summary="댓글 수정")
async def updateComment(item: Comment) -> str:
    comment = session.query(CommentTable).filter(CommentTable.id == item.commentId).first()

    if comment is None or comment.boardId != item.boardId:
        raise_http_exception("댓글 정보가 없습니다.")
    elif item.userId != comment.userId:
        raise_http_exception("댓글 수정은 작성자만 가능합니다.")

    comment.contents = item.contents

    session.commit()

    return "댓글 수정 완료"


@router.post("/delete/comment", summary="댓글 삭제")
async def delete_comment(item: CommentDeleteParam) -> List[Comment]:
    session.commit()
    comment = session.query(CommentTable).filter(
        CommentTable.id == item.commentId
    ).first()

    if comment is None or comment.boardId != item.boardId:
        raise_http_exception("댓글 정보가 없습니다.")
    elif item.userId != comment.userId:
        raise_http_exception("댓글 삭제는 작성자만 가능합니다.")
    else:
        session.delete(comment)
        session.commit()

    return await select_comments(item.boardId, item.userId)


@router.post("/update/boardLike", summary="게시글 좋아요 업데이트")
async def update_board_like(item: BoardIdInfoParam) -> BoardItem:
    session.commit()

    boardLike = session.query(BoardLikeTable).filter(
        BoardLikeTable.boardId == item.boardId, BoardLikeTable.userId == item.userId
    ).first()

    if boardLike:
        session.delete(boardLike)
        session.commit()
    else:
        boardLike = item.toBoardLikeTable()
        session.add(boardLike)
        session.commit()

    return await select_board(item.boardId, item.userId)
