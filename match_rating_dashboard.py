import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Value Odds Dashboard", layout="wide")

# === LOAD DATA ===
df = pd.read_csv("championship_rating_backtest.csv")

# === HEADER ===
st.markdown("""
<style>
    .main { background-color: #f9f9f9; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("Value Odds – Match Rating Betting Dashboard")
st.caption("Explore profit/loss by match rating, market, season, and value tier")

# === SIDEBAR FILTERS ===
st.sidebar.header("Filter Options")

seasons = df['Season'].unique().tolist()
markets = df['Market'].unique().tolist()
ratings = sorted(df['MatchRating'].unique())
tiers = df['Value Rating'].unique().tolist()

selected_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)
selected_markets = st.sidebar.multiselect("Market", markets, default=markets)
selected_tiers = st.sidebar.multiselect("Value Tier", tiers, default=tiers)
rating_range = st.sidebar.slider("Match Rating Range", min_value=min(ratings), max_value=max(ratings), value=(min(ratings), max(ratings)))
exclude_draws = st.sidebar.checkbox("Exclude Draws", value=False)

# === APPLY FILTERS ===
filtered = df[
    (df['Season'].isin(selected_seasons)) &
    (df['Market'].isin(selected_markets)) &
    (df['Value Rating'].isin(selected_tiers)) &
    (df['MatchRating'] >= rating_range[0]) &
    (df['MatchRating'] <= rating_range[1])
]

if exclude_draws:
    filtered = filtered[filtered['Market'] != 'Draw']

# === METRICS ===
total_bets = len(filtered)
total_profit = filtered['P/L'].sum()
strike_rate = (filtered['Result'] == 'win').mean() * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Bets", total_bets)
col2.metric("Total Profit", round(total_profit, 2))
col3.metric("Strike Rate", f"{strike_rate:.2f}%")

# === TABS ===
tab1, tab2, tab3 = st.tabs(["Performance", "Strategy Explorer", "Filtered Data"])

# === TAB 1: PERFORMANCE ===
with tab1:
    st.subheader("Profit by Match Rating")
    rating_profit = filtered.groupby('MatchRating')['P/L'].sum().reset_index()
    chart = alt.Chart(rating_profit).mark_bar().encode(
        x=alt.X('MatchRating:O', title="Match Rating"),
        y=alt.Y('P/L:Q', title="Total Profit"),
        tooltip=['MatchRating', 'P/L']
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("ROI by Value Tier")
    roi_tier = filtered.groupby('Value Rating').agg({
        'P/L': 'sum',
        'Result': lambda x: (x == 'win').sum()
    }).reset_index()
    roi_tier['Bets'] = filtered['Value Rating'].value_counts().reindex(roi_tier['Value Rating']).values
    roi_tier['ROI'] = roi_tier['P/L'] / roi_tier['Bets'] * 100

    chart2 = alt.Chart(roi_tier).mark_bar().encode(
        x=alt.X('Value Rating', title="Value Tier"),
        y=alt.Y('ROI', title="ROI %"),
        tooltip=['Bets', 'P/L', 'ROI']
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart2, use_container_width=True)

# === TAB 2: STRATEGY EXPLORER ===
with tab2:
    st.subheader("Profit by Season and Market")
    summary = filtered.groupby(['Season', 'Market'])['P/L'].sum().reset_index()
    chart3 = alt.Chart(summary).mark_bar().encode(
        x=alt.X('Season:N'),
        y='P/L:Q',
        color='Market:N',
        column='Market:N',
        tooltip=['Season', 'Market', 'P/L']
    ).properties(
        width=200
    )
    st.altair_chart(chart3, use_container_width=True)

# === TAB 3: RAW DATA ===
with tab3:
    st.subheader("Filtered Bets")
    st.dataframe(filtered[['Date', 'Fixture', 'Season', 'Market', 'MatchRating', 'Available Odds', 'Fair Odds', 'Value Rating', 'Result', 'P/L']])