from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class ModelCipher(Base):
    __tablename__ = 'cipher'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    encrypted_cipher = Column(String, nullable=False)
    method = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "encrypted_cipher": self.encrypted_cipher,
            "method": self.method,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            encrypted_cipher=data.get("encrypted_cipher"),
            method=data.get("method"),
        )
    