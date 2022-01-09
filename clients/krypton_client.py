from clients.redis_client import RedisOrderClient
from config.config import BASE_URL_KRYPTON_ORDER_API, BOT_NAME , DEFAULT_BOT_ID
from clients.cryptocom_client import CryptoApiClient
import requests
import json
import traceback


class KryptonApiClient:
    def __init__(self,pair) -> None:
        self.redis_orders = RedisOrderClient(pair)
        self.base_url = BASE_URL_KRYPTON_ORDER_API
        self.bot_id = DEFAULT_BOT_ID
        self.auth = {}
        
    def get_token(self):
        url = self.base_url+"/order/bot/get_token"
        body = {'bot_uid': DEFAULT_BOT_ID}
        response_token = requests.post(url, json=body)
        response_token = json.loads(response_token.content)['body']
        response = response_token['token']
        self.auth['auth']=response
        
    def list_coins(self):
        url = self.base_url+"/order/coins"
        coins = json.loads(requests.post(url).content)['body']['coins']
        return coins
    
    def list_bot_orders(self):
        url = self.base_url+"/order/bot/get_bot_orders"
        try:
            orders = json.loads(requests.post(url,headers=self.auth).content)['body']['orders']
            return orders
        except:
            self.get_token()
            try:
                orders = json.loads(requests.post(url,headers=self.auth).content)['body']['orders']
                return orders
            except Exception:
                with open("log.txt","a") as log:
                    log.write(traceback.format_exc())           
        
    def get_len_bot_orders(self):
        return(len(self.list_bot_orders()))
    
    def list_pairs_on_based_usdt(self):
        pairs = []
        coins = self.list_coins()
        for coin in coins:
            pair = coin+"_USDT"
            pairs.append(pair)
        return pairs
    
    def get_valid_usdt_pairs(self):
        cac = CryptoApiClient()
        crypto_pairs = cac.list_pairs()
        kac = KryptonApiClient()
        crypto_pairs = cac.list_pairs()
        krypton_pairs = kac.list_pairs_on_based_usdt()
        pairs = list(set(krypton_pairs) & set(crypto_pairs))
        return pairs
    
    def get_valid_irt_pairs(self):
        pairs = self.get_valid_usdt_pairs()
        irt_pairs = []
        for pair in pairs:
            first_symbol = pair.split("_")[0]
            irt_pairs.append(first_symbol+"_IRT")
        return irt_pairs
    
    def get_all_pairs(self):
        irt_base_pair = self.get_valid_irt_pairs()
        usdt_base_pair = self.get_valid_usdt_pairs()
        all_pairs = irt_base_pair + usdt_base_pair
        return all_pairs
    
    def get_last_price(self,pair):
        request = requests.post(url=self.base_url+"/cron/current-price",data={"pair":pair},headers=self.auth)
        if json.loads(request.content)['status'] == 401:
            self.get_token()
            self.get_last_price(pair)
        price = json.loads(request.content)['body']['price']
        return price
    
    def cancel_order(self,order_id):
        response = requests.post(self.base_url+"/order/bot/cancel",data={"order_id":order_id},headers=self.auth)
        if json.loads(response.content)['status'] == 401:
            self.get_token()
            self.cancel_order(order_id)
        if json.loads(response.content)['status']==200:
            return response
        
    def set_order(self, pair,order_type,side, quantity, price):
        order = {
            'price': price,
            'side': side,
            'type': order_type,
            'amount': quantity,
            'pair': pair,
            'bot_name' : BOT_NAME
            }
        response = requests.post(self.base_url+"/order/bot/submit",data=order, headers=self.auth)
        if json.loads(response.content)['status'] == 401:
            self.get_token()
            self.set_order(pair,order_type,side,quantity,price)
        if json.loads(response.content)['status']==200:
            return response
        
    def cancel_all_orders(self):
        orders = self.list_bot_orders()
        for order in orders:
            self.cancel_order(order['uid'])
        