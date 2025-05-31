import streamlit as st
import pandas as pd
import altair as alt
import os

# === HEADER + INTRO ===
st.set_page_config(page_title="Value Odds Dashboard", layout="wide")

st.title("📊 Value Odds – Match Rating Backtest Dashboard")

with st.expander("ℹ️ About This Dashboard", expanded=True):
    st.markdown("""
    A professional-grade Streamlit dashboard that analyses football match betting value using match ratings and regression-based fair odds.
    
    This dashboard is part of the **Value Odds advisory system**, designed to identify and track value bets across top global football leagues.
    
    ### 🧩 Features

    - Filter historical bets by:
      - Match Rating
      - Market (Home/Draw/Away)
      - Value Tier (Fair, Good, Excellent)
      - Season
      - League 

    - Visualise:
      - Profit/loss by Match Rating
      - ROI by Value Tier
      - Strategy trends over time

    - Download filtered data for deeper analysis

    ### ⚙️ Powered By

    - **API-Football** – for live fixtures and form data  
    - **Odds API** – for real-time market odds  
    - **In-house regression model** – trained on rolling 3-season match result data

    ### 🚀 Coming Soon

    - Live tips feed for upcoming matches
    - Text/Email alerts
    - BTTS, Over/Under, Correct Score market models
    - Premium advisory service (limited subscriptions)

    ### 📩 Contact & Access

    To request early access or join the waiting list for paid features, email:  
    **thesoccerspy@yahoo.com**
    """)

# === CONFIG ===
data_dir = "leagues"  # folder that contains your backtest CSVs like backtest_championship.csv, etc.

# === LOAD ALL BACKTEST FILES ===
backtest_files = [f for f in os.listdir(data_dir) if f.startswith("backtest_") and f.endswith(".csv")]

if not backtest_files:
    st.error("⚠️ No backtest files found in the 'leagues' folder.")
    st.stop()

dfs = []

for file in backtest_files:
    path = os.path.join(data_dir, file)
    league_name = file.replace("backtest_", "").replace(".csv", "")
    df = pd.read_csv(path)
    df["League"] = league_name
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# === SIDEBAR FILTERS ===
st.sidebar.title("🔍 Filter Matches")

leagues = df['League'].unique()
seasons = df['Season'].unique()
markets = df['Market'].unique()
values = df['Value Rating'].dropna().unique()
ratings = sorted(df['MatchRating'].dropna().unique())

selected_league = st.sidebar.multiselect("League", sorted(leagues), default=sorted(leagues))
selected_season = st.sidebar.multiselect("Season", sorted(seasons), default=sorted(seasons))
selected_market = st.sidebar.multiselect("Market", sorted(markets), default=sorted(markets))
selected_value = st.sidebar.multiselect("Value Tier", sorted(values), default=sorted(values))
selected_ratings = st.sidebar.slider("Match Rating Range", min(ratings), max(ratings), (min(ratings), max(ratings)))

# === FILTER DATA ===
filtered = df[
    (df['League'].isin(selected_league)) &
    (df['Season'].isin(selected_season)) &
    (df['Market'].isin(selected_market)) &
    (df['Value Rating'].isin(selected_value)) &
    (df['MatchRating'].between(*selected_ratings))
]

# === KPIs ===
total_bets = len(filtered)
wins = (filtered['Result'] == 'win').sum()
pl = round(filtered['P/L'].sum(), 2)
roi = round((pl / total_bets) * 100, 2) if total_bets > 0 else 0
strike_rate = round((wins / total_bets) * 100, 2) if total_bets > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Bets", total_bets)
col2.metric("Strike Rate", f"{strike_rate}%")
col3.metric("Total P/L", f"{pl} pts")

st.markdown("---")

# === CHART: P/L by Match Rating ===
if not filtered.empty:
    rating_chart = (
        filtered.groupby("MatchRating")["P/L"]
        .sum()
        .reset_index()
        .rename(columns={"P/L": "Profit"})
    )
    chart = alt.Chart(rating_chart).mark_bar().encode(
        x=alt.X("MatchRating:O", title="Match Rating"),
        y=alt.Y("Profit:Q", title="Profit (pts)"),
        tooltip=["MatchRating", "Profit"]
    ).properties(title="💹 Profit by Match Rating", height=300)
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No results match your filters.")

# === TABLE ===
st.markdown("### 📄 Filtered Results")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

# === DOWNLOAD BUTTON ===
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered CSV", data=csv, file_name="filtered_results.csv", mime='text/csv')
