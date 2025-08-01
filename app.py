
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page setup
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
        return float(''.join([c for c in str(dp_str) if c.isdigit() or c == '.' or c == '-']))
    except:
        return None

df["Value"] = df["DP ID"].apply(clean_dp)

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    toggle = st.toggle("Fridge Power Status", value=True)
    st.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))
    st.markdown("---")

# Metrics
st.subheader("📊 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.2f} V")
col2.metric("Avg Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.2f} W")
col3.metric("Avg Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.2f} mA")
col4.metric("Min Energy", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# Two small side-by-side charts
col5, col6 = st.columns(2)

with col5:
    st.markdown("**🍕 Event Distribution**")
    pie_labels = df["Event Details"].value_counts().index
    pie_sizes = df["Event Details"].value_counts().values
    fig1, ax1 = plt.subplots(figsize=(4, 4))
    ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

with col6:
    st.markdown("**⏱️ Power Over Time**")
    power_df = df[df["Event Details"].str.lower() == "power"].sort_values("Time")
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    ax2.plot(power_df["Time"], power_df["Value"], color="orange")
    ax2.set_ylabel("Watts")
    ax2.set_xlabel("Time")
    ax2.grid(True)
    st.pyplot(fig2)

# Area chart + bar chart
col7, col8 = st.columns(2)

with col7:
    st.markdown("**🌊 Cumulative Energy**")
    energy_df = df[df["Event Details"].str.lower() == "add electricity"].copy()
    energy_df["Cumulative kWh"] = energy_df["Value"].cumsum()
    fig3, ax3 = plt.subplots(figsize=(5, 3))
    ax3.fill_between(energy_df["Time"], energy_df["Cumulative kWh"], color='green', alpha=0.6)
    ax3.set_xlabel("Time")
    ax3.set_ylabel("kWh")
    st.pyplot(fig3)

with col8:
    st.markdown("**📅 Daily kWh Usage**")
    df["Date"] = df["Time"].dt.date
    daily = df[df["Event Details"].str.lower() == "add electricity"].groupby("Date")["Value"].sum().reset_index()
    fig4 = px.bar(daily, x="Date", y="Value", height=250, labels={"Value": "kWh"})
    st.plotly_chart(fig4, use_container_width=True)

# More compact graphs
col9, col10 = st.columns(2)

with col9:
    st.markdown("**📦 Voltage Box Plot**")
    volt_df = df[df["Event Details"].str.lower() == "voltage"]
    fig5, ax5 = plt.subplots(figsize=(4, 3))
    sns.boxplot(x=volt_df["Value"], ax=ax5, color="lightblue")
    ax5.set_title("Voltage Distribution")
    st.pyplot(fig5)

with col10:
    st.markdown("**🔥 Hourly Energy Heatmap**")
    energy_df["Hour"] = energy_df["Time"].dt.hour
    energy_df["Date"] = energy_df["Time"].dt.date
    heatmap_data = energy_df.pivot_table(values="Value", index="Hour", columns="Date", aggfunc="sum")
    fig6, ax6 = plt.subplots(figsize=(5, 3))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax6)
    ax6.set_title("Hourly kWh Usage")
    st.pyplot(fig6)

# Final row
st.markdown("---")
col11, col12 = st.columns(2)

with col11:
    st.markdown("**📈 Dual Line: Power vs Voltage**")
    voltage_df = df[df["Event Details"].str.lower() == "voltage"].sort_values("Time")
    fig7, ax7 = plt.subplots(figsize=(5, 3))
    ax7.plot(power_df["Time"], power_df["Value"], color="red", label="Power (W)")
    ax7.set_ylabel("Power (W)", color="red")
    ax8 = ax7.twinx()
    ax8.plot(voltage_df["Time"], voltage_df["Value"], color="blue", label="Voltage (V)")
    ax8.set_ylabel("Voltage (V)", color="blue")
    fig7.tight_layout()
    st.pyplot(fig7)

with col12:
    st.markdown("**🧮 Power vs Voltage Scatter**")
    merged = pd.merge(power_df, voltage_df, on="Time", suffixes=("_power", "_voltage"))
    fig8 = px.scatter(merged, x="Value_voltage", y="Value_power", height=300,
                      labels={"Value_voltage": "Voltage (V)", "Value_power": "Power (W)"})
    st.plotly_chart(fig8, use_container_width=True)

# Device Status
st.markdown("### 🧲 Fridge Control: {}".format("🟢 ON" if toggle else "🔴 OFF"))

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Developed by Shanzia Shabnom Mithun | CSE407 - Green Computing</div>", unsafe_allow_html=True)
