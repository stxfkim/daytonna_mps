import pandas as pd
import numpy as np

def report_by_project(df):
    # Ensure the 'tanggal' column is in datetime format
    df['tanggal'] = pd.to_datetime(df['tanggal'], format='%Y-%m-%d')

    # Group by 'Project', 'nama', and 'jabatan' and pivot the table
    pivot_df = df.pivot_table(index=['project', 'nama', 'jabatan'], 
                              columns=df['tanggal'].dt.day, 
                              values='billable_hours', 
                              aggfunc='sum').reset_index()

    # Create a list of all days (1 to 31)
    all_days = [str(i) for i in range(1, 32)]
    
    # Reindex the pivot table to ensure all days are present
    pivot_df = pivot_df.reindex(columns=['project', 'nama', 'jabatan'] + list(range(1, 32)), fill_value=0)
    
    # Rename columns
    pivot_df.columns = ['project', 'nama', 'jabatan'] + all_days

    # Calculate the total working hours (TOTAL JAM KERJA)
    pivot_df['TOTAL JAM KERJA'] = pivot_df.loc[:, '1':'31'].sum(axis=1)

    # Calculate the total working days (TOTAL HARI KERJA)
    pivot_df['TOTAL HARI KERJA'] = (pivot_df.loc[:, '1':'31'] > 0).sum(axis=1)

    # Calculate meal allowance (UANG MAKAN)
    uang_makan = df['uang_makan'].iloc[0]
    basic_salary = df['basic_salary'].iloc[0]
    pivot_df['BASIC/JAM'] = basic_salary
    pivot_df['UANG MAKAN'] = uang_makan

    pivot_df['TOTAL UANG MAKAN'] = uang_makan * pivot_df['TOTAL HARI KERJA']

    # Calculate basic salary per hour (BASIC/JAM)


    # Calculate total basic salary (TOTAL BASIC)
    pivot_df['TOTAL BASIC'] = pivot_df['TOTAL JAM KERJA'] * pivot_df['BASIC/JAM']

    # Calculate subtotal (SUB TOTAL)
    pivot_df['SUB TOTAL'] = pivot_df['TOTAL BASIC'] + pivot_df['UANG MAKAN']

    # Select and order the columns for the final DataFrame
    final_df = pivot_df[['project', 'nama', 'jabatan'] + all_days + 
                        ['TOTAL JAM KERJA', 'TOTAL HARI KERJA', 'UANG MAKAN', 
                         'BASIC/JAM','TOTAL UANG MAKAN', 'TOTAL BASIC', 'SUB TOTAL']]

    
    final_df.to_excel("output/report_project.xlsx",index=0)
    
    return final_df
