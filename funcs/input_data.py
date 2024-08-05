import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from pathlib import Path

def input_data(attendance_data,employee_master,holidays_date):
    
    ter_mapping = pd.read_csv('temp_data/ter_mapping.csv')
    #st.write(ter_mapping)
    
    # file absensi
    attendance_data_df = None
    if attendance_data is not None:
            attendance_data_df = pd.read_excel(attendance_data,engine='xlrd', dtype={"nik": str})
            attendance_data_df.columns = attendance_data_df.columns.str.lower()
            attendance_data_df["tanggal"] = pd.to_datetime(attendance_data_df["tanggal"],format='%d/%m/%Y')
            attendance_data_df['tanggal'] = attendance_data_df['tanggal'].dt.strftime('%d/%m/%Y')
            attendance_data_df['nik'] = attendance_data_df['nik'].astype(str)
           
            st.write(attendance_data_df)
    else:
        st.warning("Data Absensi belum di-upload", icon="⚠️")
    
    # file data pekerja
    emp_master_last_updated = Path("temp_data/emp_master_last_updated.txt").read_text()
    st.write("#### Data Master Pegawai")
    st.write("last update:", emp_master_last_updated)
    employee_master_df = None
    if employee_master is not None:
        employee_master_df = pd.read_excel(
        employee_master, dtype={"nik": str})
        employee_master_df['status_pajak'] = employee_master_df['jenis_kelamin']+employee_master_df['status_kawin']
        employee_master_df = employee_master_df.merge(
                    ter_mapping,
                    left_on="status_pajak",
                    right_on="tax_status",
                    how="inner",
                )
        employee_master_df = employee_master_df.drop(columns=['tax_status'])
        employee_master_df['nik'] = employee_master_df['nik'].astype('str')


        employee_master_df.to_csv("temp_data/temp_employee_master.csv", index=None)
        f = open("temp_data/emp_master_last_updated.txt", "w")
        f.write(str(datetime.now().strftime("%Y-%m-%d %H:%M")))
        f.close()
        st.write(employee_master_df)
    else:
        my_file = Path("temp_data/temp_employee_master.csv")
        if my_file.is_file():
            employee_master_df = pd.read_csv(my_file, dtype={"nik": str})            
            st.write(employee_master_df)
        else:
            st.warning("Data Master Pegawai belum di-upload", icon="⚠️")

    # file libur & cuti bersama
    holidays_date_last_updated = Path("temp_data/holidays_date_last_updated.txt").read_text()
    st.write("#### Data Libur & Cuti Bersama")
    st.write("last update:", holidays_date_last_updated)
    holidays_date_df = None
    if holidays_date is not None:
        holidays_date_df = pd.read_excel(holidays_date)
        holidays_date_df['tanggal_libur'] = pd.to_datetime(holidays_date_df['tanggal_libur'], format='%Y-%m-%d')        
        holidays_date_df.to_csv("temp_data/temp_holidays_date.csv", index=None)
        f = open("temp_data/holidays_date_last_updated.txt", "w")
        f.write(str(datetime.now().strftime("%Y-%m-%d %H:%M")))
        f.close()
        #st.write(holidays_date_df)
    else:
            my_file = Path("temp_data/temp_holidays_date.csv")
            if my_file.is_file():
                holidays_date_df = pd.read_csv(my_file)
                holidays_date_df['tanggal_libur'] = pd.to_datetime(holidays_date_df['tanggal_libur'], format='%Y-%m-%d') 
                st.write(holidays_date_df)
            else:
                st.warning("Data Libur & Cuti Bersama belum di-upload", icon="⚠️")
    return attendance_data_df, employee_master_df, holidays_date_df
