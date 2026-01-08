from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Text, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, relationship
from db import Base
from pydantic import BaseModel


class UserTable(Base):
    __tablename__ = "farmiary_users"

    idx = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    login_type = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False)
    profile_image = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("FarmGroup", back_populates="user")
    
    
class FarmiaryUser(BaseModel):
    idx: int = None
    email: str = None
    loginType: str = None
    name: str = None
    profileImage: str = None
    createdAt: datetime = None


class FarmTable(Base):
    __tablename__ = "farms"

    idx = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    info = Column(Text)
    qr = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("FarmGroup", back_populates="farm")
    plants = relationship("Plant", back_populates="farm")
    schedules = relationship("Schedule", back_populates="farm")


class Farmiary(BaseModel):
    idx: int = None
    name: str = None
    address: str = None
    info: str = None
    qr: str = None
    createdAt: datetime = None


class FarmGroupTable(Base):
    __tablename__ = "farm_groups"

    farm_idx = Column(Integer, ForeignKey("farms.idx"), primary_key=True)
    user_idx = Column(Integer, ForeignKey("users.idx"), primary_key=True)
    role = Column(String(20), nullable=False)

    farm = relationship("Farm", back_populates="users")
    user = relationship("User", back_populates="farms")


class FarmGroup(BaseModel):
    farmIdx: int = None
    userIdx: int = None
    role: str = None


class PlantTable(Base):
    __tablename__ = "plants"

    idx = Column(Integer, primary_key=True)
    farm_idx = Column(Integer, ForeignKey("farms.idx"), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

    farm = relationship("Farm", back_populates="plants")
    schedules = relationship("SchedulePlant", back_populates="plant")


class Plant(BaseModel):
    idx: int = None
    farmIdx: int = None
    name: str = None
    startDate: datetime = None
    endDate: datetime = None


class ScheduleTable(Base):
    __tablename__ = "farmiary_schedules"

    idx = Column(Integer, primary_key=True)
    farm_idx = Column(Integer, ForeignKey("farms.idx"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    contents = Column(Text)

    farm = relationship("Farm", back_populates="schedules")
    workers = relationship("ScheduleWorker", back_populates="schedule")
    plants = relationship("SchedulePlant", back_populates="schedule")


class FarmiarySchedule(BaseModel):
    idx: int = None
    farmIdx: int = None
    scheduledAt: str = None
    contents: str = None


class ScheduleWorkerTable(Base):
    __tablename__ = "schedule_workers"

    schedule_idx = Column(Integer, ForeignKey("schedules.idx"), primary_key=True)
    user_idx = Column(Integer, ForeignKey("users.idx"), primary_key=True)

    schedule = relationship("Schedule", back_populates="workers")
    user = relationship("User")


class ScheduleWorker(BaseModel):
    idx: int = None
    farmIdx: int = None
    scheduledAt: str = None
    contents: str = None


class SchedulePlantTable(Base):
    __tablename__ = "schedule_plants"

    schedule_idx = Column(Integer, ForeignKey("schedules.idx"), primary_key=True)
    plant_idx = Column(Integer, ForeignKey("plants.idx"), primary_key=True)

    schedule = relationship("Schedule", back_populates="plants")
    plant = relationship("Plant", back_populates="schedules")


class SchedulePlant(BaseModel):
    scheduleIdx: int = None
    plantIdx: int = None
