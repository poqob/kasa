from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

class ModelSession(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
    expiration = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "expiration": self.expiration.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            token=data.get("token"),
            expiration=datetime.strptime(data.get("expiration"), '%Y-%m-%d %H:%M:%S'),
        )

    def __repr__(self):
        return f"DTOSession(token={self.token!r}, expiration={self.expiration!r})"