from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Demographics", page_icon="🛒", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "main_data.csv"
    return pd.read_csv(file_path, parse_dates=["order_purchase_timestamp"])


def pct_label(count, total):
    return f"{count:,} ({count / total * 100:.2f}%)"


df = load_data()

st.title("🛒 E-Commerce Customer Demographics Dashboard")
st.markdown("Dashboard ini menampilkan hasil analisis persebaran pelanggan unik e-commerce di Brazil (2016-2018).")

st.sidebar.header("Filter Data Global")
st.sidebar.markdown("Semua filter di bawah memengaruhi seluruh metrik dan visualisasi.")

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Periode Tanggal Pesanan:", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, (tuple, list)) else date_range

all_regions = sorted(df["region_cluster"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region Makro:", options=all_regions, default=all_regions)

state_options = sorted(df.loc[df["region_cluster"].isin(selected_regions), "customer_state"].unique())
selected_states = st.sidebar.multiselect("Negara Bagian (State):", options=state_options, default=state_options)

order_date = df["order_purchase_timestamp"].dt.date
filtered_df = df[
    (order_date >= start_date)
    & (order_date <= end_date)
    & (df["region_cluster"].isin(selected_regions))
    & (df["customer_state"].isin(selected_states))
]

if filtered_df.empty:
    st.warning("Data tidak tersedia untuk filter yang dipilih. Silakan ubah periode, region, atau negara bagian.")
    st.stop()

total_customers = filtered_df["customer_unique_id"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pelanggan Unik", f"{total_customers:,}")
col2.metric("Total Pesanan", f"{filtered_df['order_id'].nunique():,}")
col3.metric("Total Kota (City)", f"{filtered_df['customer_city'].nunique():,}")
col4.metric("Total Negara Bagian (State)", f"{filtered_df['customer_state'].nunique():,}")

st.divider()

st.subheader("1. Top 10 Kota dengan Konsentrasi Pelanggan Terbesar")
top_cities = (
    filtered_df.groupby("customer_city").customer_unique_id.nunique()
    .sort_values(ascending=False).head(10).reset_index()
)
top_cities.columns = ["customer_city", "customer_count"]

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x="customer_count", y="customer_city", hue="customer_city", data=top_cities,
            palette="viridis", legend=False, ax=ax1)
for i, cnt in enumerate(top_cities["customer_count"]):
    ax1.text(cnt, i, "  " + pct_label(cnt, total_customers), va="center", fontsize=10)
ax1.set_xlim(0, top_cities["customer_count"].max() * 1.2)
ax1.set_title("Top 10 Kota dengan Pelanggan Terbanyak", fontsize=14, fontweight="bold")
ax1.set_xlabel("Jumlah Pelanggan Unik (orang)")
ax1.set_ylabel("Kota")
st.pyplot(fig1)
leader = top_cities.iloc[0]
st.caption(
    f"Dalam filter saat ini, {leader['customer_city']} memiliki pelanggan terbanyak: "
    f"{pct_label(int(leader['customer_count']), total_customers)}. Persentase dihitung terhadap seluruh pelanggan unik hasil filter."
)

st.divider()

st.subheader("2. Top 5 Negara Bagian dengan Distribusi Pelanggan Terbesar")
top_states = (
    filtered_df.groupby("customer_state").customer_unique_id.nunique()
    .sort_values(ascending=False).head(5).reset_index()
)
top_states.columns = ["customer_state", "customer_count"]

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x="customer_state", y="customer_count", hue="customer_state", data=top_states,
            palette="Blues_r", legend=False, ax=ax2)
for i, cnt in enumerate(top_states["customer_count"]):
    ax2.text(i, cnt, f"{cnt:,}\n({cnt / total_customers * 100:.2f}%)", ha="center", va="bottom", fontsize=10)
ax2.set_ylim(0, top_states["customer_count"].max() * 1.18)
ax2.set_title("Top 5 Negara Bagian dengan Pelanggan Terbanyak", fontsize=14, fontweight="bold")
ax2.set_xlabel("Negara Bagian (State)")
ax2.set_ylabel("Jumlah Pelanggan Unik (orang)")
st.pyplot(fig2)
st.caption(
    f"Lima negara bagian teratas pada filter ini mencakup {top_states['customer_count'].sum() / total_customers * 100:.2f}% pelanggan unik."
)

st.divider()

st.subheader("3. Segmentasi Pelanggan Berdasarkan Region Makro")
region_counts = (
    filtered_df.groupby("region_cluster").customer_unique_id.nunique()
    .sort_values(ascending=False).reset_index()
)
region_counts.columns = ["region_cluster", "customer_count"]

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(x="customer_count", y="region_cluster", hue="region_cluster", data=region_counts,
            palette="magma", legend=False, ax=ax3)
for i, cnt in enumerate(region_counts["customer_count"]):
    ax3.text(cnt, i, "  " + pct_label(cnt, total_customers), va="center", fontsize=10)
ax3.set_xlim(0, region_counts["customer_count"].max() * 1.2)
ax3.set_title("Distribusi Pelanggan per Region Makro Brazil", fontsize=14, fontweight="bold")
ax3.set_xlabel("Jumlah Pelanggan Unik (orang)")
ax3.set_ylabel("Region")
st.pyplot(fig3)