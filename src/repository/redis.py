import redis
import json
from src.repository.repository import Repository
from src.model.models import MODELS

class RedisRepository(Repository):
    def __init__(self, host='localhost', port=6379, db=0, model_name='cipher'):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.model = MODELS[model_name]
        self.model_name = model_name

    def _key(self, index):
        return f"{self.model_name}:{index}"

    def add(self, item):
        data = item.to_dict()
        index = data.get('id') or data.get('index')
        if index is None:
            raise ValueError('Item must have an id or index')
        self.r.set(self._key(index), json.dumps(data))

    def get(self, index):
        raw = self.r.get(self._key(index))
        if raw:
            data = json.loads(raw)
            return self.model.from_dict(data)
        return None
    
    def get_all(self):
        pattern = f"{self.model_name}:*"
        keys = self.r.keys(pattern)
        items = []
        for key in keys:
            raw = self.r.get(key)
            if raw:
                data = json.loads(raw)
                items.append(self.model.from_dict(data))
        return items

    def update(self, index, item):
        if self.r.exists(self._key(index)):
            self.r.set(self._key(index), json.dumps(item.to_dict()))

    def delete(self, index):
        self.r.delete(self._key(index))
