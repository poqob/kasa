from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class ModelSalt(Base):
    __tablename__ = 'salt'

    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String, nullable=False)
    salt = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "method": self.method,
            "salt": self.salt,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            method=data.get("method"),
            salt=data.get("salt"),
        )
    
    def __repr__(self):
        return f"ModelSalt(id={self.id}, method={self.method}, salt={self.salt})"