
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Setup
st.set_page_config(page_title="Fridge Dashboard", layout="wide")
st.markdown("<style>body {background-color: #1e1e1e; color: #f5f5f5;}</style>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #f5f5f5;'>⚡ Minimal Fridge Energy Dashboard</h2>", unsafe_allow_html=True)
st.markdown("---")

# Load and prepare data
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip()
df["Event Details"] = df["Event Details"].str.strip()
df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
df = df.dropna(subset=["Time", "Event Details", "DP ID"])

def clean_dp(dp_str):
    try:
        return float(''.join([c for c in str(dp_str) if c.isdigit() or c == '.' or c == '-']))
    except:
        return None

df["Value"] = df["DP ID"].apply(clean_dp)

# Sidebar controls
with st.sidebar:
    toggle = st.toggle("Power Status", value=True)
    st.write("Status:", "🟢 ON" if toggle else "🔴 OFF")

# Metric summary
st.markdown("### 📊 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.1f} V")
col2.metric("Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.1f} W")
col3.metric("Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.1f} mA")
col4.metric("Min Energy", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# Graph layout
colA, colB = st.columns(2)

with colA:
    st.markdown("#### 🍕 Event Type Distribution")
    st.caption("Shows how many times each sensor type (Voltage, Power, etc.) was recorded.")
    fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
    pie_labels = df["Event Details"].value_counts().index
    pie_sizes = df["Event Details"].value_counts().values
    ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

with colB:
    st.markdown("#### ⏱️ Power Trend")
    st.caption("Visualizes how the power usage changed over time.")
    power_df = df[df["Event Details"].str.lower() == "power"].sort_values("Time")
    fig2, ax2 = plt.subplots(figsize=(4.5, 2.5))
    ax2.plot(power_df["Time"], power_df["Value"], color="#ffcc00", linewidth=1)
    ax2.set_facecolor("#1e1e1e")
    ax2.tick_params(colors='white')
    ax2.set_title("Power (W)", color='white')
    st.pyplot(fig2)

colC, colD = st.columns(2)

with colC:
    st.markdown("#### 🌊 Cumulative Energy")
    st.caption("Shows how energy consumption adds up over time.")
    energy_df = df[df["Event Details"].str.lower() == "add electricity"].copy()
    energy_df["Cumulative"] = energy_df["Value"].cumsum()
    fig3, ax3 = plt.subplots(figsize=(4, 2.5))
    ax3.fill_between(energy_df["Time"], energy_df["Cumulative"], color='#29a19c', alpha=0.7)
    ax3.set_facecolor("#1e1e1e")
    ax3.tick_params(colors='white')
    ax3.set_title("Total Energy (kWh)", color='white')
    st.pyplot(fig3)

with colD:
    st.markdown("#### 📅 Daily Usage")
    st.caption("Displays total energy used per day.")
    df["Date"] = df["Time"].dt.date
    daily = df[df["Event Details"].str.lower() == "add electricity"].groupby("Date")["Value"].sum().reset_index()
    fig4 = px.bar(daily, x="Date", y="Value", labels={"Value": "kWh"}, height=250)
    fig4.update_layout(plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e", font_color="white")
    st.plotly_chart(fig4, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Minimal Dashboard • CSE407 Project • Developed by Shanzia Shabnom Mithun</div>", unsafe_allow_html=True)
