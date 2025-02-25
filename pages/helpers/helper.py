import requests
import streamlit as st
import pandas as pd
import json
import yfinance as yf
from datetime import datetime, timedelta

class DataRetriever:
    
    def __init__(self, ticker):
        self.ticker = ticker.strip().upper()
        self.stock_price = None
    
    def getStockPrice(self):
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.ticker}&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()

        self.stock_price = float(data["Global Quote"]["05. price"])

        return self.stock_price
    
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

        # Extract the date
        date = df['date'].iloc[0]

        columns_to_remove = ['date', 'contractID', 'symbol', 'delta', 'gamma', 'theta', 'vega', 'rho']

        # Drop the columns
        df = df.drop(columns=columns_to_remove)

        # Split the DataFrame into call and put data
        df_calls = df[df['type'] == 'call'].copy()
        df_puts = df[df['type'] == 'put'].copy()

        # Drop the 'type' column since it is redundant after splitting
        df_calls.drop(columns=['type'], inplace=True)
        df_puts.drop(columns=['type'], inplace=True)

        # Rename columns to differentiate call and put data
        df_calls = df_calls.add_prefix('call_')
        df_puts = df_puts.add_prefix('put_')

        df_option_chain = pd.merge(
            df_calls,
            df_puts,
            left_on=['call_strike', 'call_expiration'],
            right_on=['put_strike', 'put_expiration'],
            suffixes=('_call', '_put')
        )

        # Drop duplicate columns (like strike and expiration appearing twice)
        df_option_chain.drop(columns=['put_strike', 'put_expiration'], inplace=True)

        # Rename strike and expiration for clarity
        df_option_chain.rename(columns={'call_strike': 'strike', 'call_expiration': 'expiration'}, inplace=True)

        # Define the desired order for the suffixes of call_ and put_ columns
        column_order = [
            "_ask", "_ask_size", "_bid", "_bid_size", "_mark", "_last",
            "_volume", "_open_interest", "_implied_volatility"
        ]

        # Build the ordered list of columns
        call_columns = [f"call{suffix}" for suffix in column_order][::-1]
        put_columns = [f"put{suffix}" for suffix in column_order]

        # Combine into the final column order: call columns, strike/expiration, put columns
        final_column_order = call_columns + ['strike', 'expiration'] + put_columns

        # Reorder the DataFrame
        df_option_chain = df_option_chain[final_column_order]

        return date, df_option_chain
    
    def getEarningsHistory(self, numberOfRows):
        url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={self.ticker}&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()
        quarterly_earnings = data["quarterlyEarnings"]
        quarterly_earnings = quarterly_earnings[:min(numberOfRows, len(quarterly_earnings))] if quarterly_earnings[0]["reportedEPS"] != "None" else quarterly_earnings[1:min(numberOfRows + 1, len(quarterly_earnings))]
        return [(entry["reportedDate"], entry["reportTime"]) for entry in quarterly_earnings]
    
    def __getDayData(self, date):
        month = '-'.join(date.split('-')[:2])
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={self.ticker}&interval=1min&month={month}&outputsize=full&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()
        dates = list(data["Time Series (1min)"].keys())
        position = "Middle"
        if date in dates[0]:
            position = "End"
        elif date in dates[-1]:
            position = "Beginning"
        
        open_price = data["Time Series (1min)"][f"{date} 09:30:00"]["1. open"]
        close_price = data["Time Series (1min)"][f"{date} 16:00:00"]["4. close"]

        return open_price, close_price, position
    
    def __getMonthEdgeData(self, month, edge):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={self.ticker}&interval=30min&month={month}&outputsize=full&apikey={st.secrets["ALPHA_VANTAGE_KEY"]}'
        r = requests.get(url)
        data = r.json()
        dates = list(data["Time Series (30min)"].keys())
        if edge == "First":
            date = dates[-1]
        else:
            date = dates[0]
        
        date = date.split(" ")[0]
        
        open_price = data["Time Series (30min)"][f"{date} 09:30:00"]["1. open"]
        close_price = data["Time Series (30min)"][f"{date} 16:00:00"]["4. close"]

        return open_price, close_price

    def getEarningsData(self, numberOfRows):

        earnings_history = self.getEarningsHistory(numberOfRows)

        earnings_data = []

        for reportedDate, reportTime in earnings_history:
            # Convert reportedDate string to datetime object
            reportedDate = datetime.strptime(reportedDate, '%Y-%m-%d')

            if reportTime == "Pre-Market":
                # use yfinance to get stock price for reportedDate and 4 days before
                stock = yf.Ticker(self.ticker)
                stock_price = stock.history(start=reportedDate - timedelta(days=4), end=reportedDate)

                # get opening price for reportedDate
                opening_price = stock_price.iloc[-1]["Open"]

                # get closing price for 1 day before reportedDate
                closing_price = stock_price.iloc[-2]["Close"]

                # get price difference
                price_difference = closing_price - opening_price

                # get percentage difference
                percentage_difference = (price_difference / opening_price) * 100

                # get adjusted price difference
                adjusted_price_difference = (percentage_difference / 100) * self.stock_price
                
            else:
                # use yfinance to get stock price for reportedDate and 4 days after
                stock = yf.Ticker(self.ticker)
                stock_price = stock.history(start=reportedDate, end=reportedDate + timedelta(days=4))

                # get opening price for reportedDate
                opening_price = stock_price.iloc[0]["Close"]

                # get closing price for 1 day after reportedDate
                closing_price = stock_price.iloc[1]["Open"]

                # get price difference
                price_difference = abs(closing_price - opening_price)

                # get percentage difference
                percentage_difference = abs((price_difference / opening_price) * 100)

                # get adjusted price difference
                adjusted_price_difference = (percentage_difference / 100) * self.stock_price

            earnings_data.append((reportedDate, reportTime, opening_price, closing_price, price_difference, percentage_difference, adjusted_price_difference))

        return earnings_data