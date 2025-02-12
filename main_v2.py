import streamlit as st
import pandas as pd
from helper_v2 import DataRetriever
import plotly.express as px

def formatEarningsHistory(df):
    df = df[["Report Time", "Reported Date"]]
    df["Report Time"] = df["Report Time"].replace({
        "post-market": "After Close",
        "pre-market": "Before Open"
    })
    return df

code = st.text_input("Enter code to use this app", type="password")

if code == "Mario":

    # Number of rows in the table (dynamic)
    num_rows = st.slider("Number of rows", min_value=1, max_value=20, value=10)
    ticker = st.text_input("Enter Ticker Symbol", placeholder="AAPL, TSLA, etc.")

    dr = DataRetriever(ticker=ticker)
    if ticker:
        stock_price = dr.getStockPrice()
        earnings_data = dr.getEarningsData(num_rows)
        earnings_history = dr.getEarningsHistory(num_rows)
    else:
        stock_price = 0
        earnings_data = None
        earnings_history = None

    st.subheader(f"Stock Price: ${stock_price}")  # Display stock price beside input

    if earnings_history is not None:
        df = pd.DataFrame(earnings_history, columns=["Reported Date", "Report Time"])
        df_formatted = formatEarningsHistory(df)
        st.write("Earnings History Table")
        st.dataframe(df_formatted, use_container_width=True)

    if earnings_data is not None:
        # Convert earnings_data to DataFrame
        df = pd.DataFrame(earnings_data, columns=["Reported Date", "Report Time", "Price Before", "Price After", "Price Difference", "Percentage Difference"])
        st.write("Earnings Data Table")
        st.dataframe(df, use_container_width=True)

        # analyze the data. find the average percentage difference, quartiles, etc.
        average_percentage_difference = df["Percentage Difference"].mean()
        quartiles = df["Percentage Difference"].quantile([0.25, 0.5, 0.75])
        st.write(f"Average Percentage Difference: {average_percentage_difference}%")
        st.write(f"Quartiles: {quartiles}")

        # plot the price difference as a boxplot
        st.write("Boxplot of Price Differences")
        fig = px.box(df, y="Price Difference")
        st.plotly_chart(fig)

        # plot the percentage difference as a boxplot
        st.write("Boxplot of Percentage Differences")
        fig = px.box(df, y="Percentage Difference")
        st.plotly_chart(fig)
