import streamlit as st

pg = st.navigation([st.Page("pages/home.py"), st.Page("pages/auto_screener.py"), st.Page("pages/stock_details.py")])
pg.run()