from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List
from model.userModel import UserTable

Base = declarative_base()


class TeamTable(Base):
    __tablename__ = 'team'
    teamId = Column(Integer, primary_key=True)
    name = Column(String)
    image = Column(String)


class GameTable(Base):
    __tablename__ = 'game'
    gameId = Column(Integer, primary_key=True)
    gameDate = Column(DateTime)
    leftTeamId = Column(Integer)
    rightTeamId = Column(Integer)
    seats = relationship("SeatTable", back_populates="game")
    reservations = relationship("ReservationTable", back_populates="game")


class Game(BaseModel):
    gameDate: datetime = None
    leftTeamId: int
    rightTeamId: int


def create_game(item: Game) -> GameTable:
    game = GameTable()
    game.gameDate = item.gameDate
    game.leftTeamId = item.leftTeamId
    game.rightTeamId = item.rightTeamId

    return game


class SeatTable(Base):
    __tablename__ = 'seat'
    seatId = Column(Integer, primary_key=True)
    gameId = Column(Integer, ForeignKey('game.gameId'))
    seatNumber = Column(String)
    game = relationship("GameTable", back_populates="seats")
    reservations = relationship("ReservationTable", back_populates="seat")


class Seat(BaseModel):
    gameId: int
    seatNumber: str


def create_seat(gameId: int, seatNumber: str) -> SeatTable:
    seat = SeatTable()
    seat.gameId = gameId
    seat.seatNumber = seatNumber

    return seat


class ReservationTable(Base):
    __tablename__ = 'reservation'
    reservationId = Column(Integer, primary_key=True)
    gameId = Column(Integer, ForeignKey('game.gameId'))
    seatId = Column(Integer, ForeignKey('seat.seatId'))
    userId = Column(Integer, ForeignKey(UserTable.index))
    reservationDate = Column(DateTime)
    game = relationship("GameTable", back_populates="reservations")
    seat = relationship("SeatTable", back_populates="reservations")


class Reservation(BaseModel):
    gameId: int
    seatId: int
    userId: int
    reservationDate: datetime


def createReservation(gameId: int, seatId: int, userId: int, date: datetime) -> ReservationTable:
    reservation = ReservationTable()
    reservation.gameId = gameId
    reservation.seatId = seatId
    reservation.userId = userId
    reservation.reservationDate = date

    return reservation


class ReservationTicketItem(BaseModel):
    gameId: int
    userId: int
    count: int
    seatNumber: str


class GameIdParam(BaseModel):
    gameId: int


class TicketIdList(BaseModel):
    idList: List[int]


class CustomException(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message
