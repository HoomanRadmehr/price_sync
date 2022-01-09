from config.config import REDIS_ALL_ORDERS_DB_NUMBER, REDIS_HOST ,REDIS_PORT , REDIS_PASSWORD , REDIS_YAML_PATH , DEFAULT_REDIS_DB
import redis
import json
import yaml


class RedisClient:
    def __init__(self,db=None) -> None:
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.password = REDIS_PASSWORD
        if db:
            self.db = db
        else:
            self.db = DEFAULT_REDIS_DB
        self.redis = redis.Redis(self.host,self.port,self.db,self.password)
        
    def get(self,key):
        return self.redis.get(key)
            
    def get_json(self,key):
        try:
            return json.loads(self.get(key).decode())
        except:
            pass
    
    def all(self):
        list_keys = self.redis.keys()
        datas = []
        for key in list_keys:
            datas.append(self.get_json(key))
        return datas
    
    def delete(self,key):
        self.redis.delete(key)
        
class RedisOrderClient(RedisClient):
    def __init__(self, pair) -> None:
        db = self.get_db_number(pair)
        super().__init__(db)
        
    def get_db_number(self,pair):
        redis = RedisClient(REDIS_ALL_ORDERS_DB_NUMBER)
        return int(redis.get(f"ORDER_DB_NUMBER_{pair}"))

    def get_len_buy_order(self):
        return len([order for order in self.all() if order['side']=='buy'])
    
    def get_len_sell_order(self):
        return len([order for order in self.all() if order['side']=='sell'])