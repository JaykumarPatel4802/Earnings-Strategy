import streamlit as st
from pages.helpers.helper import DataRetriever
from pages.stock_details import formatEarningsHistory
import pandas as pd

st.title("Auto Screener")

code = st.text_input("Enter code to use this app", type="password", key="auto_screener_code")

if code == "Mario":

    price_range = st.slider("Price Range", min_value=0, max_value=500, value=(40, 250))
    tickers = st.text_input("Tickers (comma separated)", placeholder="AAPL, TSLA, NVDA, ...")
    num_rows = st.slider("Number of historical earnings data points to use", min_value=1, max_value=20, value=10)
    percent_change_threshold = st.slider("Percent Change Threshold", min_value=0, max_value=100, value=10)

    low_price = price_range[0]
    high_price = price_range[1]

    if st.button("Run"):
        st.write(f"Running the screener for {low_price} to {high_price}")

        shortlist = {}

        for ticker in tickers.split(","):
            # get average percent change in earnings history
            try:
                dr = DataRetriever(ticker)
                stock_price = dr.getStockPrice()

                if stock_price < low_price or stock_price > high_price:
                    continue

                earnings_data = dr.getEarningsData(num_rows)
                earnings_history = dr.getEarningsHistory(num_rows)

                earnings_data_df = pd.DataFrame(earnings_data, columns=["Reported Date", "Report Time", "Price Before", "Price After", "Absolute Price Difference", "Absolute Percentage Difference", "Adjusted Price Difference"])
                earnings_history_df = pd.DataFrame(earnings_history, columns=["Reported Date", "Report Time"])
                earnings_history_df = formatEarningsHistory(earnings_history_df)

                # get average percent change in earnings history
                average_percentage_difference = earnings_data_df["Absolute Percentage Difference"].mean()

                if average_percentage_difference > percent_change_threshold and low_price <= stock_price <= high_price:
                    shortlist[ticker] = {
                        "stock_price": stock_price,
                        "earnings_data": earnings_data,
                        "earnings_data_df": earnings_data_df,
                        "earnings_history": earnings_history,
                        "earnings_history_df": earnings_history_df,
                        "average_percentage_difference": average_percentage_difference
                    }

            
            except Exception as e:
                st.error(f"Error processing Ticker: {ticker}: {e}")
                continue

        for ticker, data in shortlist.items():
            st.write(f"{ticker} - Price: ${data['stock_price']} - Average Percentage Difference: {data['average_percentage_difference']}%")
            with st.expander("Additional Data"):
                st.write("Earnings Data Table")
                st.dataframe(data['earnings_data_df'], use_container_width=True)

                st.write("Earnings History Table")
                st.dataframe(data['earnings_history_df'], use_container_width=True)
