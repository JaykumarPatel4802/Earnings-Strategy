import streamlit as st
import pandas as pd
from helper import DataRetriever

# Number of rows in the table (dynamic)
num_rows = st.slider("Number of rows", min_value=1, max_value=20, value=7)
ticker = st.text_input("Enter Ticker Symbol", placeholder="AAPL, TSLA, etc.")

dr = DataRetriever(ticker=ticker)
stock_price = dr.getPrice()
st.subheader(f"Stock Price: ${stock_price}")  # Display stock price beside input




# Placeholder for the table data
data = {"Delta $": [0] * num_rows, "Delta %": [0] * num_rows, "% to Points": [0] * num_rows}

# Creating the dynamic table
for i in range(num_rows):
    col1, col2 = st.columns(2)
    
    # Input A and Input B
    data["Delta $"][i] = col1.number_input(f"{i+1}Q - $ Delta", key=f"input_a_{i}", format="%0.5f")
    data["Delta %"][i] = col2.number_input(f"{i+1}Q - % Delta", key=f"input_b_{i}", format="%0.5f")
    
    # # Output C (dynamic value based on Input A and Input B)
    # data["Output C"][i] = data["Input A"][i] + data["Input B"][i]  # Example logic
    # col3.write(f"{data['Output C'][i]}")  # Display Output C
    data["% to Points"][i] = (data["Delta %"][i] * stock_price)

# Convert to DataFrame and display
df = pd.DataFrame(data)
st.write("Final Table:")
st.dataframe(df)
