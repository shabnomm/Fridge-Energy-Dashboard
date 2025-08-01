
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Setup
st.set_page_config(page_title="Fridge Energy Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>⚡ Fridge Energy Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Load data
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip()
df["Event Details"] = df["Event Details"].str.strip()
df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
df = df.dropna(subset=["Time", "Event Details", "DP ID"])

def clean_dp(dp_str):
    try:
        return float(''.join([c for c in str(dp_str) if c.isdigit() or c=='.' or c=='-']))
    except:
        return None

df["Value"] = df["DP ID"].apply(clean_dp)

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    toggle = st.toggle("Fridge Power Status", value=True)
    st.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))

# Summary metrics
st.subheader("📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.2f} V")
col2.metric("Avg Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.2f} W")
col3.metric("Avg Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.2f} mA")
col4.metric("Min Energy", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# General Patterns section
st.markdown("### 📈 General Patterns")
colA, colB = st.columns(2)
with colA:
    st.markdown("**🍕 Event Distribution**")
    df_counts = df["Event Details"].value_counts()
    fig, ax = plt.subplots(figsize=(3,3))
    ax.pie(df_counts.values, labels=df_counts.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
with colB:
    st.markdown("**⏱️ Power Over Time**")
    power_df = df[df["Event Details"].str.lower()=="power"].sort_values("Time")
    fig, ax = plt.subplots(figsize=(4,2.5))
    ax.plot(power_df["Time"], power_df["Value"], color="orange")
    ax.set_xlabel("Time"); ax.set_ylabel("Watts")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# Cumulative Energy
st.markdown("**🌊 Cumulative Energy**")
energy_df = df[df["Event Details"].str.lower()=="add electricity"].copy()
energy_df["Cumulative kWh"] = energy_df["Value"].cumsum()
fig, ax = plt.subplots(figsize=(4,2.5))
ax.fill_between(energy_df["Time"], energy_df["Cumulative kWh"], color="green", alpha=0.6)
ax.set_xlabel("Time"); ax.set_ylabel("kWh")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Daily Trends section
st.markdown("### 📅 Daily Trends")
colC, colD = st.columns(2)
with colC:
    st.markdown("**📅 Daily Usage**")
    df["Date"] = df["Time"].dt.date
    daily = df[df["Event Details"].str.lower()=="add electricity"].groupby("Date")["Value"].sum().reset_index()
    fig = px.bar(daily, x="Date", y="Value", labels={"Value":"kWh"}, height=250)
    st.plotly_chart(fig, use_container_width=True)
with colD:
    st.markdown("**📦 Voltage Distribution**")
    volt_df = df[df["Event Details"].str.lower()=="voltage"]
    fig, ax = plt.subplots(figsize=(3.5,2.5))
    sns.boxplot(x=volt_df["Value"], ax=ax, color="lightblue")
    st.pyplot(fig)

# Hourly Heatmap
st.markdown("**🔥 Hourly Heatmap**")
energy_df["Hour"] = energy_df["Time"].dt.hour
heatmap_data = energy_df.pivot_table(index="Hour", columns="Date", values="Value", aggfunc="sum", fill_value=0)
fig, ax = plt.subplots(figsize=(4,2.5))
sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
ax.set_ylabel("Hour"); ax.set_xlabel("Date")
plt.xticks(rotation=45)
st.pyplot(fig)

# Comparative Insights
st.markdown("### 🧪 Comparative Insights")
colE, colF = st.columns(2)
with colE:
    st.markdown("**📈 Power vs Voltage Over Time**")
    voltage_df = df[df["Event Details"].str.lower()=="voltage"].sort_values("Time")
    fig, ax = plt.subplots(figsize=(4,2.5))
    ax.plot(power_df["Time"], power_df["Value"], color="red", label="Power")
    ax.set_ylabel("Power", color="red")
    ax2 = ax.twinx()
    ax2.plot(voltage_df["Time"], voltage_df["Value"], color="blue", label="Voltage")
    ax2.set_ylabel("Voltage", color="blue")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
with colF:
    st.markdown("**🧮 Power vs Voltage Scatter**")
    merged = pd.merge(power_df, voltage_df, on="Time", suffixes=("_p","_v"))
    fig = px.scatter(merged, x="Value_v", y="Value_p", labels={"Value_v":"Voltage","Value_p":"Power"}, height=250)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:gray;'>Shanzia Shabnom Mithun | CSE407</div>", unsafe_allow_html=True)
