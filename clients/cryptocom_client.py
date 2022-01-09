from config.config import CRYPTO_COM_BASE_API_URL
from json import loads
import requests

class CryptoApiClient:
    def __init__(self) -> None:
        self.base_url = CRYPTO_COM_BASE_API_URL
        
    def list_pairs(self):
        list_pairs = []
        pairs = loads(requests.get(f"{self.base_url}/public/get-instruments").content)['result']['instruments']
        for pair in pairs:
            list_pairs.append(pair['instrument_name'])
        return list_pairs
    