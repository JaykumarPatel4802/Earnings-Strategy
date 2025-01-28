import requests
import streamlit as st
import pandas as pd

class DataRetriever:
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()
    
    def getStockPrice(self):
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.ticker}&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()

        return float(data["Global Quote"]["05. price"])
    
    def getOptionsData(self):
        url = f'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&datatype=csv&symbol={self.ticker}&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.text.split('\r\n')
        
        # Split the header and rows
        header = data[0].split(',')
        rows = [row.split(',') for row in data[1:len(data)-1]]

        # Create DataFrame
        df = pd.DataFrame(rows, columns=header)

        # Convert numeric columns to appropriate data types
        numeric_columns = ['strike', 'last', 'mark', 'bid', 'bid_size', 'ask', 'ask_size', 'volume', 
                        'open_interest', 'implied_volatility', 'delta', 'gamma', 'theta', 'vega', 'rho']

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df