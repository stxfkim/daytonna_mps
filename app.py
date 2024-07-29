import streamlit as st
import pandas as pd



pg = st.navigation([
    st.Page("pages/main.py", title="Home"),
    st.Page("pages/view_payroll.py", title="Slip Bayangan")
])
pg.run()

hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


