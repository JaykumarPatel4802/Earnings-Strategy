import requests
import streamlit as st
import pandas as pd
import json

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
            price_before_earnings = None
            price_after_earnings = None
            
            date_split = reportedDate.split('-')
            current_date_open, current_date_close, position = self.__getDayData(reportedDate)
            if (position == "Middle" and reportTime == "pre-market") or (position == "End" and reportTime == "pre-market"):
                # get previous day data
                previous_date = date_split[0] + '-' + date_split[1] + '-' + str(int(date_split[2]) - 1).zfill(2)
                previous_date_open, previous_date_close, _ = self.__getDayData(previous_date)
                price_before_earnings = previous_date_close
                price_after_earnings = current_date_open
            elif (position == "Middle" and reportTime == "post-market") or (position == "Beginning" and reportTime == "post-market"):
                # get next day data
                next_date = date_split[0] + '-' + date_split[1] + '-' + str(int(date_split[2]) + 1).zfill(2)
                next_date_open, next_date_close, _ = self.__getDayData(next_date)
                price_before_earnings = current_date_close
                price_after_earnings = next_date_open
            elif position == "Beginning":
                # reaching here implies we need previous day's data (last day of previous month)
                if int(date_split[1]) - 1 >= 1:
                    previous_month = date_split[0] + '-' + str(int(date_split[1]) - 1).zfill(2)
                else:
                    previous_month = str(int(date_split[0]) - 1).zfill(2) + '-' + '12'
                previous_date_open, previous_date_close = self.__getMonthEdgeData(previous_month, "Last")
                price_before_earnings = previous_date_close
                price_after_earnings = current_date_open
            else:
                # reaching here implies position is "End" and we need next day's data (first day of next month)
                if int(date_split[1]) + 1 <= 12:
                    next_month = date_split[0] + '-' + str(int(date_split[1]) + 1).zfill(2)
                else:
                    next_month= str(int(date_split[0]) - 1).zfill(2) + '-' + '01'
                next_date_open, next_date_close = self.__getMonthEdgeData(next_month, "First")
                price_before_earnings = current_date_close
                price_after_earnings = next_date_open

            percent_price_change = abs(((float(price_after_earnings) - float(price_before_earnings)) / float(price_before_earnings)) * 100)
            price_change = abs(float(price_after_earnings) - float(price_before_earnings))
            earnings_data.append({
                "reportedDate": reportedDate,
                "reportTime": reportTime,
                "priceBeforeEarnings": float(price_before_earnings),
                "priceAfterEarnings": float(price_after_earnings),
                "priceChange": price_change,
                "percentPriceChange": percent_price_change
            })
        
        return earnings_data