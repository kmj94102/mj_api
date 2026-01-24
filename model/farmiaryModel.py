from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from db import Base
from pydantic import BaseModel


class IdParam(BaseModel):
    idx: int = None


class FarmiaryUserTable(Base):
    __tablename__ = "farmiary_users"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    login_type = Column(String(20))
    name = Column(String(50))
    profile_image = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class FarmiaryUser(BaseModel):
    loginType: str = None
    email: str = None
    name: str = None
    profileImage: str = None

    def toTable(self) -> FarmiaryUserTable:
        return FarmiaryUserTable(
            login_type=self.loginType,
            email=self.email,
            name=self.name,
            profile_image=self.profileImage,
            created_at=datetime.now()
        )


class LoginParam(BaseModel):
    email: str = None
    loginType: str = None


class FarmTable(Base):
    __tablename__ = "farms"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    info = Column(Text)
    qr = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class FarmGroupTable(Base):
    __tablename__ = "farm_groups"

    farm_idx = Column(Integer, ForeignKey("farms.idx"), primary_key=True)
    user_idx = Column(Integer, ForeignKey("farmiary_users.idx"), primary_key=True)
    role = Column(String(20), nullable=False)

    farm = relationship("FarmTable", foreign_keys=[farm_idx])
    user = relationship("FarmiaryUserTable", foreign_keys=[user_idx])


class NewAddFarm(BaseModel):
    name: str = None
    address: str = None
    info: str = None
    userIdx: int = None

    def toFarmTable(self) -> FarmTable:
        now = datetime.now()
        return FarmTable(
            name=self.name,
            address=self.address,
            info=self.info,
            qr=f"Farmiary_{self.name}_{now}",
            created_at=now
        )

    def toFarmGroupTable(self, farmIdx) -> FarmGroupTable:
        return FarmGroupTable(
            farm_idx=farmIdx,
            user_idx=self.userIdx,
            role="MASTER",
        )


class GroupSearch(BaseModel):
    qr: str = None


class JoinFarm(BaseModel):
    qr: str = None
    userIdx: int = None

    def toTable(self, farmIdx) -> FarmGroupTable:
        return FarmGroupTable(
            farm_idx=farmIdx,
            user_idx=self.userIdx,
            role="MEMBER"
        )


class WithdrawalFarm(BaseModel):
    userIdx: int = None
    farmIdx: int = None


class PlantTable(Base):
    __tablename__ = "plants"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    farm_idx = Column(Integer, ForeignKey("farms.idx"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    farm = relationship("FarmTable", foreign_keys=[farm_idx])


class Plant(BaseModel):
    farmIdx: int = None
    name: str = None
    startDate: str = None
    endDate: str = None

    def toTable(self) -> PlantTable:
        return PlantTable(
            farm_idx=self.farmIdx,
            name=self.name,
            start_date=yearMonthConver(self.startDate),
            end_date=yearMonthConver(self.endDate)
        )


class ScheduleTable(Base):
    __tablename__ = "farmiary_schedules"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    farm_idx = Column(Integer, ForeignKey("farms.idx"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    contents = Column(Text)

    farm = relationship("FarmTable", foreign_keys=[farm_idx])
    plants = relationship(
        "SchedulePlantTable",
        back_populates="schedule"
    )

    workers = relationship(
        "ScheduleWorkerTable",
        back_populates="schedule"
    )


class ScheduleWorkerTable(Base):
    __tablename__ = "schedule_workers"

    schedule_idx = Column(Integer, ForeignKey("farmiary_schedules.idx"), primary_key=True)
    user_idx = Column(Integer, ForeignKey("farmiary_users.idx"), primary_key=True)

    # schedule = relationship("ScheduleTable", foreign_keys=[schedule_idx])
    # user = relationship("FarmiaryUserTable", foreign_keys=[user_idx])
    schedule = relationship(
        "ScheduleTable",
        back_populates="workers"
    )

    user = relationship("FarmiaryUserTable", foreign_keys=[user_idx])


class SchedulePlantTable(Base):
    __tablename__ = "schedule_plants"

    schedule_idx = Column(Integer, ForeignKey("farmiary_schedules.idx"), primary_key=True)
    plant_idx = Column(Integer, ForeignKey("plants.idx"), primary_key=True)

    # schedule = relationship("ScheduleTable", foreign_keys=[schedule_idx])
    # plant = relationship("PlantTable", foreign_keys=[plant_idx])
    schedule = relationship(
        "ScheduleTable",
        back_populates="plants"
    )

    plant = relationship("PlantTable", foreign_keys=[plant_idx])


class ScheduleParam(BaseModel):
    farmIdx: int = None
    scheduledAt: datetime = None
    contents: str = None
    workerList: List[int]
    plantList: List[int]

    def toScheduleTable(self) -> ScheduleTable:
        return ScheduleTable(
            farm_idx=self.farmIdx,
            scheduled_at=self.scheduledAt,
            contents=self.contents
        )

    def toScheduleWorkerTableList(self, idx) -> List[ScheduleWorkerTable]:
        return [
            ScheduleWorkerTable(
                schedule_idx=idx,
                user_idx=userIdx
            )
            for userIdx in self
        ]

    def toSchedulePlantTableList(self, idx) -> List[SchedulePlantTable]:
        return [
            SchedulePlantTable(
                schedule_idx=idx,
                plant_idx=plantIdx
            )
            for plantIdx in self
        ]


def yearMonthConver(yearMonth: str) -> Optional[date]:
    if yearMonth is None:
        return None

    if isinstance(yearMonth, str) and yearMonth.strip() == "":
        return None

    year, month_num = map(int, yearMonth.split("."))
    result = date(year, month_num, 1)

    return result


class MonthScheduleParam(BaseModel):
    year: int = None
    month: int = None
    userIdx: int = None


class HomeParam(BaseModel):
    year: int = None
    month: int = None
    date: int = None
    userIdx: int = None
