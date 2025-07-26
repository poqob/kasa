from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.repository.repository import Repository
from src.model.models import MODELS

class SqliteRepository(Repository):
    def __init__(self, db_url: str, model_name: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.model = MODELS[model_name]
        self.model.__table__.create(self.engine, checkfirst=True)

    def add(self, item):
        session = self.Session()
        session.add(item)
        session.commit()
        session.close()

    def get(self, index):
        session = self.Session()
        result = session.query(self.model).filter_by(id=index).first()
        session.close()
        return result


    def get_all(self):
        session = self.Session()
        results = session.query(self.model).all()
        session.close()
        return results

    def update(self, index, item):
        session = self.Session()
        obj = session.query(self.model).filter_by(id=index).first()
        if obj:
            for key, value in item.to_dict().items():
                if key != 'id' and hasattr(obj, key):
                    setattr(obj, key, value)
            session.commit()
        session.close()

    def delete(self, index):
        session = self.Session()
        obj = session.query(self.model).filter_by(id=index).first()
        if obj:
            session.delete(obj)
            session.commit()
        session.close()
