import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import warnings
warnings.filterwarnings('ignore')
from openpyxl import load_workbook
from openpyxl.styles.alignment import Alignment
import streamlit as st
from pathlib import Path


def sidebar_menu():
    with st.sidebar:
        #    st.sidebar.title(":abacus: Mini Payroll System")

        attendance_data = st.sidebar.file_uploader(
            "**Upload Data Absensi**", type=["xlsx", "xls"]
        )
        if attendance_data is not None:
            attendance_data_df = pd.read_excel(attendance_data,engine='xlrd', dtype={"nik": str})
            attendance_data_df.columns = attendance_data_df.columns.str.lower()
            attendance_data_df['tanggal'] = pd.to_datetime(attendance_data_df['tanggal']).dt.date

            min_date = attendance_data_df['tanggal'].min()
            max_date = attendance_data_df['tanggal'].max()
            st.write(attendance_data_df['tanggal'].min(),"-",attendance_data_df['tanggal'].max())

        else:
            min_date = date.today()
            max_date = date.today()

        start_date = st.date_input("**Start Date**", min_date,
                                   min_value=min_date,
                                   max_value=max_date)
        
        end_date = st.date_input("**End Date**", max_date,
                                   min_value=min_date,
                                   max_value=max_date)
        st.markdown("""---""")
        
        
        employee_master = st.sidebar.file_uploader(
            "**Upload Master Data Pegawai**", type=["xlsx", "xls"]
        )
        holidays_date = st.sidebar.file_uploader(
            "**Upload Data Libur & Cuti Bersama**", type=["xlsx", "xls"]
        )

        st.markdown("""---""")

        if st.button("Log out"):
            st.session_state.password_correct = False
            st.rerun()

        

                
    return attendance_data, start_date, end_date, employee_master, holidays_date
