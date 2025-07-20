
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.model.model_cipher import ModelCipher, Base
from src.repository.repository import Repository


class CipherRepository(Repository):
    def __init__(self, sqlite_path, redis_host='localhost', redis_port=6379, redis_db=0):
        self.engine = create_engine(f'sqlite:///{sqlite_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def add(self, item: ModelCipher):
        session = self.Session()
        session.add(item)
        session.commit()
        session.refresh(item)
        cipher_id = item.id
        session.close()
        self.redis.hset(f"cipher:{cipher_id}", mapping=item.to_dict())
        return cipher_id

    def get(self, index):
        data = self.redis.hgetall(f"cipher:{index}")
        if data:
            return ModelCipher.from_dict(data)
        session = self.Session()
        cipher = session.query(ModelCipher).filter_by(id=index).first()
        session.close()
        if cipher:
            self.redis.hset(f"cipher:{index}", mapping=cipher.to_dict())
            return cipher
        return None

    def update(self, index, item: ModelCipher):
        session = self.Session()
        db_cipher = session.query(ModelCipher).filter_by(id=index).first()
        if db_cipher:
            db_cipher.name = item.name
            db_cipher.encrypted_cipher = item.encrypted_cipher
            db_cipher.method = item.method
            session.commit()
            self.redis.hset(f"cipher:{index}", mapping=db_cipher.to_dict())
        session.close()

    def delete(self, index):
        session = self.Session()
        cipher = session.query(ModelCipher).filter_by(id=index).first()
        if cipher:
            session.delete(cipher)
            session.commit()
        session.close()
        self.redis.delete(f"cipher:{index}")

    def get_all(self):
        session = self.Session()
        ciphers = session.query(ModelCipher).all()
        session.close()
        for cipher in ciphers:
            self.redis.hset(f"cipher:{cipher.id}", mapping=cipher.to_dict())
        return ciphers
