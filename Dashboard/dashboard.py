from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Demographics", page_icon="🛒", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_data():
    folder = Path(__file__).parent
    for path in (folder / "main_data.csv", folder.parent / "main_data.csv"):
        if path.exists():
            return pd.read_csv(path)
    st.error("File main_data.csv tidak ditemukan. Jalankan Notebook.ipynb terlebih dahulu.")
    st.stop()


df = load_data()

st.title("🛒 E-Commerce Customer Demographics Dashboard")
st.markdown(
    "Dashboard ini menampilkan hasil analisis geografis persebaran pelanggan e-commerce (Olist) di Brazil. "
    "Data bersumber dari tabel pelanggan dan mencakup seluruh data historis yang tercatat di dataset."
)

st.sidebar.header("Filter Data Global")
st.sidebar.markdown("Filter ini memengaruhi seluruh metrik dan visualisasi di dashboard.")

all_regions = sorted(df["region_cluster"].unique())
selected_regions = st.sidebar.multiselect("Region Makro:", options=all_regions, default=all_regions)

state_options = sorted(df.loc[df["region_cluster"].isin(selected_regions), "customer_state"].unique())
selected_states = st.sidebar.multiselect("Negara Bagian (State):", options=state_options, default=state_options)

filtered_df = df[df["region_cluster"].isin(selected_regions) & df["customer_state"].isin(selected_states)]

col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan Unik", f"{filtered_df['customer_unique_id'].nunique():,}")
col2.metric("Total Kota (City)", f"{filtered_df['customer_city'].nunique():,}")
col3.metric("Total Negara Bagian (State)", f"{filtered_df['customer_state'].nunique():,}")

st.divider()

if filtered_df.empty:
    st.warning("Data tidak tersedia untuk filter yang dipilih. Silakan pilih region atau negara bagian lain.")
else:
    total_customers = filtered_df["customer_unique_id"].nunique()
    city_counts = (
        filtered_df.groupby("customer_city")["customer_unique_id"].nunique()
        .sort_values(ascending=False).reset_index(name="customer_count")
    )

    st.subheader("1. Di 10 kota manakah konsentrasi pelanggan terbesar berada?")
    top_cities = city_counts.head(10).copy()
    top_cities["percentage"] = top_cities["customer_count"] / total_customers * 100

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(x="customer_count", y="customer_city", hue="customer_city",
                data=top_cities, palette="viridis", legend=False, ax=ax1)
    for i, (cnt, pct) in enumerate(zip(top_cities["customer_count"], top_cities["percentage"])):
        ax1.text(cnt + top_cities["customer_count"].max() * 0.01, i, f"{cnt:,} ({pct:.2f}%)", va="center")
    ax1.set_xlim(0, top_cities["customer_count"].max() * 1.2)
    ax1.set_title("Top 10 Kota dengan Pelanggan Unik Terbanyak", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Jumlah Pelanggan Unik (persentase dari total pelanggan terfilter)")
    ax1.set_ylabel("Kota")
    st.pyplot(fig1)
    plt.close(fig1)

    top10_pct = top_cities["customer_count"].sum() / total_customers * 100
    st.caption(
        f"**{top_cities.iloc[0]['customer_city']}** berada di posisi teratas dengan "
        f"{top_cities.iloc[0]['customer_count']:,} pelanggan ({top_cities.iloc[0]['percentage']:.2f}%). "
        f"Gabungan {len(top_cities)} kota teratas mewakili {top10_pct:.2f}% pelanggan terfilter."
    )

    st.divider()

    st.subheader("2. Bagaimana distribusi pelanggan di 5 negara bagian teratas?")
    top_states = (
        filtered_df.groupby("customer_state")["customer_unique_id"].nunique()
        .sort_values(ascending=False).head(5).reset_index(name="customer_count")
    )
    top_states["percentage"] = top_states["customer_count"] / total_customers * 100

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(x="customer_state", y="customer_count", hue="customer_state",
                data=top_states, palette="Blues_r", legend=False, ax=ax2)
    for i, (cnt, pct) in enumerate(zip(top_states["customer_count"], top_states["percentage"])):
        ax2.text(i, cnt + top_states["customer_count"].max() * 0.01, f"{cnt:,}\n({pct:.2f}%)",
                 ha="center", va="bottom")
    ax2.set_ylim(0, top_states["customer_count"].max() * 1.18)
    ax2.set_title("Top 5 Negara Bagian dengan Pelanggan Unik Terbanyak", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Negara Bagian")
    ax2.set_ylabel("Jumlah Pelanggan Unik (persentase dari total pelanggan terfilter)")
    st.pyplot(fig2)
    plt.close(fig2)

    st.caption(
        f"Lima negara bagian teratas mencakup {top_states['percentage'].sum():.2f}% pelanggan terfilter; "
        f"**{top_states.iloc[0]['customer_state']}** menjadi yang terbesar "
        f"({top_states.iloc[0]['percentage']:.2f}%)."
    )

    st.divider()

    st.subheader("3. Segmentasi Pelanggan Berdasarkan Region Makro")
    region_counts = (
        filtered_df.groupby("region_cluster")["customer_unique_id"].nunique()
        .sort_values(ascending=False).reset_index(name="customer_count")
    )
    region_counts["percentage"] = region_counts["customer_count"] / total_customers * 100

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    sns.barplot(x="customer_count", y="region_cluster", hue="region_cluster",
                data=region_counts, palette="magma", legend=False, ax=ax3)
    for i, (cnt, pct) in enumerate(zip(region_counts["customer_count"], region_counts["percentage"])):
        ax3.text(cnt + region_counts["customer_count"].max() * 0.01, i, f"{cnt:,} ({pct:.2f}%)", va="center")
    ax3.set_xlim(0, region_counts["customer_count"].max() * 1.2)
    ax3.set_title("Distribusi Pelanggan per Region Makro Brazil", fontsize=14, fontweight="bold")
    ax3.set_xlabel("Jumlah Pelanggan Unik")
    ax3.set_ylabel("Region")
    st.pyplot(fig3)
    plt.close(fig3)

    st.divider()

    st.subheader("4. Segmentasi Kota Berdasarkan Ukuran Basis Pelanggan")
    labels = ["1-10", "11-50", "51-100", "101-1000", ">1000"]
    city_counts["city_tier"] = pd.cut(
        city_counts["customer_count"], bins=[0, 10, 50, 100, 1000, float("inf")], labels=labels
    )
    tier = city_counts.groupby("city_tier", observed=False).agg(
        jumlah_kota=("customer_city", "count"), jumlah_pelanggan=("customer_count", "sum")
    ).reset_index()
    tier["city_tier"] = tier["city_tier"].astype(str)
    tier["pct_kota"] = tier["jumlah_kota"] / tier["jumlah_kota"].sum() * 100
    tier["pct_pelanggan"] = tier["jumlah_pelanggan"] / total_customers * 100

    fig4, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, col, pal, title, xl in [
        (axes[0], "pct_kota", "crest", "Persentase Jumlah Kota per Tier", "% dari seluruh kota"),
        (axes[1], "pct_pelanggan", "flare", "Persentase Pelanggan per Tier", "% dari seluruh pelanggan unik"),
    ]:
        sns.barplot(x=col, y="city_tier", hue="city_tier", data=tier, palette=pal,
                    order=labels, legend=False, ax=ax)
        for i, lab in enumerate(labels):
            v = tier.loc[tier["city_tier"] == lab, col].iloc[0]
            ax.text(v + 0.5, i, f"{v:.2f}%", va="center")
        ax.set_xlim(0, max(tier[col].max() * 1.2, 1))
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel(xl)
        ax.set_ylabel("")
    axes[0].set_ylabel("Tier (pelanggan unik per kota)")
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    small = tier.loc[tier["city_tier"] == "1-10"].iloc[0]
    st.caption(
        f"{small['pct_kota']:.2f}% kota hanya memiliki 1-10 pelanggan, "
        f"namun totalnya hanya {small['pct_pelanggan']:.2f}% dari seluruh pelanggan terfilter."
    )

st.caption("Catatan: dataset pelanggan tidak memiliki kolom tanggal, sehingga dashboard tidak menyediakan filter waktu.")
