import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import openpyxl
import streamlit as st
from pathlib import Path


def generate_payslip(working_hours_df,summary_salary_df,periode):
    
    working_hours_df['sheet_name'] = working_hours_df['nik'] + "_" +working_hours_df["nama"].replace(
            " ", "_", regex=True)
    
    working_hours_df['jam_mulai'] = working_hours_df['jam_mulai'].dt.strftime('%H:%M')
    working_hours_df['jam_akhir'] = working_hours_df['jam_akhir'].dt.strftime('%H:%M')
    
    wb = openpyxl.load_workbook(Path('template/template_slipgaji.xlsx'))
    sheetname_list = summary_salary_df['sheet_name'].unique()
    
    filename = periode.replace(" ", "_")
    
    file_output = Path('output/slipgaji_'+filename+".xlsx")
    
    for sheetname in sheetname_list:
        #st.write(sheetname)
        tmp_detail = working_hours_df[working_hours_df['sheet_name']==str(sheetname)]
        tmp_summary = summary_salary_df[summary_salary_df['sheet_name']==str(sheetname)]
        
        sheet = wb.copy_worksheet(wb.active)
        sheet.title = sheetname

        start_row = 5
        start_col = 1  # Column A
        # Write detail working hours
        tmp_detail_table = tmp_detail[['tanggal','jam_mulai', 'jam_akhir','billable_hours']]
        for r_idx, row in enumerate(dataframe_to_rows(tmp_detail_table, index=False, header=False), start=start_row):
            for c_idx, value in enumerate(row, start=start_col):
                sheet.cell(row=r_idx, column=c_idx, value=value)

        # B42 : Name 
        sheet['B42'].value = tmp_summary['nama'].iloc[0]         
        
        # H4 : Employee Number
        sheet['H4'].value = tmp_summary['nik'].iloc[0]
        # H5 : Name 
        sheet['H5'].value = tmp_summary['nama'].iloc[0] 
        # H6 : Jabatan 
        sheet['H6'].value = tmp_summary['jabatan'].iloc[0] 
        # H7 : Status Keluarga 
        sheet['H7'].value = tmp_summary['status_pajak'].iloc[0] 
        # H8 : NPWP 
        sheet['H8'].value = tmp_summary['npwp'].iloc[0] 
        # H9 : Periode Gaji 
        sheet['H9'].value = periode
        # H11 : Total Jam Kerja 
        sheet['H11'].value = tmp_summary['monthly_billable_hours'].iloc[0]  
        
        # H9 : Periode Gaji 
        sheet['I14'].value = tmp_summary['basic_salary'].iloc[0]
        # H11 : Total Jam Kerja 
        sheet['I15'].value = tmp_summary['uang_makan'].iloc[0]          

        # G14 : Makan & Transport 
        sheet['G14'].value = tmp_summary['monthly_billable_hours'].iloc[0]   
        # G15 : Makan & Transport 
        sheet['G15'].value = tmp_summary['total_meal_days'].iloc[0]  
        # K23 : BPJSTK 
        sheet['K23'].value = tmp_summary['bpjstk_deduction'].iloc[0]  
        # K24 : Pajak
        sheet['K24'].value = tmp_summary['tax_deduction'].iloc[0]  
        
        
    sheet_to_delete = wb['tmp']
    wb.remove(sheet_to_delete)    
    wb.save(file_output)
    