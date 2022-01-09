from traceback import TracebackException
from clients.krypton_client import KryptonApiClient
from clients.redis_client import RedisOrderClient
from clients.redis_client import RedisClient
from config.config import REDIS_TICKER_DB,REDIS_ATR_DB,ALL_TIMEFRAMES,PROBABLITEIS_COEFFICIENT,MINIMUM_ORDER_IN_ORDER_BOOK,TRADING_VOLUME_COEFFICIENT,FIX_IRT_TRADING_AMOUNT,FIX_USDT_TRADING_AMOUNT
import numpy as np
import json


class MarketMakerBot:
    def __init__(self,pair) -> None:
        self.pair = pair
        self.redis_orders = RedisOrderClient(pair)
        self.redis_tick_data = RedisClient(REDIS_TICKER_DB)
        self.redis_atr = RedisClient(REDIS_ATR_DB)
        self.krypton = KryptonApiClient(self.pair)
            
    def create_noisy_tick(self):
        redis = self.redis_atr
        atr = float(redis.get(f'ATR_{self.pair}_1m'))
        if atr > 1 :
            std_atr = np.sqrt(atr) #std = atr and it can be changed
        else:
            std_atr = atr**2 #std = atr and it can be changed
        noise = np.random.normal(std_atr,std_atr/10,1)
        return noise
            
    def create_humanly_volume(self,volume):
        random_fix = np.random.uniform(1,3)
        if float(volume) < 1:
            for digit in str(float(volume)):
                if digit != "0" and digit != ".":
                    first_digit = digit
                    first_digit_index = str(volume).index(first_digit)
                    str_humanly_number = str(float(volume))[:int(first_digit_index)+int(random_fix)]
                    return float(str_humanly_number)
        else:
            for number in str(float(volume)):
                if number == ".":
                    index_digit = str(float(volume)).index(".")
                    if index_digit>random_fix:
                        humanly_number = str(float(volume[:random_fix]))+str("0"*len(volume)-random_fix-index_digit)
                    else:
                        humanly_number = str(float(volume))[:int(random_fix)]
            return float(humanly_number)
                
    def create_bot_or_humanly_volume(self,volume):
        creator =  np.random.choice(["human","bot"],1,p=[0.5,0.5])
        if creator == "human":
            human_volume = self.create_humanly_volume(volume)
            return human_volume
        if creator == "bot":
            bot_volume = volume
            return bot_volume
        
    def create_limit_alltimeframe_orders(self):
        atrs = {}
        last_crypto_price = float(self.redis_tick_data.get(self.pair).decode())
        last_krypton_price = self.krypton.get_last_price(self.pair)
        redis = self.redis_atr
        for time_frame in ALL_TIMEFRAMES:
            atrs[time_frame] = float(redis.get(f'ATR_{self.pair}_{time_frame}'))
        if  self.redis_orders.get_len_buy_order() < MINIMUM_ORDER_IN_ORDER_BOOK/2:
            new_side = None
            choice_time_frame_order = np.random.choice(list(PROBABLITEIS_COEFFICIENT.keys()),int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_buy_order(),p=list(PROBABLITEIS_COEFFICIENT.values()))
            for choice in choice_time_frame_order:
                choosen_atr = atrs[choice]
                if choosen_atr > 1:
                    std_choosen_atr = choosen_atr #std = atr and it can be changed
                else:
                    std_choosen_atr = choosen_atr #std = atr and it can be changed
                choosen_volume_coeff = TRADING_VOLUME_COEFFICIENT[choice]
                if last_crypto_price < last_krypton_price:
                    new_order_price = last_crypto_price - abs(np.random.normal(std_choosen_atr,std_choosen_atr/10,1))
                    if self.pair.endswith("_IRT"):
                        fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                    if self.pair.endswith("_USDT"):
                        fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                    random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                    final_volume = self.create_bot_or_humanly_volume(random_volume)
                    self.krypton.set_order(self.pair.lower(),"limit","buy",final_volume,new_order_price)
                if last_crypto_price > last_krypton_price:
                    if int(MINIMUM_ORDER_IN_ORDER_BOOK/2)- self.redis_orders.get_len_sell_order() > 0:
                        choice_time_frame_order = np.random.choice(list(PROBABLITEIS_COEFFICIENT.keys()),int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_sell_order(),p=list(PROBABLITEIS_COEFFICIENT.values()))
                        new_side = "sell"
                        for choice in choice_time_frame_order:
                            choosen_atr = atrs[choice]
                            if choosen_atr > 1:
                                std_choosen_atr = choosen_atr #std = atr and it can be changed
                            else:
                                std_choosen_atr = choosen_atr #std = atr and it can be changed
                            choosen_volume_coeff = TRADING_VOLUME_COEFFICIENT[choice]
                            new_order_price = last_crypto_price + abs(np.random.normal(std_choosen_atr,std_choosen_atr/10,1))
                            if self.pair.endswith("_IRT"):
                                fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            if self.pair.endswith("_USDT"):
                                fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                            final_volume = self.create_bot_or_humanly_volume(random_volume)
                            self.krypton.set_order(self.pair.lower(),"limit",new_side,final_volume,new_order_price)
                    
        if self.redis_orders.get_len_sell_order() < MINIMUM_ORDER_IN_ORDER_BOOK/2:
            new_side = None
            if int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_sell_order():
                choice_time_frame_order = np.random.choice(list(PROBABLITEIS_COEFFICIENT.keys()),int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_sell_order(),p=list(PROBABLITEIS_COEFFICIENT.values()))
                for choice in choice_time_frame_order:
                    choosen_atr = atrs[choice]
                    if choosen_atr > 1:
                        std_choosen_atr = choosen_atr #std = atr and it can be changed
                    else:
                        std_choosen_atr = choosen_atr #std = atr and it can be changed
                    choosen_volume_coeff = TRADING_VOLUME_COEFFICIENT[choice]
                    if last_crypto_price > last_krypton_price:
                        new_order_price = abs(np.random.normal(std_choosen_atr,std_choosen_atr/10,1))+last_crypto_price
                        if self.pair.endswith("_IRT"):
                            fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                            final_volume = self.create_bot_or_humanly_volume(random_volume)
                        if self.pair.endswith("_USDT"):
                            fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                            final_volume = self.create_bot_or_humanly_volume(random_volume)
                        self.krypton.set_order(self.pair.lower(),"limit","sell",final_volume,new_order_price)
            if last_crypto_price < last_krypton_price:
                new_side = "buy"
                if int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_buy_order() > 0:
                    choice_time_frame_order = np.random.choice(list(PROBABLITEIS_COEFFICIENT.keys()),int(MINIMUM_ORDER_IN_ORDER_BOOK/2)-self.redis_orders.get_len_buy_order(),p=list(PROBABLITEIS_COEFFICIENT.values()))
                    for choice in choice_time_frame_order:
                        choosen_atr = atrs[choice]
                        if choosen_atr > 1:
                            std_choosen_atr = choosen_atr #std = atr and it can be changed
                        else:
                            std_choosen_atr = choosen_atr #std = atr and it can be changed
                        if self.pair.endswith("_IRT"):
                            fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                            final_volume = self.create_bot_or_humanly_volume(random_volume)
                        if self.pair.endswith("_USDT"):
                            fix_volume = FIX_IRT_TRADING_AMOUNT*choosen_volume_coeff/last_crypto_price
                            random_volume = fix_volume+abs(np.random.normal(0,fix_volume/10,1))
                            final_volume = self.create_bot_or_humanly_volume(random_volume)
                        choosen_volume_coeff = TRADING_VOLUME_COEFFICIENT[choice]
                        new_order_price = last_crypto_price - abs(np.random.normal(std_choosen_atr,std_choosen_atr/10,1))
                        self.krypton.set_order(self.pair.lower(),"limit",new_side,final_volume,new_order_price)
                        
    def create_limit_tick_timeframe_order(self,side):
        try:
            if self.redis_orders.get_len_buy_order() or self.redis_orders.get_len_sell_order() < MINIMUM_ORDER_IN_ORDER_BOOK/2:
                self.create_limit_alltimeframe_orders()
        except:
            self.create_limit_alltimeframe_orders()
        new_side = None
        last_crypto_price = float(self.redis_tick_data.get(self.pair).decode())
        last_krypton_price = self.krypton.get_last_price(self.pair)
        noise = abs(self.create_noisy_tick())
        if side == "buy" and last_crypto_price < last_krypton_price:
            new_order_price = last_crypto_price-noise
        if side == "sell" and last_crypto_price > last_krypton_price:
            new_order_price = last_crypto_price+noise
        if side == "buy" and last_crypto_price > last_krypton_price:
            new_side = "sell"
            new_order_price = last_crypto_price+noise
        if side == "sell" and last_crypto_price < last_krypton_price:
            new_side = "buy"
            new_order_price = last_crypto_price - noise
        if self.pair.endswith("_IRT"):
            fix_volume = FIX_IRT_TRADING_AMOUNT*TRADING_VOLUME_COEFFICIENT["1m"]/last_crypto_price
        if self.pair.endswith("_USDT"):
            fix_volume = FIX_USDT_TRADING_AMOUNT*TRADING_VOLUME_COEFFICIENT["1m"]/last_crypto_price
        random_volume = fix_volume+np.random.normal(0,fix_volume/10,1)
        final_volume = self.create_bot_or_humanly_volume(random_volume)
        if not new_side:
            self.krypton.set_order(self.pair.lower(),"limit",side,final_volume,new_order_price)
        if new_side:
            self.krypton.set_order(self.pair.lower(),"limit",new_side,final_volume,new_order_price)
    
    def get_nearest_order_id(self):
        redis = self.redis_tick_data
        krypton_orders = self.redis_orders.all()
        last_crpyto_com_price = redis.get(self.pair).decode()
        diff_prices = {}
        if krypton_orders:
            for order in krypton_orders:
                order_id = order["uid"]
                if float(last_crpyto_com_price) < float(order['price']):
                    diff_prices[order_id]=float(order['price'])-float(last_crpyto_com_price)
                if float(last_crpyto_com_price) > float(order['price']):
                    diff_prices[order_id]=float(last_crpyto_com_price)-float(order['price'])
            nearest_order_id = min(diff_prices,key=diff_prices.get)
            return nearest_order_id

    def cancel_outlier_orders(self):
        krypton_orders = self.redis_orders.all()
        daily_atr = float(self.redis_atr.get(f"ATR_{self.pair}_1D"))
        last_crpyto_com_price = float(self.redis_tick_data.get(self.pair))
        if krypton_orders:
            for order in krypton_orders:
                diffrence = abs(float(last_crpyto_com_price)-float(order['price']))
                if diffrence > daily_atr:
                    self.krypton.cancel_order(order["uid"])
        
    def create_market_order(self):
        self.create_limit_alltimeframe_orders()
        nearest_order_id = self.get_nearest_order_id()
        nearest_order = json.loads(self.redis_orders.get(nearest_order_id).decode())
        price = nearest_order["price"]
        quantity = nearest_order["amount"]
        krypton_order_side = nearest_order["side"]
        if krypton_order_side == "buy":
            new_order_side = "sell"
        else:
            new_order_side = "buy"
        self.krypton.set_order(self.pair,"market",new_order_side,quantity,price)
        self.create_limit_tick_timeframe_order(new_order_side)
        
    def run(self):
        self.krypton.cancel_all_orders() # can be uncomment or comment
        self.create_limit_alltimeframe_orders()
        while True:
            self.cancel_outlier_orders()
            self.create_market_order()
            