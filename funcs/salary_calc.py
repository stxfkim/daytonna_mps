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
import zipfile

#from functions import *


def bpjstk_deduction_calc(df):
    # Define the deduction based on the monthly_billable_salary column
    df['bpjstk_deduction'] = df['monthly_billable_salary'].apply(
        lambda x: 0 if x <= 1000000 else
                  40000 if x <= 3000000 else
                  62000 if x <= 5000000 else
                  90000
    )
    return df
    
    

def salary_calc(working_hours_df,employee_master_df):

    #Hitung Gaji Harian
    tmp_working_hours = working_hours_df[['nik','tanggal','billable_hours']]
    tmp_working_hours.columns = ['nik_wh','tanggal','billable_hours']
    tmp_working_hours['nik_wh'] = tmp_working_hours['nik_wh'].astype(str)
    tmp_salary_df = employee_master_df.merge(
            tmp_working_hours,
            left_on="nik",
            right_on="nik_wh",
            how="inner"
        )
    
    #drop table yg engga perlu
    tmp_salary_df = tmp_salary_df.drop(
            columns=["jenis_kelamin",'status_kawin','status_pajak','nik_wh']
        )
    
    #hitung gaji dari billable_hours * basic salary (daily level)
    tmp_salary_df['billable_salary'] = tmp_salary_df['billable_hours']*tmp_salary_df['basic_salary']
    
    #agregat monthly uang makan
    tmp_monthly_meal_allowance = (
            tmp_salary_df.groupby("nik")
            .agg({"uang_makan": "sum"})
            .rename(columns={"uang_makan": "monthly_meal_allowance"})
            .reset_index()
        )
    tmp_monthly_meal_allowance.columns = ['nik_tmp','monthly_meal_allowance']

    #agregat monthly salary from total daily salary
    tmp_monthly_salary = (
            tmp_salary_df.groupby("nik")
            .agg({"billable_salary": "sum"})
            .rename(columns={"billable_salary": "monthly_billable_salary"})
            .reset_index()
        )
    # join dengan monthly salary
    tmp_monthly_salary.columns = ['nik_tmp','monthly_billable_salary']
    tmp_salary_df = tmp_salary_df.merge(
            tmp_monthly_salary,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    tmp_salary_df = tmp_salary_df.drop(
            columns=["nik_tmp"]
        )
    
    #join dengan monthly meal allowance
    tmp_salary_df = tmp_salary_df.merge(
            tmp_monthly_meal_allowance,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    tmp_salary_df = tmp_salary_df.drop(
            columns=["nik_tmp"]
        ) 
    salary_df = bpjstk_deduction_calc(tmp_salary_df)
    return salary_df