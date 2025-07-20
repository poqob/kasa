#cache.py
from src.repository.redis import RedisRepository
from src.repository.sqlite import SqliteRepository

class CacheManager:
    def __init__(self,model_name: str):
        self.model_name = model_name
        self.redis_repo = RedisRepository(model_name=model_name)
        self.sqlite_repo = SqliteRepository(db_url='sqlite:///db/kasa.db', model_name=model_name)

    def sync(self):
        # Fetch all items from SQLite
        sqlite_items = self.sqlite_repo.get_all()

        # Add items to Redis
        for item in sqlite_items:
            self.redis_repo.r.hset(f"{self.model_name}:{item.id}", mapping=item.to_dict())

    def flush_cache(self)-> bool:
        redis_repo = RedisRepository(model_name=self.model_name)
        return redis_repo.r.flushdb(asynchronous=True)
    
    


