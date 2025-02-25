import streamlit as st

contract_price = st.number_input("Enter the contract price", value=0.0, format="%.5f")
vega = st.number_input("Enter the vega", value=0.0, format="%.5f")
theta = st.number_input("Enter the theta", value=0.0, format="%.5f")
current_iv = st.number_input("Enter the current IV", value=0.0, format="%.5f")
predicted_iv = st.number_input("Enter the predicted IV", value=0.0, format="%.5f")

if contract_price and vega and theta and current_iv and predicted_iv:
    # Calculate the value based on the inputs
    value = contract_price - theta - (vega * (current_iv - predicted_iv))
    st.write(f"Calculated Value: {value}")






