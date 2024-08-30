import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import warnings
warnings.filterwarnings("ignore")
from openpyxl import load_workbook
from openpyxl.styles.alignment import Alignment
import streamlit as st
from pathlib import Path
import zipfile

def tax_calc(gross_salary, ter_type):

    # ter_mapping_df = pd.DataFrame({
    #     'tax_status': [
    #         'LTK0',  'LTK1', 'LK0', 'LTK2', 'LTK3',  'LK1',  'LK2',  'LK3',
    #         'PTK0', 'PTK1',  'PK0', 'PTK2',  'PTK3',  'PK1',  'PK2', 'PK3'
    #     ],
    #     'ter_type': [
    #         'TER_A', 'TER_A', 'TER_A', 'TER_B', 'TER_B', 'TER_B', 'TER_B', 'TER_C',
    #         'TER_A', 'TER_A', 'TER_A', 'TER_B', 'TER_B', 'TER_A', 'TER_A', 'TER_A'
    #     ]
    # })

    # ter_mapping_df.to_csv('temp_data/ter_mapping.csv', index=None)


    # Define the data as lists
    ter_mapping_detail_df = pd.read_csv('temp_data/ter_detail_mapping.csv')


    # Find the row where the gross_salary fits within the salary range
    # match = ter_mapping_detail_df[(ter_mapping_detail_df['min_salary'] <= gross_salary) & 
    #                               (ter_mapping_detail_df['max_salary'] >= gross_salary)]
    # if not match.empty:
    #     return match.iloc[0]['ter_percentage']
    # else:
    #     return None
    
    

    match = ter_mapping_detail_df[
        (ter_mapping_detail_df['ter_type'] == ter_type) &
        (ter_mapping_detail_df['min_salary'] <= gross_salary) &
        (ter_mapping_detail_df['max_salary'] >= gross_salary)
    ]
    if not match.empty:
        return match.iloc[0]['ter_percentage']
    else:
        return None