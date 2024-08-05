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
from funcs.tax_calc import tax_calc

#from functions import *


def bpjstk_deduction_calc(df):
    # Define the deduction based on the monthly_billable_salary column
    df['bpjstk_deduction'] = df['monthly_billable_salary'].apply(
        lambda x: 0 if x <= 1000000 else
                  40000 if x <= 3000000 else
                  62000 if x <= 5000000 else
                  90010
    )
    return df
    
    

def salary_calc(working_hours_df,employee_master_df):

    #Hitung Gaji Harian
    tmp_working_hours = working_hours_df[['nik','tanggal','billable_hours']]
    tmp_working_hours.columns = ['nik_wh','tanggal','billable_hours']
    tmp_working_hours['nik_wh'] = tmp_working_hours['nik_wh'].astype(str)
    detail_salary_df = employee_master_df.merge(
            tmp_working_hours,
            left_on="nik",
            right_on="nik_wh",
            how="inner"
        )
    
    #drop table yg engga perlu
    detail_salary_df = detail_salary_df.drop(
            columns=["jenis_kelamin",'status_kawin','nik_wh']
        )
    
    #hitung gaji dari billable_hours * basic salary (daily level)
    detail_salary_df['billable_salary'] = detail_salary_df['billable_hours']*detail_salary_df['basic_salary']
    
    #agregat monthly uang makan
    detail_salary_df['billable_meal_allowance'] = detail_salary_df.apply(
        lambda row: row['uang_makan'] if row['billable_hours'] >= 5 else 0,
        axis=1
    )
    
    #total hari uang makan
    detail_salary_df['is_meal_allowance'] = detail_salary_df.apply(
        lambda row: 1 if row['billable_hours'] >= 5 else 0,
        axis=1
    )

   # Aggregate the 'is_meal_allowance' by 'nik'
    tmp_total_meal_days = (
        detail_salary_df.groupby("nik")
        .agg({"is_meal_allowance": "sum"})
        .rename(columns={"is_meal_allowance": "total_meal_days"})
        .reset_index()
    )    
    tmp_total_meal_days.columns = ['nik_tmp','total_meal_days']
    

    #join dengan monthly meal allowance
    detail_salary_df = detail_salary_df.merge(
            tmp_total_meal_days,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    detail_salary_df = detail_salary_df.drop(
            columns=["nik_tmp"]
        ) 
    
    #total hari uang makan
    detail_salary_df['is_meal_allowance'] = detail_salary_df.apply(
        lambda row: 1 if row['billable_hours'] >= 5 else 0,
        axis=1
    )
        
#START
    # Aggregate the '' by 'nik'
    tmp_monthly_meal_allowance = (
        detail_salary_df.groupby("nik")
        .agg({"billable_meal_allowance": "sum"})
        .rename(columns={"billable_meal_allowance": "monthly_meal_allowance"})
        .reset_index()
    )    
    tmp_monthly_meal_allowance.columns = ['nik_tmp','monthly_meal_allowance']

    #join dengan monthly meal allowance
    detail_salary_df = detail_salary_df.merge(
            tmp_monthly_meal_allowance,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    detail_salary_df = detail_salary_df.drop(
            columns=["nik_tmp"]
        ) 


# END NEW
    # Aggregate the 'billable_meal_allowance' by 'nik'
    tmp_monthly_billable_hours = (
        detail_salary_df.groupby("nik")
        .agg({"billable_hours": "sum"})
        .rename(columns={"billable_hours": "monthly_billable_hours"})
        .reset_index()
    )    
    tmp_monthly_billable_hours.columns = ['nik_tmp','monthly_billable_hours']

    #join dengan monthly meal allowance
    detail_salary_df = detail_salary_df.merge(
            tmp_monthly_billable_hours,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    detail_salary_df = detail_salary_df.drop(
            columns=["nik_tmp"]
        ) 

    #agregat monthly salary from total daily salary
    tmp_monthly_salary = (
            detail_salary_df.groupby("nik")
            .agg({"billable_salary": "sum"})
            .rename(columns={"billable_salary": "monthly_billable_salary"})
            .reset_index()
        )
    # join dengan monthly salary
    tmp_monthly_salary.columns = ['nik_tmp','monthly_billable_salary']
    detail_salary_df = detail_salary_df.merge(
            tmp_monthly_salary,
            left_on="nik",
            right_on="nik_tmp",
            how="inner"
        )
    detail_salary_df = detail_salary_df.drop(
            columns=["nik_tmp"]
        )
    


    detail_salary_df['gross_salary'] = detail_salary_df['monthly_billable_salary']+detail_salary_df['monthly_meal_allowance']
    
    detail_salary_df = bpjstk_deduction_calc(detail_salary_df)

    detail_salary_df['tax_percentage'] = detail_salary_df['gross_salary'].apply(lambda x: tax_calc(x))

    # lanjut 
    # hitung tax_deduction amount (gross_salary*tax_percentage)
    detail_salary_df['tax_deduction'] = (detail_salary_df['gross_salary']*detail_salary_df['tax_percentage']).round(0)
    # hitung net_salary (gross_salary-(bpjstk_deduction+tax_deduction))
    detail_salary_df['net_salary'] = detail_salary_df['gross_salary']-(detail_salary_df['bpjstk_deduction']+detail_salary_df['tax_deduction'])
    
    detail_salary_df['sheet_name'] = detail_salary_df['nik'] + "_" +detail_salary_df["nama"].replace(
            " ", "_", regex=True)
    
    
    
    summary_salary_columns = [
    'nik', 'nama', 'norek', 'npwp', 'jabatan','status_pajak',
    'uang_makan', 'basic_salary', 'monthly_billable_hours' ,'total_meal_days',
    'monthly_meal_allowance', 'monthly_billable_salary',
    'gross_salary', 'bpjstk_deduction', 'tax_deduction',
    'net_salary','sheet_name']
    tmp_salary_df = detail_salary_df[summary_salary_columns]


    # Drop duplicates based on 'nik' and keep the first occurrence
    summary_salary_df = tmp_salary_df.drop_duplicates(subset='nik').reset_index(drop=True)
    
    
    
    
    
    return detail_salary_df, summary_salary_df