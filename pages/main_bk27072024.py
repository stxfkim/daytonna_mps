import streamlit as st
import pandas as pd
import datetime
from datetime import date
from pathlib import Path
import zipfile
import warnings
#from functions import *

st.set_page_config(
    initial_sidebar_state="expanded"
)

from funcs.input_data import input_data
from funcs.sidebar_menu import sidebar_menu
from funcs.login import login
from funcs.salary_calc import salary_calc
from funcs.working_hours_calc import working_hours_calc
from funcs.tax_calc import tax_calc

warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from openpyxl.styles.alignment import Alignment



if login():
    
    # page config
    #st.set_page_config(page_title="Daytonna - Mini Payroll System", layout="wide")
    
    # side bar with input of excel files & dates
    attendance_data, start_date, end_date, employee_master, holidays_date = sidebar_menu()
    
    # main tabs
    input_data_tab, working_hours_calc_tab,salary_calc_tab, generate_report_tab = st.tabs(
        ["Input Data ", "Hitung Jam Kerja" , "Hitung Gaji", "Generate Report"]
    )
    
    with input_data_tab:
        st.write("#### Data Absensi")

        attendance_data_df, employee_master_df, holidays_date_df = input_data(attendance_data,
                                                                              employee_master,
                                                                              holidays_date)

    with working_hours_calc_tab:

        is_attendance_empty =  (lambda x: True if x is None else x.empty)(attendance_data_df)
        if is_attendance_empty: st.warning("Data Absensi belum di-upload",icon="⚠️")
        btnWorkingHoursCalc = st.button(
                "Hitung Jam Kerja", help="klik tombol untuk hitung jam kerja",
                type="primary", disabled=is_attendance_empty
            )
        

        working_hours_df = None
        if btnWorkingHoursCalc:
            
            attendance_data_df['tanggal'] = pd.to_datetime(attendance_data_df['tanggal']).dt.date

            filtered_attendance_df = attendance_data_df[
                    attendance_data_df["tanggal"].between(start_date, end_date)
                ]
            working_hours_df = working_hours_calc(filtered_attendance_df,holidays_date_df)
            st.dataframe(working_hours_df,use_container_width=True)
            working_hours_df.to_csv("temp_data/temp_working_hours.csv",index=None)
            #simpan file slip bayangan untuk ditampilkan di page Slip Bayangan
            slip_bayangan_df = working_hours_df[['nik','nama','tanggal','jam_mulai','jam_akhir','billable_hours']]
            slip_bayangan_df.columns = ['nik','nama','tanggal','jam_mulai','jam_akhir','total_jam']
            slip_bayangan_df.to_csv("temp_data/temp_slip_bayangan.csv",index=None)
            
            
    with salary_calc_tab:
        is_working_hours_df_empty =  (lambda x: True if x is None else x.empty)(working_hours_df)
        if is_working_hours_df_empty: st.warning("Data Jam Kerja belum tersedia",icon="⚠️")
        btnSalaryCalc = st.button(
                "Hitung Gaji", help="klik tombol untuk hitung gaji",
                type="primary", disabled=is_working_hours_df_empty
            )
        if btnSalaryCalc:
            st.write("hitung gajiiiiiii")

        ter_mapping_detail_df = tax_calc()

        ter_mapping_detail_df

        


    with generate_report_tab:
        st.write("blank")
        st.__version__
 

font_css = """
    <style>
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
    font-size: 20px;
    font-weight: bold;
    margin-top: 0%;
    }

   button[data-baseweb="tab"] {
   font-size: 20px;
   margin: 0;
   width: 100%;
   margin-top: 0%;
   }
   
    #MainMenu {visibility: hidden;}

    """

st.markdown(font_css, unsafe_allow_html=True)


