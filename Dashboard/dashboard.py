import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static

# Pengaturan tampilan Seaborn
sns.set(style='darkgrid')

# Membaca dataset dengan caching untuk menghemat resource
@st.cache_data
def load_data():
    try:
        all_df = pd.read_csv('Dashboard\df.csv') 
        geolocation_df = pd.read_csv('Dashboard\geolocation.csv') 
        all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'])
        return all_df, geolocation_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Memuat data
data, geolocation = load_data()

# Jika data berhasil dimuat
if not data.empty and not geolocation.empty:
    # Mengatur sidebar
    st.sidebar.header("Filter") 
    st.sidebar.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    min_date = data['order_approved_at'].min().date()  # Ubah ke format date
    max_date = data['order_approved_at'].max().date()  # Ubah ke format date

    # Gunakan pd.to_datetime untuk memastikan kita mendapatkan tanggal
    start_date, end_date = st.sidebar.date_input("Select Date Range", 
                                                [min_date, max_date], 
                                                min_value=min_date, 
                                                max_value=max_date)

    # Filter data berdasarkan tanggal
    filtered_df = data[(data['order_approved_at'] >= pd.to_datetime(start_date)) & 
                    (data['order_approved_at'] <= pd.to_datetime(end_date))]

    # Judul Dashboard
    st.title("E-Commerce Public Data Analysis")
    st.write("**Dashboard untuk analisis data e-commerce.**")

    # Analisis Total Order dan Revenue
    total_orders = filtered_df['order_id'].nunique()
    total_revenue = filtered_df['payment_value'].sum()
    st.metric(label="Total Orders", value=total_orders)
    st.metric(label="Total Revenue", value=f"${total_revenue:.2f}")

    # Visualisasi Order Harian
    st.subheader("Daily Orders")
    daily_orders = filtered_df.resample('D', on='order_approved_at').agg({'order_id': 'nunique'}).reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=daily_orders, x='order_approved_at', y='order_id', marker='o', color='blue')
    plt.title('Daily Orders Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Orders')
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())  # gcf() digunakan untuk memastikan grafik muncul di Streamlit

    # Visualisasi Pengeluaran Pelanggan
    st.subheader("Customer Spending")
    customer_spending = filtered_df.groupby('customer_id')['payment_value'].sum().reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.histplot(customer_spending['payment_value'], bins=30, color='green', kde=True)
    plt.title('Distribution of Customer Spending')
    plt.xlabel('Spending Amount')
    plt.ylabel('Frequency')
    st.pyplot(plt.gcf())

    # Visualisasi Produk Terlaris
    st.subheader("Top Selling Products")
    top_products = filtered_df['product_category_name_english'].value_counts().head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_products.index, y=top_products.values, palette='viridis')
    plt.title('Top Selling Products')
    plt.xlabel('Product Categories')
    plt.ylabel('Number of Sales')
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())

    # Visualisasi Skor Ulasan
    st.subheader("Customer Review Scores")
    review_scores = filtered_df['review_score'].value_counts().sort_index()
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=review_scores.index, y=review_scores.values, palette='coolwarm')
    plt.title('Distribution of Customer Review Scores')
    plt.xlabel('Review Score')
    plt.ylabel('Count')
    st.pyplot(plt.gcf())

    # Visualisasi Geolokasi Pelanggan
    st.subheader("Customer Geolocation")
    if 'geolocation_lng' in geolocation.columns and 'geolocation_lat' in geolocation.columns:
        map_center = [geolocation['geolocation_lat'].mean(), geolocation['geolocation_lng'].mean()]
        customer_map = folium.Map(location=map_center, zoom_start=5)

        # Menambahkan marker untuk setiap pelanggan
        for idx, row in geolocation.iterrows():
            folium.CircleMarker(
                location=(row['geolocation_lat'], row['geolocation_lng']),
                radius=3,
                color='blue',
                fill=True,
                fill_opacity=0.6
            ).add_to(customer_map)

        # Menampilkan peta dalam Streamlit
        st.subheader("Map of Customer Locations")
        # Menyimpan peta dalam HTML dan menampilkannya
        folium_static(customer_map)

    # Informasi Tambahan di Sidebar
    st.sidebar.header("Data Info")
    st.sidebar.write(f"Total Records: {len(data)}")
    st.sidebar.write(f"Selected Date Range: {start_date} to {end_date}")
    
    # Menjalankan aplikasi
    st.caption('Copyright (C) Rama Syailana Dewa 2024')

else:
    st.error("Data tidak tersedia. Pastikan dataset df.csv dan geolocation.csv sudah benar.")
