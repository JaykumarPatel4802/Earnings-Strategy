import requests
import streamlit as st

class DataRetriever:
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()

    def __checkTicker(self):
        return True if self.ticker != "" else False
    
    def getPrice(self):
        if not self.__checkTicker():
            return 0
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.ticker}&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()

        return float(data["Global Quote"]["05. price"])