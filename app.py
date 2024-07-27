import streamlit as st
import pandas as pd



pg = st.navigation([
    st.Page("pages/main.py", title="Home"),
    st.Page("pages/view_payroll.py", title="Slip Bayangan")
])
pg.run()




