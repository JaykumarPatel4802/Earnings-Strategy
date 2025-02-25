import streamlit as st
from pages.helpers.helper import DataRetriever
import pandas as pd

st.title("Auto Screener")

code = st.text_input("Enter code to use this app", type="password")

if code == "Mario":

    price_range = st.slider("Price Range", min_value=0, max_value=500, value=(40, 250))
    tickers = st.text_input("Tickers (comma separated)")
    num_rows = st.slider("Number of rows", min_value=1, max_value=20, value=10)
    percent_change_threshold = st.slider("Percent Change Threshold", min_value=0, max_value=100, value=10)

    low_price = price_range[0]
    high_price = price_range[1]

    if st.button("Run"):
        st.write(f"Running the screener for {low_price} to {high_price}")

        shortlist = {}

        for ticker in tickers.split(","):
            print(f"Processing {ticker}")
            # get average percent change in earnings history
            try:
                dr = DataRetriever(ticker)
                stock_price = dr.getStockPrice()

                if stock_price < low_price or stock_price > high_price:
                    continue

                earnings_data = dr.getEarningsData(num_rows)
                earnings_history = dr.getEarningsHistory(num_rows)

                df = pd.DataFrame(earnings_data, columns=["Reported Date", "Report Time", "Price Before", "Price After", "Absolute Price Difference", "Absolute Percentage Difference", "Adjusted Price Difference"])

                # get average percent change in earnings history
                average_percentage_difference = df["Absolute Percentage Difference"].mean()

                print(f"{ticker} - Price: ${stock_price} - Average Percentage Difference: {average_percentage_difference}%")

                if average_percentage_difference > percent_change_threshold and low_price <= stock_price <= high_price:
                    shortlist[ticker] = {
                        "stock_price": stock_price,
                        "earnings_data": earnings_data,
                        "earnings_data_df": df,
                        "earnings_history": earnings_history,
                        "average_percentage_difference": average_percentage_difference
                    }

            
            except Exception as e:
                continue

        for ticker, data in shortlist.items():
            st.write(f"{ticker} - Price: ${data['stock_price']} - Average Percentage Difference: {data['average_percentage_difference']}%")
            with st.expander("Additional Data"):
                st.write(data)
