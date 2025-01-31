import streamlit as st
import pandas as pd
from helper import DataRetriever

def optionsDFHighlighter(x):
    # Create a DataFrame of styles, same shape as `x`, with empty defaults
    styles = pd.DataFrame("", index=x.index, columns=x.columns)
    
    # Apply specific styles to the desired columns
    styles["strike"] = "background-color: lightblue;"
    
    return styles

def formatEarningsHistory(df):
    df = df[["Report Time", "Reported Date"]]
    df["Report Time"] = df["Report Time"].replace({
        "post-market": "After Close",
        "pre-market": "Before Open"
    })
    return df

code = st.text_input("Enter code to use this app")

if code == "Mario":

    # Number of rows in the table (dynamic)
    num_rows = st.slider("Number of rows", min_value=1, max_value=20, value=10)
    ticker = st.text_input("Enter Ticker Symbol", placeholder="AAPL, TSLA, etc.")

    dr = DataRetriever(ticker=ticker)
    if ticker:
        stock_price = dr.getStockPrice()
        # options_date, options_df = dr.getOptionsData()
        # earnings_data = dr.getEarningsData(num_rows)
        options_date, options_df = None, None
        earnings_data = None
        earnings_history = dr.getEarningsHistory(num_rows)
    else:
        stock_price = 0
        options_date, options_df = None, None
        earnings_data = None
        earnings_history = None

    st.subheader(f"Stock Price: ${stock_price}")  # Display stock price beside input


    # if earnings_data is not None:
    #     # Convert the data into a DataFrame
    #     df = pd.DataFrame(earnings_data)

    #     # Optional: Format the percentPriceChange column to show percentages
    #     df['percentPriceChange'] = df['percentPriceChange'].apply(lambda x: f"{x}%")

    #     # Display the DataFrame as a table in Streamlit
    #     st.write("Earnings Report Table:")
    #     st.dataframe(df, use_container_width=True)

    # if options_df is not None:
    #     st.subheader(f"Displaying options data for: {options_date}")

    #     # Group the DataFrame by expiration
    #     grouped = options_df.groupby("expiration")

    #     # Iterate through each group and apply the highlighter
    #     for expiration_date, group in grouped:
    #         # Apply styling to the group
    #         styled_group = group.style.apply(optionsDFHighlighter, axis=None)

    #         # Use an expander for each expiration group
    #         with st.expander(f"Expiration: {expiration_date}", expanded=False):
    #             # Display the styled DataFrame
    #             st.dataframe(styled_group, use_container_width=True)

    if earnings_history is not None:
        df = pd.DataFrame(earnings_history, columns=["Reported Date", "Report Time"])
        df_formatted = formatEarningsHistory(df)
        st.write("Earnings History Table")
        st.dataframe(df_formatted, use_container_width=True)
