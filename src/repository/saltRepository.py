import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.model.model_salt import ModelSalt, Base
from src.repository.repository import Repository


class SaltRepository(Repository):
    def __init__(self, sqlite_path, redis_host='localhost', redis_port=6379, redis_db=0):
        self.engine = create_engine(f'sqlite:///{sqlite_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def add(self, item: ModelSalt):
        session = self.Session()
        session.add(item)
        session.commit()
        session.refresh(item)
        salt_id = item.id
        session.close()
        self.redis.hset(f"salt:{salt_id}", mapping=item.to_dict())
        return salt_id

    def get(self, index):
        data = self.redis.hgetall(f"salt:{index}")
        if data:
            return ModelSalt.from_dict(data)
        session = self.Session()
        salt = session.query(ModelSalt).filter_by(id=index).first()
        session.close()
        if salt:
            self.redis.hset(f"salt:{index}", mapping=salt.to_dict())
            return salt
        return None

    def update(self, index, item: ModelSalt):
        session = self.Session()
        db_salt = session.query(ModelSalt).filter_by(id=index).first()
        if db_salt:
            db_salt.method = item.method
            db_salt.salt = item.salt
            session.commit()
            self.redis.hset(f"salt:{index}", mapping=db_salt.to_dict())
        session.close()

    def delete(self, index):
        session = self.Session()
        salt = session.query(ModelSalt).filter_by(id=index).first()
        if salt:
            session.delete(salt)
            session.commit()
        session.close()
        self.redis.delete(f"salt:{index}")

    def delete_all(self):
        session = self.Session()
        session.query(ModelSalt).delete()
        session.commit()
        session.close()
        self.redis.flushdb()

    def get_all(self):
        session = self.Session()
        salts = session.query(ModelSalt).all()
        session.close()
        for salt in salts:
            self.redis.hset(f"salt:{salt.id}", mapping=salt.to_dict())
        return salts
