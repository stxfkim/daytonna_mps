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


def salary_calc(attendance_data_df, start_date, end_date):
        employee_master_df = pd.read_csv(
            "temp_data/temp_employee_master.csv", dtype={"Nomor Rekening": str}
        )
        holidays_date_df = pd.read_csv("temp_data/temp_holidays_date.csv")
        st.markdown(" \n\n")
        # st.write("Klik tombol dibawah untuk hitung gaji & generate kwitansi")
        col1, col2 = st.columns(2)
        btnHitungGaji = st.button(
                "Hitung Gaji", help="klik tombol ini untuk hitung gaji", type="primary"
            )

        if btnHitungGaji:
            with st.spinner("Loading...."):
                attendance_data_df["Tanggal"] = pd.to_datetime(
                    attendance_data_df["Tanggal"], format="%d-%m-%Y"
                )
                attendance_data_df["Tanggal"] = attendance_data_df["Tanggal"].dt.date
                filtered_attendance_df = attendance_data_df[
                    attendance_data_df["Tanggal"].between(start_date, end_date)
                ]
                # join to get payroll details
                absensi_emp_master = filtered_attendance_df.merge(
                    employee_master_df[
                        [
                            "PIN/ID",
                            "Keterangan",
                            "Gaji Harian (Pokok)",
                            "Upah Lembur",
                            "Nama Bank",
                            "Nama Akun Bank",
                            "Nomor Rekening",
                        ]
                    ],
                    left_on="NIP",
                    right_on="PIN/ID",
                    how="left",
                )
                
                #absensi_emp_master = absensi_emp_master[absensi_emp_master["Keterangan Tidak Hadir"].isnull()]
                
                absensi_emp_master["Tanggal"] = pd.to_datetime(
                    absensi_emp_master["Tanggal"]
                )
                holidays_date_df["Tanggal Libur"] = pd.to_datetime(
                    holidays_date_df["Tanggal Libur"]
                )
                # get holiday flag
                absensi_emp_master["weekday"] = absensi_emp_master["Tanggal"].dt.day_name()

                absensi_emp_master = absensi_emp_master.merge(
                    holidays_date_df,
                    left_on="Tanggal",
                    right_on="Tanggal Libur",
                    how="left",
                )
                absensi_emp_master["is_holiday"] = (
                    absensi_emp_master["Tanggal"]
                    .isin(holidays_date_df["Tanggal Libur"])
                    .apply(lambda x: "Y" if x else "N")
                )
                absensi_emp_master = absensi_emp_master.drop(
                    columns=["PIN/ID", "Tanggal Libur"]
                )
                # st.write(absensi_emp_master)
                # get daily worker only data
                pekerja_harian = absensi_emp_master[
                    absensi_emp_master["Keterangan"] == "HARIAN"
                ]
                pekerja_harian_scan = pekerja_harian.drop(
                    columns=["Tidak Scan Masuk", "Tidak Scan Pulang"]
                )

                # convert Scan related column into datetime
                for col in list(pekerja_harian_scan.filter(regex="Scan ").columns):
                    pekerja_harian[col] = pd.to_datetime(
                        pekerja_harian_scan[col], format="%H:%M:%S"
                    )

                pekerja_harian["Tanggal"] = pd.to_datetime(pekerja_harian["Tanggal"])

                # get scan_masuk and scan_pulang
                pekerja_harian["scan_min"] = pekerja_harian[
                    list(pekerja_harian_scan.filter(regex="Scan").columns)
                ].min(axis=1)
                pekerja_harian["scan_max"] = pekerja_harian[
                    list(pekerja_harian_scan.filter(regex="Scan").columns)
                ].max(axis=1)
                
                pekerja_harian[
                    ["scan_masuk", "scan_pulang"]
                ] = pekerja_harian.apply(calculate_scan_time, axis=1, result_type="expand")
              
                # daily worker early scan (before 8AM)
                pekerja_harian["scan_masuk"] = pekerja_harian["scan_masuk"].apply(
                    lambda x: pd.Timestamp("1900-01-01T08")
                    if x <= pd.Timestamp("1900-01-01T08")
                    else x
                )

                # get denda and uang makan
                # pekerja_harian["denda_tidak_scan_masuk"] = pekerja_harian[
                #     "Tidak Scan Masuk"
                # ].apply(lambda x: denda_scan_masuk if x == "Y" else 0)
                # pekerja_harian["denda_tidak_scan_pulang"] = pekerja_harian[
                #     "Tidak Scan Pulang"
                # ].apply(lambda x: denda_scan_masuk if x == "Y" else 0)
                # pekerja_harian["uang_makan_harian"] = pekerja_harian["Uang Makan"].apply(
                #     lambda x: uang_makan if x == "Y" else 0
                # )
                
                # calculate working hours
                pekerja_harian[
                    ["jam_kerja", "jam_lembur", "timedelta"]
                ] = pekerja_harian.apply(calculate_work_hours, axis=1, result_type="expand")
      
                pekerja_harian[
                    ["gaji_harian", "gaji_lembur", "total_gaji_harian"]
                ] = pekerja_harian.apply(calculate_salary, axis=1, result_type="expand")

                total_gaji_df = (
                    pekerja_harian.groupby("NIP")
                    .agg({"total_gaji_harian": "sum","Kasbon": "sum"})
                    .rename(columns={"total_gaji_harian": "gaji_final_sebelum_kasbon","Kasbon": "total_kasbon"})
                    .reset_index()
                )
                gaji_pekerja_harian_details = pd.merge(
                    pekerja_harian, total_gaji_df, on="NIP", how="left"
                )

                gaji_pekerja_harian_details["gaji_final"] = gaji_pekerja_harian_details["gaji_final_sebelum_kasbon"] - gaji_pekerja_harian_details["total_kasbon"] 
                
                df_ph_details = (
                gaji_pekerja_harian_details[
                        [
                            "NIP",
                            "Nama",
                            "Tanggal",
                            "Keterangan",
                            "Gaji Harian (Pokok)",
                            "Upah Lembur",
                            "Keterangan Libur",
                            "scan_masuk",
                            "scan_pulang",
                            "denda_tidak_scan_masuk",
                            "denda_tidak_scan_pulang",
                            "uang_makan_harian",
                            "jam_kerja",
                            "jam_lembur",
                            "timedelta",
                            "gaji_harian",
                            "gaji_lembur",
                            "total_gaji_harian",
                            "gaji_final_sebelum_kasbon",
                            "total_kasbon",
                            "gaji_final"
                        ]
                    ]
                )
                st.markdown("### Detail Gaji Pekerja Harian (preview)")
                st.dataframe(df_ph_details)


                ph_list_nip = df_ph_details["NIP"].drop_duplicates().values.tolist()
                ph_list_filename = []
                for idx in range(len(ph_list_nip)):
                    temp_df = df_ph_details[df_ph_details["NIP"] == ph_list_nip[idx]]
                    nama_str = temp_df['Nama'].head(1).to_string(index=False).replace(' ', '_')
                    file_name = "Details_"+nama_str+"_"+str(start_date.strftime('%d%b'))+"-"+str(end_date.strftime('%d%b%Y'))+".xlsx"
                    temp_df.to_excel("kwitansi_output/" + file_name, index=None)
                    ph_list_filename.append("kwitansi_output/" + file_name)
                
                df_kwitansi = (
                    gaji_pekerja_harian_details[
                        [
                            "NIP",
                            "Nama",
                            "Nama Bank",
                            "Nama Akun Bank",
                            "Nomor Rekening",
                            "total_kasbon",
                            "gaji_final_sebelum_kasbon"
                        ]
                    ]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
                df_kwitansi["gaji_final"] = df_kwitansi["gaji_final_sebelum_kasbon"] - df_kwitansi["total_kasbon"] 
                df_kwitansi["start_date"] = start_date
                df_kwitansi["end_date"] = end_date
                df_kwitansi[["nama_worksheet"]] = df_kwitansi[["Nama"]].replace(
                    " ", "_", regex=True
                )
                file_list = generate_kwitansi(df_kwitansi)

                
                st.markdown("### Detail Kwitansi")
                st.write(df_kwitansi)
                gaji_pekerja_harian_details.to_excel(
                    "kwitansi_output/" + "detail_perhitungan_gaji.xlsx", index=None
                )
                df_kwitansi.to_excel(
                    "kwitansi_output/" + "detail_kwitansi.xlsx", index=None
                )

                file_list.append("kwitansi_output/" + "detail_kwitansi.xlsx")
                file_list.append("kwitansi_output/" + "detail_perhitungan_gaji.xlsx")
                file_list+=ph_list_filename
                with zipfile.ZipFile(
                    "kwitansi_output/"
                    + "Kwitansi_"
                    + str(start_date.strftime("%d%b"))
                    + "-"
                    + str(end_date.strftime("%d%b%Y"))
                    + ".zip",
                    "w",
                ) as zipMe:
                    for file in file_list:
                        zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)
        with col2:
            my_file = Path(
                "kwitansi_output/"
                + "Kwitansi_"
                + str(start_date.strftime("%d%b"))
                + "-"
                + str(end_date.strftime("%d%b%Y"))
                + ".zip"
            )
            if my_file.is_file():
                with open(
                    "kwitansi_output/"
                    + "Kwitansi_"
                    + str(start_date.strftime("%d%b"))
                    + "-"
                    + str(end_date.strftime("%d%b%Y"))
                    + ".zip",
                    "rb",
                ) as fp:
                    btn = st.download_button(
                        label="Download Kwitansi",
                        data=fp,
                        file_name="Kwitansi_"
                        + str(start_date.strftime("%d%b"))
                        + "-"
                        + str(end_date.strftime("%d%b%Y"))
                        + ".zip",
                        mime="application/zip",
                    )
