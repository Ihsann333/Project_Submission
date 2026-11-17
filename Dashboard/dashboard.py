from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Olist Customer Demographics", page_icon="🛒", layout="wide")
sns.set_theme(style="whitegrid")


def load_data():
    file_path = Path(__file__).parent / "main_data.csv"
    return pd.read_csv(file_path)


def pct_label(count, total):
    return f"{count:,} ({count / total * 100:.2f}%)"


def make_table(data, label_col, label_name, total):
    t = data.copy()
    t.insert(0, "No", range(1, len(t) + 1))
    t["Persentase (%)"] = (t["customer_count"] / total * 100).round(2)
    return t.rename(columns={label_col: label_name, "customer_count": "Jumlah Pelanggan Unik"})


df = load_data()

st.title("🛒 Olist Customer Demographics Dashboard")
st.markdown(
    "Dashboard ini menampilkan persebaran pelanggan unik Olist berdasarkan kota, "
    "negara bagian (state), dan region makro Brazil."
)

st.subheader("5 Data Teratas (Head)")
st.dataframe(df.head(5), hide_index=True)

st.sidebar.header("Filter Data")
st.sidebar.markdown("Filter di bawah memengaruhi seluruh metrik, grafik, dan tabel.")

all_regions = sorted(df["region_cluster"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region Makro:", options=all_regions, default=all_regions)

state_options = sorted(df.loc[df["region_cluster"].isin(selected_regions), "customer_state"].unique())
selected_states = st.sidebar.multiselect("Negara Bagian (State):", options=state_options, default=state_options)

filtered_df = df[
    df["region_cluster"].isin(selected_regions) & df["customer_state"].isin(selected_states)
]

if filtered_df.empty:
    st.warning("Data tidak tersedia untuk filter yang dipilih. Silakan ubah region atau negara bagian.")
    st.stop()

total_customers = filtered_df["customer_unique_id"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan Unik", f"{total_customers:,}")
col2.metric("Total Kota (City)", f"{filtered_df['customer_city'].nunique():,}")
col3.metric("Total Negara Bagian (State)", f"{filtered_df['customer_state'].nunique():,}")

st.divider()

# ---------------------------------------------------------------- Pertanyaan 1
st.subheader("1. Top 10 Kota dengan Pelanggan Unik Terbanyak")
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
ax1.set_title("10 Kota dengan Pelanggan Unik Terbanyak", fontsize=14, fontweight="bold")
ax1.set_xlabel("Jumlah Pelanggan Unik (orang)")
ax1.set_ylabel("Kota")
st.pyplot(fig1)
leader = top_cities.iloc[0]
st.caption(
    f"Pada filter saat ini, {leader['customer_city']} memiliki pelanggan terbanyak: "
    f"{pct_label(int(leader['customer_count']), total_customers)}. "
    "Persentase dihitung terhadap seluruh pelanggan unik hasil filter."
)
st.dataframe(make_table(top_cities, "customer_city", "Kota", total_customers), hide_index=True)

st.divider()

# ---------------------------------------------------------------- Pertanyaan 2
st.subheader("2. Top 5 Negara Bagian dengan Pelanggan Unik Terbanyak")
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
ax2.set_title("5 Negara Bagian dengan Pelanggan Unik Terbanyak", fontsize=14, fontweight="bold")
ax2.set_xlabel("Negara Bagian (State)")
ax2.set_ylabel("Jumlah Pelanggan Unik (orang)")
st.pyplot(fig2)
st.caption(
    f"Lima negara bagian teratas pada filter ini mencakup "
    f"{top_states['customer_count'].sum() / total_customers * 100:.2f}% pelanggan unik."
)
st.dataframe(make_table(top_states, "customer_state", "Negara Bagian", total_customers), hide_index=True)

st.divider()

# ---------------------------------------------------------------- Region makro
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
ax3.set_ylabel("Region Makro")
st.pyplot(fig3)
st.dataframe(make_table(region_counts, "region_cluster", "Region Makro", total_customers), hide_index=True)
