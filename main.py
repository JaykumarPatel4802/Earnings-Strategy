import streamlit as st
import pandas as pd
from helper import DataRetriever

def optionsDFHighlighter(x):
    # Create a DataFrame of styles, same shape as `x`, with empty defaults
    styles = pd.DataFrame("", index=x.index, columns=x.columns)
    
    # Apply specific styles to the desired columns
    styles["strike"] = "background-color: lightblue;"
    
    return styles

# Number of rows in the table (dynamic)
num_rows = st.slider("Number of rows", min_value=1, max_value=20, value=7)
ticker = st.text_input("Enter Ticker Symbol", placeholder="AAPL, TSLA, etc.")

dr = DataRetriever(ticker=ticker)
if ticker:
    stock_price = dr.getStockPrice()
    options_date, options_df = dr.getOptionsData()
    earnings_data = dr.getEarningsData()
else:
    stock_price = 0
    options_date, options_df = None, None
    earnings_data = None

st.subheader(f"Stock Price: ${stock_price}")  # Display stock price beside input

# # Placeholder for the table data
# data = {"Delta $": [0] * num_rows, "Delta %": [0] * num_rows, "% to Points": [0] * num_rows}

# # Creating the dynamic table
# for i in range(num_rows):
#     col1, col2 = st.columns(2)
    
#     # Input A and Input B
#     data["Delta $"][i] = col1.number_input(f"{i+1}Q - $ Delta", key=f"input_a_{i}", format="%0.5f")
#     data["Delta %"][i] = col2.number_input(f"{i+1}Q - % Delta", key=f"input_b_{i}", format="%0.5f")
    
#     # # Output C (dynamic value based on Input A and Input B)
#     # data["Output C"][i] = data["Input A"][i] + data["Input B"][i]  # Example logic
#     # col3.write(f"{data['Output C'][i]}")  # Display Output C
#     data["% to Points"][i] = (data["Delta %"][i] * stock_price)

# # Convert to DataFrame and display
# df = pd.DataFrame(data)
# st.write("Final Table:")
# st.dataframe(df, use_container_width=True)

if earnings_data is not None:
    # Convert the data into a DataFrame
    df = pd.DataFrame(earnings_data)

    # Optional: Format the percentPriceChange column to show percentages
    df['percentPriceChange'] = df['percentPriceChange'].apply(lambda x: f"{x}%")

    # Display the DataFrame as a table in Streamlit
    st.write("Earnings Report Table:")
    st.dataframe(df, use_container_width=True)

if options_df is not None:
    st.subheader(f"Displaying options data for: {options_date}")

    # Group the DataFrame by expiration
    grouped = options_df.groupby("expiration")

    # Iterate through each group and apply the highlighter
    for expiration_date, group in grouped:
        # Apply styling to the group
        styled_group = group.style.apply(optionsDFHighlighter, axis=None)

        # Use an expander for each expiration group
        with st.expander(f"Expiration: {expiration_date}", expanded=False):
            # Display the styled DataFrame
            st.dataframe(styled_group, use_container_width=True)