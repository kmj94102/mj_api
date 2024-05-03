from sqlalchemy import Column, Integer, DateTime, Text
from pydantic import BaseModel
from db import Base
from datetime import datetime
from typing import List


class Board(BaseModel):
    id: int = 0
    contents: str = None
    image: str = None
    timestamp: datetime = None
    teamId: int = None
    userId: int = None


class BoardTable(Base):
    __tablename__ = 'board'
    id = Column(Integer, primary_key=True, autoincrement=True)
    contents = Column(Text)
    image = Column(Text)
    timestamp = Column(DateTime)
    teamId = Column(Integer)
    userId = Column(Integer)


class Comment(BaseModel):
    commentId: int = 0
    contents: str = None
    timestamp: str = None
    boardId: int = None
    userId: int = None
    nickname: str = None
    isAuthor: bool = None


class CommentTable(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    contents = Column(Text)
    timestamp = Column(DateTime)
    userId = Column(Integer)
    boardId = Column(Integer)


class BoardLikeTable(Base):
    __tablename__ = 'board_like'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    userId = Column(Integer)
    boardId = Column(Integer)


class BoardIdInfoParam(BaseModel):
    userId: int = None
    boardId: int = None

    def toBoardLikeTable(self) -> BoardLikeTable:
        return BoardLikeTable(
            timestamp=datetime.now(),
            userId=self.userId,
            boardId=self.boardId
        )


class BoardSelectParam(BaseModel):
    skip: int = 0
    limit: int = 10
    teamId: int
    userId: int


class CommentDeleteParam(BaseModel):
    commentId: int
    boardId: int
    userId: int


class BoardItem(BaseModel):
    id: int
    contents: str
    image: str
    isAuthor: bool
    timestamp: str
    name: str
    nickname: str
    likeCount: int
    isLike: bool
    commentCount: int


class BoardWriteParam(BaseModel):
    contents: str
    image: str
    teamId: int
    userId: int

    def toTable(self) -> BoardTable:
        return BoardTable(
            contents=self.contents,
            image=self.image,
            timestamp=datetime.now(),
            teamId=self.teamId,
            userId=self.userId
        )


class CommentWriteParam(BaseModel):
    contents: str
    userId: int
    boardId: int

    def toTable(self) -> CommentTable:
        return CommentTable(
            contents=self.contents,
            timestamp=datetime.now(),
            userId=self.userId,
            boardId=self.boardId
        )


class BoardDetail(BaseModel):
    id: int
    contents: str
    image: str
    isAuthor: bool
    timestamp: str
    name: str
    nickname: str
    likeCount: int
    isLike: bool
    commentList: List[Comment]


class BoardDetailParam(BaseModel):
    boardId: int
    userId: int
