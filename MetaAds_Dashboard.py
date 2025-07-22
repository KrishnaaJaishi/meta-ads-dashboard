#!/usr/bin/env python
# coding: utf-8

# # Meta Ads Dashboard
# Interactive visual dashboard for Meta ads performance using Supabase data.

# In[20]:


import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# Supabase credentials
# Setup your credentials
url = "https://mwxipprqzljrhwbhlmuf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im13eGlwcHJxemxqcmh3YmhsbXVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxNTkyMDAsImV4cCI6MjA2ODczNTIwMH0.qFmt8xB7qRLUoC7SG6IDAB4lKdkUOIU-wU-kFRAd8sg"  # safe if RLS is on
supabase: Client = create_client(url, key)

# Load from Supabase
response = supabase.table('MetaAds').select("*").execute()
df = pd.DataFrame(response.data)


# In[21]:


# Convert 'day', 'start', 'reporting_start', 'reporting_end' from text to datetime

df['day'] = pd.to_datetime(df['day'], errors='coerce', dayfirst=True)
df['start'] = pd.to_datetime(df['start'], errors='coerce', dayfirst=True)
df['reporting_start'] = pd.to_datetime(df['reporting_start'], errors='coerce', dayfirst=True)
df['reporting_end'] = pd.to_datetime(df['reporting_end'], errors='coerce', dayfirst=True)


# In[22]:


import streamlit as st
import pandas as pd
import plotly.express as px


# Streamlit UI controls
st.sidebar.header("Filter Options")

min_date = df['day'].min()
max_date = df['day'].max()

start_date = st.sidebar.date_input('Start Date', min_date)
end_date = st.sidebar.date_input('End Date', max_date)

campaign_options = ['All'] + sorted(df['campaign'].unique())
selected_campaign = st.sidebar.selectbox('Campaign', campaign_options, index=0)

if start_date > end_date:
    st.error("❗ Start date must be before end date.")
    st.stop()

# Filter data
filtered = df[(df['day'] >= pd.to_datetime(start_date)) & (df['day'] <= pd.to_datetime(end_date))]
if selected_campaign != 'All':
    filtered = filtered[filtered['campaign'] == selected_campaign]

if filtered.empty:
    st.warning("⚠️ No data available for this date range or campaign.")
    st.stop()

filtered = filtered.copy()
filtered['roi'] = filtered['results'] / filtered['amount_spent'].replace(0, pd.NA)

st.title("📊 Meta Ads Dashboard")

# Visual 1: Daily Spend
fig1 = px.line(filtered, x='day', y='amount_spent', title='💰 Daily Ad Spend Over Time', color='campaign', markers=True)
st.plotly_chart(fig1, use_container_width=True)

# Visual 2: Daily Results
fig2 = px.bar(filtered, x='day', y='results', title='📈 Daily Results (Leads)', color='campaign')
st.plotly_chart(fig2, use_container_width=True)

# Visual 3: Cost Per Result
fig3 = px.line(filtered, x='day', y='cost_per_result', title='💸 Cost Per Lead Over Time', color='campaign', markers=True)
st.plotly_chart(fig3, use_container_width=True)

# Visual 4: CTR Trend
fig4 = px.line(filtered, x='day', y='ctr', title='🔁 CTR (Click-Through Rate) Trend', color='campaign', markers=True)
st.plotly_chart(fig4, use_container_width=True)

# Visual 5: ROI (Results / Spend)
fig5 = px.line(filtered, x='day', y='roi', title='📊 ROI (Results per Dollar Spent)', color='campaign', markers=True)
st.plotly_chart(fig5, use_container_width=True)

# Visual 6: Reach vs Impressions
reach_impressions = filtered.groupby("campaign")[["reach", "impressions"]].sum().reset_index()
fig6 = px.bar(reach_impressions, x="campaign", y=["reach", "impressions"], barmode="group", title="👥 Reach vs Impressions per Campaign")
st.plotly_chart(fig6, use_container_width=True)

# Visual 7: Daily Link Clicks
df_clicks = filtered.groupby("day")["link_clicks"].sum().reset_index()
fig7 = px.line(df_clicks, x="day", y="link_clicks", title="🖱️ Daily Link Clicks Over Time", markers=True, color_discrete_sequence=px.colors.qualitative.Dark24)
st.plotly_chart(fig7, use_container_width=True)

# Visual 8: Daily Spend (again for context)
df_spend = filtered.groupby("day")["amount_spent"].sum().reset_index()
fig8 = px.line(df_spend, x="day", y="amount_spent", title="📆 Total Money Spent Over Time", markers=True, color_discrete_sequence=px.colors.qualitative.Bold)
st.plotly_chart(fig8, use_container_width=True)

# Daily Summary
daily_summary = filtered.groupby('day')[['amount_spent', 'reach', 'impressions', 'link_clicks']].sum().reset_index()

# Visual 9a: Daily Reach vs Impressions
fig9a = px.line(
    daily_summary.melt(id_vars='day', value_vars=['reach', 'impressions'],
                       var_name='Metric', value_name='Value'),
    x='day', y='Value', color='Metric',
    title="📈 Daily Reach vs Impressions",
    markers=True,
    color_discrete_map={
        'reach': '#06D6A0',
        'impressions': '#118AB2'
    }
)
fig9a.update_layout(xaxis_title="Date", yaxis_title="Count", template="plotly_white")
st.plotly_chart(fig9a, use_container_width=True)

# Visual 9b: Daily Spend vs Link Clicks
fig9b = px.line(
    daily_summary.melt(id_vars='day', value_vars=['amount_spent', 'link_clicks'],
                       var_name='Metric', value_name='Value'),
    x='day', y='Value', color='Metric',
    title="💰 Daily Spend vs Link Clicks",
    markers=True,
    color_discrete_map={
        'amount_spent': '#EF476F',
        'link_clicks': '#FFD166'
    }
)
fig9b.update_layout(xaxis_title="Date", yaxis_title="Value", template="plotly_white")
st.plotly_chart(fig9b, use_container_width=True)

# KPI Summary
total_spent = filtered['amount_spent'].sum()
total_results = filtered['results'].sum()
avg_cost = total_spent / total_results if total_results > 0 else 0
avg_ctr = filtered['ctr'].mean()

st.markdown(f"""
### 🔢 KPI Summary
- 💰 Total Spent: ${total_spent:.2f}
- 📈 Total Results (Leads): {total_results}
- 💸 Avg Cost per Result: ${avg_cost:.2f}
- 🔁 Avg CTR: {avg_ctr:.2f}%
""")


# In[ ]:




