from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Text
from datetime import datetime
Base = declarative_base()


class AdProfitTable(Base):
    __tablename__ = 'ad_profit'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text)
    refreshToken = Column(Text)
    accessToken = Column(Text)
    device = Column(Text)
    timestamp = Column(DateTime)


class AdProfit(BaseModel):
    email: str = None
    refreshToken: str = None
    accessToken: str = None
    device: str = None

    def toTable(self) -> AdProfitTable:
        return AdProfitTable(
            email=self.email,
            refreshToken=self.refreshToken,
            accessToken=self.accessToken,
            device=self.device,
            timestamp=datetime.now()
        )
