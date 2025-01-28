import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DataRetriever:
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()

    def __checkTicker(self):
        return True if self.ticker != "" else False
    
    def getPrice(self):
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.ticker}&apikey={os.getenv("ALPHA_VANTAGE_KEY")}'
        r = requests.get(url)
        data = r.json()

        return float(data["Global Quote"]["05. price"]) if self.__checkTicker() else 0