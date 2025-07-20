import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.model.model_session import ModelSession, Base
from src.repository.repository import Repository


class SessionRepository(Repository):
    def __init__(self, sqlite_path, redis_host='localhost', redis_port=6379, redis_db=0):
        self.engine = create_engine(f'sqlite:///{sqlite_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    def add(self, item: ModelSession):
        session = self.Session()
        session.add(item)
        session.commit()
        session.refresh(item)
        session_id = item.id
        session.close()
        self.redis.hset(f"session:{session_id}", mapping=item.to_dict())
        return session_id

    def get(self, index):
        data = self.redis.hgetall(f"session:{index}")
        if data:
            return ModelSession.from_dict(data)
        session = self.Session()
        session_obj = session.query(ModelSession).filter_by(id=index).first()
        session.close()
        if session_obj:
            self.redis.hset(f"session:{index}", mapping=session_obj.to_dict())
            return session_obj
        return None

    def update(self, index, item: ModelSession):
        session = self.Session()
        db_session = session.query(ModelSession).filter_by(id=index).first()
        if db_session:
            db_session.token = item.token
            db_session.expiration = item.expiration
            session.commit()
            self.redis.hset(f"session:{index}", mapping=db_session.to_dict())
        session.close()

    def delete(self, index):
        session = self.Session()
        session_obj = session.query(ModelSession).filter_by(id=index).first()
        if session_obj:
            session.delete(session_obj)
            session.commit()
        session.close()
        self.redis.delete(f"session:{index}")

    def get_all(self):
        session = self.Session()
        sessions = session.query(ModelSession).all()
        session.close()
        for session_obj in sessions:
            self.redis.hset(f"session:{session_obj.id}", mapping=session_obj.to_dict())
        return sessions
