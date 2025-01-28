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