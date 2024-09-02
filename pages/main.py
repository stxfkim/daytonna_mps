import streamlit as st
import pandas as pd
import datetime
from datetime import date
from pathlib import Path
import zipfile
import warnings
import os
#from functions import *

st.set_page_config(
    initial_sidebar_state="expanded",
    page_title="Mini Payroll System"
)

from funcs.input_data import input_data
from funcs.sidebar_menu import sidebar_menu
from funcs.login import login
from funcs.salary_calc import salary_calc
from funcs.working_hours_calc import working_hours_calc, time_adjustment
from funcs.tax_calc import tax_calc
from funcs.gen_payslip import generate_payslip
from funcs.gen_report import report_by_project,generate_report
from funcs.utils import *

warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from openpyxl.styles.alignment import Alignment



if login():
    
    # page config
    #st.set_page_config(page_title="Daytonna - Mini Payroll System", layout="wide")
    
    # side bar with input of excel files & dates
    attendance_data, start_date, end_date, employee_master, holidays_date = sidebar_menu()
    
    # main tabs
    input_data_tab, salary_calc_tab = st.tabs(
        ["Input Data ", "Hitung Gaji"]
    )
    
    # input_data_tab, salary_calc_tab, generate_report_tab = st.tabs(
    #     ["Input Data ", "Hitung Gaji", "Generate Report"]
    # )
    
    with input_data_tab:
        st.write("#### Data Absensi")

        attendance_data_df, employee_master_df, holidays_date_df = input_data(attendance_data,
                                                                              employee_master,
                                                                              holidays_date)
        

        

    with salary_calc_tab:

        col_btnSalaryCalc, col_btnDownloadSlip, col_btnDownloadReport = st.columns(3)
        is_attendance_empty =  (lambda x: True if x is None else x.empty)(attendance_data_df)
        if is_attendance_empty: st.warning("Data Absensi belum di-upload",icon="⚠️")
        with col_btnSalaryCalc:
            
            btnSalaryCalc = st.button(
                    "Hitung Gaji", help="klik tombol untuk hitung gaji",
                    type="primary", disabled=is_attendance_empty
                )
            
  
        detail_salary_df = None
        summary_salary_df = None
        working_hours_df = None
        file_output = ''
        periode = None
        project_report_df = None
        
        if btnSalaryCalc:
            with st.spinner('Processing...'):

            
                # Generate Jam Kerja
                attendance_data_adjusted = time_adjustment(attendance_data_df,employee_master_df)
            
                working_hours_df = working_hours_calc(attendance_data_adjusted,holidays_date_df,employee_master_df,start_date, end_date)

                st.session_state['working_hours_df'] = working_hours_df
                # st.markdown("#### Rincian Total Jam Kerja")
                # st.dataframe(working_hours_df,use_container_width=True)
                
                # Slip bayangan
                slip_bayangan_df = working_hours_df[['nik','nama','tanggal','jam_mulai','jam_akhir','billable_hours']]
                slip_bayangan_df.columns = ['nik','nama','tanggal','jam_mulai','jam_akhir','total_jam']
                slip_bayangan_df.to_csv("temp_data/temp_slip_bayangan.csv",index=None)
                


                #generate data gaji         
                detail_salary_df,summary_salary_df = salary_calc(working_hours_df,employee_master_df)


                # Store the dataframes to display later
                st.session_state['detail_salary_df'] = detail_salary_df
                st.session_state['summary_salary_df'] = summary_salary_df
                # st.markdown("#### Summary Gaji")  
                # summary_salary_df            
                
                # st.markdown("#### Detail Gaji")  
                # detail_salary_df
                
                
                # generate payslips
                periode = get_periode(start_date,end_date)
                path_output = generate_payslip(working_hours_df,summary_salary_df,detail_salary_df,periode)
                st.session_state['file_output'] = path_output
                
                project_report_df = report_by_project(detail_salary_df)
                project_report_output = generate_report(project_report_df,periode)
                st.session_state['project_report_output'] = project_report_output
                
                
                st.session_state['project_report_df'] = project_report_df

        # Display the dataframes if they exist
        if 'working_hours_df' in st.session_state:
            st.markdown("#### Rincian Total Jam Kerja")
            st.dataframe(st.session_state['working_hours_df'], use_container_width=True)

        if 'summary_salary_df' in st.session_state:
            st.markdown("#### Summary Gaji")
            st.dataframe(st.session_state['summary_salary_df'])

        if 'detail_salary_df' in st.session_state:
            st.markdown("#### Detail Gaji")
            st.dataframe(st.session_state['detail_salary_df'])
            
        if 'project_report_df' in st.session_state:
            st.markdown("#### Project Report")
            st.dataframe(st.session_state['project_report_df'])


            
        with col_btnDownloadSlip:
            if 'file_output' in st.session_state and os.path.exists(st.session_state['file_output']):
                periode = get_periode(start_date, end_date)
                filename = 'report_' + periode.replace(' ', '_') + ".xlsx"

                with open(st.session_state['file_output'], 'rb') as file:
                    file_data = file.read()

                st.download_button(
                    label="Download Slip Gaji",
                    data=file_data,
                    file_name=filename,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        with col_btnDownloadReport:
            if 'project_report_output' in st.session_state and os.path.exists(st.session_state['project_report_output']):
                periode = get_periode(start_date, end_date)
                filename = 'report_project_' + periode.replace(' ', '_') + ".xlsx"

                with open(st.session_state['project_report_output'], 'rb') as file:
                    file_data = file.read()

                st.download_button(
                    label="Download Report Project",
                    data=file_data,
                    file_name=filename,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                


    # with generate_report_tab:
    #     btnTest = st.button(
    #                 "Hitung Jam", help="klik tombol untuk hitung gaji",
    #                 type="primary", disabled=is_attendance_empty
    #             )
    #     if btnTest:
    #         att_data  = time_adjustment(attendance_data_df,employee_master_df)
    
    #         st.dataframe(att_data,use_container_width=True)

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


