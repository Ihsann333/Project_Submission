import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema visualisasi dasar
sns.set_theme(style="whitegrid")

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="E-Commerce Demographics", page_icon="🛒", layout="wide")

# Memuat data hasil pembersihan
@st.cache_data
def load_data():
    df = pd.read_csv("clean_customers.csv")
    return df

df = load_data()

# Header Dashboard
st.title("🛒 E-Commerce Customer Demographics Dashboard")
st.markdown("Dashboard ini menampilkan hasil analisis geografis persebaran pelanggan e-commerce di Brazil.")

# Sidebar untuk Filter
st.sidebar.header("Filter Data")
selected_region = st.sidebar.multiselect(
    "Pilih Region Makro:", 
    options=df['region_cluster'].unique(), 
    default=df['region_cluster'].unique()
)

# Terapkan filter pada dataframe
filtered_df = df[df['region_cluster'].isin(selected_region)]

# Menampilkan metrik utama
col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan Unik", f"{filtered_df.shape[0]:,}")
col2.metric("Total Kota (City)", f"{filtered_df['customer_city'].nunique():,}")
col3.metric("Total Negara Bagian (State)", f"{filtered_df['customer_state'].nunique():,}")

st.divider()

# Layout Visualisasi Baris 1: Kota & Negara Bagian
st.subheader("1. Konsentrasi Pelanggan Berdasarkan Kota & Negara Bagian")
fig1, ax1 = plt.subplots(1, 2, figsize=(16, 6))

# Visualisasi Top 10 Kota
top_cities = filtered_df.groupby('customer_city').customer_unique_id.nunique().sort_values(ascending=False).head(10).reset_index()
sns.barplot(x='customer_unique_id', y='customer_city', data=top_cities, palette='viridis', ax=ax1[0])
ax1[0].set_title("Top 10 Kota dengan Pelanggan Terbanyak", fontsize=14)
ax1[0].set_xlabel("Jumlah Pelanggan")
ax1[0].set_ylabel("Kota")

# Visualisasi Top 5 Negara Bagian
top_states = filtered_df.groupby('customer_state').customer_unique_id.nunique().sort_values(ascending=False).head(5).reset_index()
sns.barplot(x='customer_state', y='customer_unique_id', data=top_states, palette='Blues_r', ax=ax1[1])
ax1[1].set_title("Top 5 Negara Bagian dengan Pelanggan Terbanyak", fontsize=14)
ax1[1].set_xlabel("Negara Bagian")
ax1[1].set_ylabel("Jumlah Pelanggan")

st.pyplot(fig1)

st.divider()

# Layout Visualisasi Baris 2: Analisis Lanjutan (Clustering)
st.subheader("2. Distribusi Pelanggan Berdasarkan Region Makro (Clustering)")
fig2, ax2 = plt.subplots(figsize=(10, 5))
cluster_counts = filtered_df.groupby('region_cluster').customer_unique_id.nunique().sort_values(ascending=False).reset_index()

sns.barplot(x='customer_unique_id', y='region_cluster', data=cluster_counts, palette='magma', ax=ax2)
ax2.set_title("Distribusi Pelanggan per Region Makro Brazil", fontsize=14)
ax2.set_xlabel("Jumlah Pelanggan")
ax2.set_ylabel("Region")

st.pyplot(fig2)
