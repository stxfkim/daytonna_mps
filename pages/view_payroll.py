import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(
    initial_sidebar_state="collapsed"
)




slip_gaji_bayangan = pd.read_csv('temp_data/temp_slip_bayangan.csv', dtype={"nik": str})
slip_gaji_bayangan['tanggal'] = pd.to_datetime(slip_gaji_bayangan['tanggal']).dt.date
slip_gaji_bayangan['jam_mulai'] = pd.to_datetime(slip_gaji_bayangan['jam_mulai']).dt.time
slip_gaji_bayangan['jam_akhir'] = pd.to_datetime(slip_gaji_bayangan['jam_akhir']).dt.time

st.html("<div style='text-align: center'> <H1> Slip Gaji Bayangan </H1> </div>")
st.html("<div style='text-align: center'> <H3> PT. Daytonna Niaga Adhya </H3> </div>")


def filter_data(query):
    return slip_gaji_bayangan[slip_gaji_bayangan['nik'].str.contains(query, case=False)]
            # Input for searching
search_query = st.text_input('masukkan Nomor Induk Karyawan anda:', '')




    # Show table only if there's a search query

if search_query:
    filtered_data = filter_data(search_query)
    if len(search_query) == 5 and not filtered_data.empty:
        
        nik_unique = filtered_data['nik'].unique()
        nik = nik_unique[0]
        nama_unique = filtered_data['nama'].unique()
        nama = nama_unique[0]
        total_jam_kerja = filtered_data['total_jam'].sum()
        if not filtered_data.empty:
            df_show = filtered_data[['tanggal', 'jam_mulai', 'jam_akhir', 'total_jam']]
            df_show.columns = ['Tanggal', 'Jam Mulai', 'Jam Akhir', 'Jam Kerja']
            min_date = slip_gaji_bayangan['tanggal'].min().strftime('%d %B %Y')
            max_date = slip_gaji_bayangan['tanggal'].max().strftime('%d %B %Y')
            indonesian_months = {
                'January': 'Januari', 'February': 'Februari', 'March': 'Maret', 'April': 'April',
                'May': 'Mei', 'June': 'Juni', 'July': 'Juli', 'August': 'Agustus',
                'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Desember'
            }
            for english, indonesian in indonesian_months.items():
                min_date = min_date.replace(english, indonesian)
                max_date = max_date.replace(english, indonesian)
            #st.write("Nomor Induk Karyawan              : ", nik)
            st.write(f"Nomor Induk Karyawan :  **{str(nik)}**")
            st.write(f"Nama :  **{str(nama)}**")
            st.write(f"Periode :  **{str(min_date)}** - **{str(max_date)}**")
            st.write(f"Total Jam Kerja :  **{str(total_jam_kerja)}**")
         
            st.dataframe(df_show.set_index(df_show.columns[0]),height=1120,width=500)
        else:
            st.warning("Nomor Induk Karyawan tidak ditemukan")
    else:
        st.warning("Nomor Induk Karyawan tidak ditemukan")
else:
    st.info('Masukkan Nomor Induk Karyawan untuk melihat slip gaji bayangan.')



font_css = """
    <style>

   h1,h3{
   padding: 0rem 0px 0rem;
   }
   p {
   margin: 0;
   }
   
    #MainMenu {visibility: hidden;}

    """
st.markdown(font_css, unsafe_allow_html=True)