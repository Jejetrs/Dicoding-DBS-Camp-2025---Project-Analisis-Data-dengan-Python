import streamlit as st
import pandas as pd
import plotly.express as px
from babel.numbers import format_currency

# Dataset
day_df = pd.read_csv("main_data/day_cleaned_final.csv")
hour_df = pd.read_csv("main_data/hour_cleaned_final.csv")

# Konversi Kolom Tanggal
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Sidebar
with st.sidebar:
    st.image("image.png")
    st.header("🔍 Filter Data")
    selected_year = st.selectbox("📅 Pilih Tahun", day_df['yr'].map({0: '2011', 1: '2012'}).unique())

    start_date = st.date_input("🗓️ Tanggal Mulai", day_df['dteday'].min())
    end_date = st.date_input("🗓️ Tanggal Akhir", day_df['dteday'].max())

    selected_season = st.multiselect("☀️ Pilih Musim", day_df['season'].unique(), day_df['season'].unique())

    # Keterangan Musim
    st.markdown("### Keterangan Musim")
    st.markdown("""
    - **1** → 🌸 Musim Semi (Spring)  
    - **2** → ☀️ Musim Panas (Summer)  
    - **3** → 🍂 Musim Gugur (Fall)  
    - **4** → ❄️ Musim Dingin (Winter)  
    """)

# **Filter Data**
if start_date > end_date:
    st.warning("❌ Tanggal mulai harus sebelum tanggal akhir. Silakan pilih kembali rentang tanggal yang benar.")
    day_filtered = pd.DataFrame()
else:
    day_filtered = day_df[(day_df['yr'] == int(selected_year) - 2011) & 
                          (day_df['season'].isin(selected_season)) & 
                          (day_df['dteday'] >= pd.to_datetime(start_date)) & 
                          (day_df['dteday'] <= pd.to_datetime(end_date))]

# **Dashboard Utama**
st.title("🚲 Dashboard Analisis Penyewaan Sepeda")

# **Metode Tabs untuk Analisis dan Penjelasan**
tab1, tab2 = st.tabs(["📊 Grafik Analisis", "ℹ️ Penjelasan Dataset & Pola"])

with tab1:
    col1, col2 = st.columns(2)
    total_orders = day_filtered['cnt'].sum() if not day_filtered.empty else 0
    total_revenue = format_currency(total_orders * 2, "USD", locale='en_US')

    with col1:
        st.metric("🛒 Total Order", value=f"{total_orders:,}")
    with col2:
        st.metric("💰 Total Pendapatan", value=total_revenue)

    # **Visualisasi hanya jika data tersedia**
    if not day_filtered.empty:
        # Grafik Penyewaan Harian
        st.markdown("### Tren Penyewaan")
        daily_counts = day_filtered.groupby('dteday')['cnt'].sum()
        fig = px.line(daily_counts, x=daily_counts.index, y=daily_counts.values, title="📊 Tren Penyewaan Sepeda Harian"
                    , labels={'x': 'Tanggal', 'y': 'Jumlah Penyewaan'})
        st.plotly_chart(fig)

        # Grafik Rata-rata Penyewaan Per Jam
        avg_hourly = hour_df.groupby('hr')['cnt'].mean()
        fig = px.bar(avg_hourly, x=avg_hourly.index, y=avg_hourly.values, 
                    title="⏰ Penyewaan Berdasarkan Jam",  
                    labels={'x': 'Jam', 'y': 'Rata-rata Penyewaan'}, 
                    color=avg_hourly.values, color_continuous_scale='Blues')
        st.plotly_chart(fig)

        # Grafik Penyewa Kasual vs Terdaftar
        st.markdown("### 👥 Perbandingan Penyewa")
        fig = px.line(day_filtered, x='dteday', y=['casual', 'registered'], title="Kasual vs Terdaftar",
                    labels={'value': 'Jumlah Penyewaan', 'dteday': 'Tanggal'},
                    color_discrete_map={'casual': 'blue', 'registered': 'red'})
        st.plotly_chart(fig)

        # Grafik Pengaruh Cuaca dan Suhu
        st.markdown("### 🌤️ Pengaruh Cuaca dan Suhu")
        fig = px.scatter(day_filtered, x='temp', y='cnt', color='weathersit',
                        title="Suhu vs Jumlah Penyewaan",
                        labels={'temp': 'Suhu', 'cnt': 'Jumlah Penyewaan'},
                        color_continuous_scale='viridis')  
        st.plotly_chart(fig)
    else:
        st.info("🔍 Tidak ada data yang tersedia untuk rentang tanggal yang dipilih.")

with tab2:
    # **Penjelasan Dataset**
    st.markdown("## ℹ️ Tentang Dataset Bike Sharing ")
    st.markdown("""
    Dataset ini berisi data historis penyewaan sepeda dari sistem **Capital Bikeshare, Washington D.C.** selama tahun **2011 dan 2012**.  
    Data mencakup informasi tentang jumlah penyewaan harian dan per jam, serta berbagai faktor yang mempengaruhinya seperti musim, cuaca, suhu, kelembaban, dan kecepatan angin.  
    Dataset ini dapat digunakan untuk analisis tren penyewaan sepeda, prediksi jumlah pengguna, serta deteksi anomali pada event tertentu. 📊
    """)
    
    st.markdown("## Pola Penyewaan Sepeda Berdasarkan Hari dan Jam")
    st.markdown("Penyewaan sepeda memiliki pola yang jelas sepanjang hari, dengan puncak pada pukul 08:00 (berangkat kerja/sekolah) dan 17:00–18:00 (pulang kerja/sekolah). "
    "Aktivitas penyewaan paling rendah terjadi pada dini hari (03:00–05:00). Tren bulanan menunjukkan peningkatan penyewaan sepeda dari awal tahun hingga pertengahan tahun "
    "(sekitar bulan Juni–Juli), lalu menurun menjelang akhir tahun. Pada tahun 2012, jumlah penyewaan lebih tinggi dibandingkan tahun 2011.")
    
    st.markdown("## ✅ Kesimpulan")
    st.markdown("""
    - 📈 Penyewaan meningkat di pertengahan tahun, dengan lonjakan signifikan pada jam sibuk (08:00 & 17:00-18:00).
    - 🔥 Suhu berpengaruh besar terhadap jumlah penyewaan.
    - 🚴‍♂️ Penyewa terdaftar lebih dominan dibanding kasual.
    - 🌧️ Kelembaban dan angin kencang sedikit mengurangi jumlah penyewaan.
    """)
