import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from pathlib import Path


def billable_hours_rounding(row):
    if pd.isna(row['billable_hours']):  # Check if the value is NaN
        return 0
    else:
        return np.floor(row['billable_hours']) + (0.5 if row['billable_hours'] % 1 >= 0.5 else 0.0)

def adjust_jam_mulai(row):
        # Extract hour and minute from 'jam_mulai_real'
    hour = row['jam_mulai_real'].hour
    minute = row['jam_mulai_real'].minute
    
        # Conditions for 's.helper' or 'store helper'
    if row['jabatan'].lower() in ['s.helper', 'store helper', 'store']:
        if (hour == 7 and minute == 0) or hour < 7 and row['jam_mulai_real'].strftime("%H:%M:%S") != '00:00:00':
            return pd.Timestamp('07:00').time()
    else:
        # Conditions for other jobs
        if (hour == 7 and minute <= 35) or hour < 7 and row['jam_mulai_real'].strftime("%H:%M:%S") != '00:00:00':
            return pd.Timestamp('07:30').time()
        
    
    # Default to jam_mulai_real if no condition matches
    return row['jam_mulai_real']


def late_hour_pinalty(row):
    
    time = row['jam_mulai_real'].strftime('%H:%M')
    timestamp = pd.to_datetime(row['tanggal'] + ' ' + time)
    
    
    # Convert reference times to timestamps for comparison
    morning_cutoff = pd.to_datetime(row['tanggal'] + ' 07:06')
    morning_non_store_cutoff = pd.to_datetime(row['tanggal'] + ' 07:36')
    afternoon_cutoff = pd.to_datetime(row['tanggal'] + ' 13:00')
    afternoon_start = pd.to_datetime(row['tanggal'] + ' 13:06')
    
    if row['jabatan'].lower() in ['s.helper', 'store helper', 'store']:
        # Check the conditions for 'store'
        if morning_cutoff <= timestamp <= afternoon_cutoff:
            return 1
        elif timestamp >= afternoon_start:
            return 1
    else:
        # Check the conditions for non-'store'
        if morning_non_store_cutoff < timestamp < afternoon_cutoff:
            return 1
        elif timestamp >= afternoon_start:
            return 1
    
    # No penalty
    return 0

def rounding_jam_finger(time_str):
    """Replace minutes based on the given conditions."""
    # Split the time into hours and minutes
    hours, mins = time_str.split(':')
    mins = int(mins)
    
    # Adjust minutes based on the condition
    if 1 <= mins <= 29:
        return f'{hours}:00'
    elif 30 <= mins <= 59:
        return f'{hours}:30'
    else:
        return time_str

def time_adjustment(attendance_data_df,employee_master_df):
    
    att_data = attendance_data_df[['nik','nama','tanggal','jam_mulai','jam_akhir','project']]
    att_data.columns = ['nik','nama','tanggal','jam_mulai_real','jam_akhir_real','project']
    
    emp_data = employee_master_df[['nik','jabatan']]
    emp_data.columns = ['nik_emp','jabatan']
    
     
    att_data_final = att_data.merge(
            emp_data,
            left_on='nik',
            right_on='nik_emp',
            how='inner'
        )
    
    #drop table yg engga perlu
    att_data_final = att_data_final.drop(
            columns=['nik_emp']
        )
    
    att_data_final['jam_mulai_real'] = pd.to_datetime(att_data_final['jam_mulai_real'], format='%H:%M').dt.time
    
    
    att_data_final['jam_mulai'] = att_data_final.apply(adjust_jam_mulai, axis=1)
    #print(att_data_final.info())
    att_data_final['late_hours'] = att_data_final.apply(late_hour_pinalty,axis=1)
    
    att_data_final['jam_mulai'] = att_data_final['jam_mulai'].apply(lambda x: x.strftime('%H:%M'))
    att_data_final['jam_mulai'] = att_data_final['jam_mulai'].apply(rounding_jam_finger)

    att_data_final['jam_akhir'] = att_data_final['jam_akhir_real'].apply(rounding_jam_finger)
       

    #att_data_final['jam_mulai'] = att_data_final['jam_mulai'].apply(lambda x: x.strftime('%H:%M'))
    #att_data_final['jam_akhir'] = att_data_final['jam_akhir'].apply(lambda x: x.strftime('%H:%M'))
    att_data_final['jam_mulai_real'] = att_data_final['jam_mulai_real'].apply(lambda x: x.strftime('%H:%M'))
    #att_data_final['jam_akhir_real'] = att_data_final['jam_akhir_real'].apply(lambda x: x.strftime('%H:%M'))


    return att_data_final
    

def breaks_hours(row):
    normal_break = pd.Timedelta(hours=1)
    friday_break = pd.Timedelta(hours=2)
    night_break = pd.Timedelta(hours=1)
    coffee_break = pd.Timedelta(minutes=30)
    
    start = row['jam_mulai']
    end = row['jam_akhir']
    
    total_breaks = pd.Timedelta(hours=0)
    
    if row['day'] in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Sabtu', 'Minggu']:  # Monday to Thursday and Sunday
        break_start = pd.to_datetime(str(start.date()) + ' 12:00')
        break_end = pd.to_datetime(str(start.date()) + ' 13:00')
        if start <= break_start < end:
            total_breaks += normal_break
        
        break_start_overtime = pd.to_datetime(str(start.date()) + ' 18:00')
        break_end_overtime = pd.to_datetime(str(start.date()) + ' 19:00')
        if (start <= break_start_overtime < end) and (break_end_overtime < end):
            total_breaks += normal_break
    elif row['day'] == 'Jumat':  # Friday
        break_start = pd.to_datetime(str(start.date()) + ' 11:30')
        break_end = pd.to_datetime(str(start.date()) + ' 13:30')
        if start <= break_start < end:
            total_breaks += friday_break
        break_start_overtime = pd.to_datetime(str(start.date()) + ' 18:00')
        break_end_overtime = pd.to_datetime(str(start.date()) + ' 19:00')
        if (start <= break_start_overtime < end) and (break_end_overtime < end):
            total_breaks += normal_break
    
    if row['jam_mulai'].hour >= 18 or row['jam_mulai'].hour < 6:  # Night shift
        night_break_start = pd.to_datetime(str(start.date()) + ' 23:00')
        night_break_end = pd.to_datetime(str(start.date()) + ' 00:00')
        coffee_break_start = pd.to_datetime(str(start.date()) + ' 03:30')
        coffee_break_end = pd.to_datetime(str(start.date()) + ' 04:00')
        
        if start <= night_break_start < end:
            total_breaks += night_break
        if coffee_break_start < end: 
            total_breaks += coffee_break

    return total_breaks.total_seconds() / 3600

def billable_hours_calc(row):
    if row['day'] in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'] and row['is_holiday'] == 'N' :
        # Shift Malam
        # 7 jam pertama 1x
        if row['total_working_hours'] <= 7:
            return row['total_working_hours']
        # 1 jam berikutnya 1.5x
        elif row['total_working_hours'] <= 8:
            return 7 + (row['total_working_hours'] - 7) * 1.5
        # jam berikutnya 2x
        else:
            return 7 + 1 * 1.5 + (row['total_working_hours'] - 8) * 2
            

    elif row['day'] == 'Sabtu' and row['is_holiday'] == 'N':
        # Shift Malam & Pagi/Normal Perhitungannya sama
        # 5 jam pertama 1x
        if row['total_working_hours'] <= 5:
            return row['total_working_hours']
        # 1 jam berikutnya 1.5x
        elif row['total_working_hours'] <= 6:
            return 5 + (row['total_working_hours'] - 5) * 1.5
        # jam berikutnya 2x
        else:
            return 5 + 1 * 1.5 + (row['total_working_hours'] - 6) * 2
    elif row['day'] == 'Minggu' or row['is_holiday'] == 'Y':  # Minggu & Libur
        # 7 jam pertama 2x
        if row['total_working_hours'] <= 7.5:
            return row['total_working_hours'] * 2
        # 1 jam berikutnya 3x
        elif row['total_working_hours'] <= 8:
            return 7 * 2 + (row['total_working_hours'] - 7) * 3
        # jam berikutnya 4x
        else:
            return 7 * 2 + 1 * 3 + (row['total_working_hours'] - 8) * 4
       


def working_hours_calc(attendance_data_df,holidays_date_df,employee_master_df,start_date, end_date): # attendance_data_df, start_date, end_date
    
    if attendance_data_df is None:
        st.warning("Data Absensi belum di-upload", icon="⚠️")
    else:
        # attendance_data_df = attendance_data_df[attendance_data_df["tanggal"].between(start_date, end_date)]
        

        attendance_data_df['tanggal'] = pd.to_datetime(attendance_data_df['tanggal'],format='%d/%m/%Y').dt.date

        attendance_data_df = attendance_data_df[
                    attendance_data_df["tanggal"].between(start_date, end_date)
                ]
        
        # attendance_data_df 
        # Function to round down to the nearest 10 minutes
        # def round_down_to_10min(dt):
        #     return dt - pd.to_timedelta(dt.minute % 10, unit='minutes')
        # attendance_data_df['jam_mulai'] = pd.to_datetime(attendance_data_df['jam_mulai'], format='%H:%M')
        # attendance_data_df['jam_akhir'] = pd.to_datetime(attendance_data_df['jam_akhir'], format='%H:%M')
        # # Apply the function
        # attendance_data_df['jam_mulai'] = attendance_data_df['jam_mulai'].apply(round_down_to_10min)
        # attendance_data_df['jam_akhir'] = attendance_data_df['jam_akhir'].apply(round_down_to_10min)
        
        # Convert 'tanggal', 'jam_mulai', and 'jam_akhir' columns to datetime
        attendance_data_df['tanggal'] = pd.to_datetime(attendance_data_df['tanggal'], format='%Y-%m-%d')
        attendance_data_df['jam_mulai'] = pd.to_datetime(attendance_data_df['jam_mulai'], format='%H:%M').dt.time
        attendance_data_df['jam_akhir'] = pd.to_datetime(attendance_data_df['jam_akhir'], format='%H:%M').dt.time
        # Convert to datetime

        # Replace NaT with '00:00:00' string
        attendance_data_df['jam_mulai'] = attendance_data_df['jam_mulai'].apply(lambda x: x.strftime('%H:%M') if not pd.isna(x) else '00:00')
        attendance_data_df['jam_akhir'] = attendance_data_df['jam_akhir'].apply(lambda x: x.strftime('%H:%M') if not pd.isna(x) else '00:00')
        # Combine 'tanggal' with 'jam_mulai' and 'jam_akhir' to create datetime columns
        attendance_data_df['jam_mulai'] = pd.to_datetime(attendance_data_df['tanggal'].astype(str) + ' ' + attendance_data_df['jam_mulai'].astype(str))
        attendance_data_df['jam_akhir'] = pd.to_datetime(attendance_data_df['tanggal'].astype(str) + ' ' + attendance_data_df['jam_akhir'].astype(str))

        # Adjust for end time being on the next day if needed
        attendance_data_df.loc[attendance_data_df['jam_akhir'] < attendance_data_df['jam_mulai'], 'jam_akhir'] += pd.Timedelta(days=1)

        # Calculate the working hours
        attendance_data_df['working_hours'] = (attendance_data_df['jam_akhir'] - attendance_data_df['jam_mulai']).dt.total_seconds() / 3600

        # Calculate the working hours per day
        attendance_data_df['tanggal'] = attendance_data_df['jam_mulai'].dt.date
        
        
     
        daily_working_hours = attendance_data_df.groupby(['nik', 'nama', 'tanggal','jam_mulai','jam_akhir'])['working_hours'].sum().reset_index()

        
        # Separate the working hours into hours and minutes
        daily_working_hours['working_hours'] = daily_working_hours['working_hours']#.apply(lambda x: divmod(x * 60, 60))
        # daily_working_hours['hours'] = daily_working_hours['working_hours'].apply(lambda x: int(x[0]))
        # daily_working_hours['minutes'] = daily_working_hours['working_hours'].apply(lambda x: int(x[1]))
        #daily_working_hours = daily_working_hours.drop(columns=['working_hours'])
        
        # Include data hari & ubah nama hari menjadi bahasa Indonesia
        daily_working_hours['day'] = daily_working_hours['jam_mulai'].dt.day_name()
        daily_working_hours['day'] = daily_working_hours['day'].replace({'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'})
        
        # Hitung total jam untuk istirahat & coffee break
        daily_working_hours['break_hours'] = daily_working_hours.apply(breaks_hours, axis=1)
        # Pengurangan working_hours-break_hours
        daily_working_hours['total_working_hours'] = daily_working_hours['working_hours'] - daily_working_hours['break_hours']
        
        ##start here
            # #get real fingerprint time
        att_data = attendance_data_df[['nik','tanggal','jabatan','jam_mulai_real','jam_akhir_real','project','late_hours']]
        att_data.columns = ['nik_tmp','tanggal_tmp','jabatan','jam_mulai_real','jam_akhir_real','project','late_hours']
        att_data["tanggal_tmp"] = pd.to_datetime(att_data["tanggal_tmp"],format='%d-%m-%Y')


        daily_working_hours["tanggal"] = pd.to_datetime(daily_working_hours["tanggal"],format='%Y-%m-%d')
        daily_working_hours = pd.merge(daily_working_hours,
                att_data,
                left_on=['nik','tanggal'],
                right_on=['nik_tmp','tanggal_tmp'],
                how='left'
            )
        

        
        daily_working_hours['tanggal'] = daily_working_hours['tanggal'].dt.strftime('%Y-%m-%d')
        
        daily_working_hours['total_working_hours'] = daily_working_hours['total_working_hours'] - daily_working_hours['late_hours']
        
        
        ##end here
        
        # convert tanggal type from object into datetime64[ns] before join with holiday_df
        daily_working_hours['tanggal'] = pd.to_datetime(daily_working_hours['tanggal'], format='%Y-%m-%d')
        daily_working_hours = daily_working_hours.merge(
                    holidays_date_df,
                    left_on="tanggal",
                    right_on="tanggal_libur",
                    how="left"
                )
        
        
        # Fill non holiday on keterangan_libur as Hari Kerja
        # check is_holiday Y or N
        daily_working_hours["is_holiday"] = (
                    daily_working_hours["tanggal"]
                    .isin(holidays_date_df["tanggal_libur"])
                    .apply(lambda x: "Y" if x else "N")
                )
        # Drop not used column
        daily_working_hours = daily_working_hours.drop(
                    columns=["tanggal_libur"]
                )
        
        #st.dataframe(daily_working_hours)
        # Hitung rate jam normal & jam lembur
        daily_working_hours['billable_hours'] = daily_working_hours.apply(billable_hours_calc, axis=1)
        
        daily_working_hours['billable_hours'] = daily_working_hours.apply(billable_hours_rounding, axis=1)
        

        
        
        # Formatting output data
        daily_working_hours['tanggal'] = daily_working_hours['tanggal'].astype(str)
       # daily_working_hours['jam_mulai'] = pd.to_datetime(daily_working_hours['jam_mulai'], format='%H:%M').dt.time
        #daily_working_hours['jam_akhir'] = pd.to_datetime(daily_working_hours['jam_akhir'], format='%H:%M').dt.time

        
        # get full name from employee data
        daily_working_hours = daily_working_hours.drop(
                columns=['nama']
            )

        emp_data = employee_master_df[['nik','nama']]
        emp_data.columns = ['nik_emp','nama']
        
        
        daily_working_hours = daily_working_hours.merge(
                emp_data,
                left_on='nik',
                right_on='nik_emp',
                how='inner'
            )
        
        #drop table yg engga perlu
        daily_working_hours = daily_working_hours.drop(
                columns=['nik_emp']
            )
        
        
       
    
        
        working_hours_output_df = daily_working_hours[['nik','nama','jabatan','project','tanggal','jam_mulai_real','jam_akhir_real', 'day', 'is_holiday', 
                                                       'keterangan_libur','jam_mulai', 'jam_akhir',
                                                       'working_hours','late_hours','break_hours','total_working_hours'
                                                       ,'billable_hours'
                                                       ]]
        

        return working_hours_output_df#,test
