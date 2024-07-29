import streamlit as st
import pandas as pd



pg = st.navigation([
    st.Page("pages/main.py", title="Home"),
    st.Page("pages/view_payroll.py", title="Slip Bayangan")
])
pg.run()

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


