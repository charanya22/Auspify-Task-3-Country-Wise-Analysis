import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Netflix Country-Wise Analysis", page_icon="🌍", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #f0fff7, #e3f5eb, #f8fffb);}
h1, h2, h3 {color: #246b52;}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.85);
    border: 1px solid #cce8d8;
    padding: 18px;
    border-radius: 16px;
}
.stButton button, .stDownloadButton button {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

data_path = Path(__file__).parent / "Dataset.csv"

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error("Dataset.csv was not found. Place it in the same folder as app.py.")
    st.stop()

required_columns = {"show_id", "title", "type", "country"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error("Dataset is missing required columns: " + ", ".join(sorted(missing_columns)))
    st.stop()

country_df = df[["show_id", "title", "type", "country"]].dropna(subset=["country"]).copy()
country_df["country"] = country_df["country"].astype(str).str.split(",")
country_df = country_df.explode("country")
country_df["country"] = country_df["country"].str.strip()
country_df = country_df[country_df["country"] != ""]

country_counts = country_df.groupby("country").size().sort_values(ascending=False)

st.title("🌍 Netflix Country-Wise Content Analysis")
st.caption("Auspify Technologies | Data Analysis Using Python")
st.markdown("---")

c1, c2, c3 = st.columns(3)
c1.metric("Countries / Regions", f"{len(country_counts):,}")
c2.metric("Title-Country Associations", f"{len(country_df):,}")
c3.metric("Top Country", country_counts.idxmax() if not country_counts.empty else "N/A")

st.markdown("---")
st.subheader("🏆 Top 10 Countries by Content")

top10 = country_counts.head(10).sort_values(ascending=True).reset_index()
top10.columns = ["Country", "Titles"]

fig = px.bar(
    top10,
    x="Titles",
    y="Country",
    orientation="h",
    text="Titles",
    color="Titles",
    color_continuous_scale=["#ccebd8", "#69b995", "#287b5c"],
    labels={"Titles": "Title-Country Associations"},
    title="Top 10 Countries"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=55, b=10)
)

st.plotly_chart(fig, width="stretch", key="top_countries_chart")

st.markdown("---")
st.subheader("🔎 Explore a Country")

countries = sorted(country_counts.index.tolist())

if countries:
    default_country = "India" if "India" in countries else countries[0]
    country = st.selectbox(
        "Select a country or region",
        countries,
        index=countries.index(default_country),
        key="country_selector"
    )

    selected = country_df[country_df["country"] == country].copy()

    left, right = st.columns([1, 2])

    with left:
        st.metric("Title-Country Associations", f"{len(selected):,}")
        st.metric("Unique Titles", f"{selected['show_id'].nunique():,}")

    with right:
        st.markdown(f"#### Content distribution in {country}")
        type_counts = selected.groupby("type").size().reset_index(name="Titles")

        fig2 = px.pie(
            type_counts,
            names="type",
            values="Titles",
            hole=0.45,
            color="type",
            color_discrete_map={
                "Movie": "#78bd9b",
                "TV Show": "#b5a4d8"
            },
            title="Movies vs TV Shows"
        )

        fig2.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=55, b=10)
        )

        st.plotly_chart(fig2, width="stretch", key="content_type_chart")

    with st.expander(f"View titles associated with {country}"):
        st.dataframe(
            selected[["title", "type", "country"]].drop_duplicates(),
            width="stretch",
            hide_index=True
        )

st.markdown("---")
st.subheader("📊 Country-Wise Summary")

summary = (
    country_df.groupby("country")
    .agg(
        Title_Associations=("show_id", "size"),
        Unique_Titles=("show_id", "nunique")
    )
    .reset_index()
    .rename(columns={"country": "Country"})
    .sort_values("Title_Associations", ascending=False)
)

st.dataframe(summary, width="stretch", hide_index=True)

st.download_button(
    "📥 Download Country-Wise Analysis CSV",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="country_wise_analysis.csv",
    mime="text/csv",
    key="download_country_summary"
)

st.markdown("---")
st.caption("Netflix Country-Wise Analysis | Python • Pandas • Plotly • Streamlit")
