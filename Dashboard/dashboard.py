import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="E-Commerce Demographics", page_icon="🛒", layout="wide")

@st.cache_data
def load_data():
    file_path = Path(__file__).parent.parent / "data" / "clean_customers.csv"
    
    if not file_path.exists():
        file_path = Path(__file__).parent / "clean_customers.csv"
        
    return pd.read_csv(file_path)

df = load_data()

st.title("🛒 E-Commerce Customer Demographics Dashboard")
st.markdown("Dashboard ini menampilkan hasil analisis geografis persebaran pelanggan e-commerce di Brazil.")

st.sidebar.header("Filter Data Global")
st.sidebar.markdown("Filter ini akan memengaruhi seluruh metrik dan visualisasi di dashboard.")

available_states = df['customer_state'].unique()
selected_states = st.sidebar.multiselect(
    "Pilih Negara Bagian (State):", 
    options=available_states, 
    default=available_states
)

filtered_df = df[df['customer_state'].isin(selected_states)]

col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan Unik", f"{filtered_df.shape[0]:,}")
col2.metric("Total Kota (City)", f"{filtered_df['customer_city'].nunique():,}")
col3.metric("Total Negara Bagian (State)", f"{filtered_df['customer_state'].nunique():,}")

st.divider()

if filtered_df.empty:
    st.warning("Data tidak tersedia untuk filter yang dipilih. Silakan pilih negara bagian lain.")
else:
    st.subheader("1. Konsentrasi Pelanggan Berdasarkan Kota & Negara Bagian")
    fig1, ax1 = plt.subplots(1, 2, figsize=(16, 6))

    top_cities = filtered_df.groupby('customer_city').customer_unique_id.nunique().sort_values(ascending=False).head(10).reset_index()
    sns.barplot(x='customer_unique_id', y='customer_city', hue='customer_city', data=top_cities, palette='viridis', legend=False, ax=ax1[0])
    ax1[0].set_title("Top 10 Kota dengan Pelanggan Terbanyak", fontsize=14)
    ax1[0].set_xlabel("Jumlah Pelanggan")
    ax1[0].set_ylabel("Kota")

    top_states = filtered_df.groupby('customer_state').customer_unique_id.nunique().sort_values(ascending=False).head(5).reset_index()
    sns.barplot(x='customer_state', y='customer_unique_id', hue='customer_state', data=top_states, palette='Blues_r', legend=False, ax=ax1[1])
    ax1[1].set_title("Top 5 Negara Bagian dengan Pelanggan Terbanyak", fontsize=14)
    ax1[1].set_xlabel("Negara Bagian")
    ax1[1].set_ylabel("Jumlah Pelanggan")

    st.pyplot(fig1)

    st.divider()

    st.subheader("2. Distribusi Pelanggan Berdasarkan Region Makro")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    cluster_counts = filtered_df.groupby('region_cluster').customer_unique_id.nunique().sort_values(ascending=False).reset_index()

    sns.barplot(x='customer_unique_id', y='region_cluster', hue='region_cluster', data=cluster_counts, palette='magma', legend=False, ax=ax2)
    ax2.set_title("Distribusi Pelanggan per Region Makro Brazil", fontsize=14)
    ax2.set_xlabel("Jumlah Pelanggan")
    ax2.set_ylabel("Region")

    st.pyplot(fig2)