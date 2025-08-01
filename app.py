
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Setup
st.set_page_config(page_title="Fridge Dashboard", layout="wide")
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

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    toggle = st.toggle("Fridge Power Status", value=True)
    st.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))

# Summary
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.2f} V")
col2.metric("Avg Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.2f} W")
col3.metric("Avg Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.2f} mA")
col4.metric("Min Energy", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# Section 1: Pie + Power Line + Area
st.markdown("### 📈 General Patterns")

colA, colB = st.columns(2)
with colA:
    st.markdown("**🍕 Event Type Distribution**")
    st.caption("Proportion of each event type (voltage, power, etc.)")
    pie_labels = df["Event Details"].value_counts().index
    pie_sizes = df["Event Details"].value_counts().values
    fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
    ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

with colB:
    st.markdown("**⏱️ Power Over Time**")
    st.caption("How the fridge's power usage changes over time")
    power_df = df[df["Event Details"].str.lower() == "power"].sort_values("Time")
    fig2, ax2 = plt.subplots(figsize=(4, 2.5))
    ax2.plot(power_df["Time"], power_df["Value"], color="orange")
    ax2.set_ylabel("Watts")
    ax2.set_xlabel("Time")
    ax2.grid(True)
    st.pyplot(fig2)

st.markdown("**🌊 Cumulative Energy**")
st.caption("Running total of energy usage over time")

energy_df = df[df["Event Details"].str.lower() == "add electricity"].copy()
energy_df["Cumulative kWh"] = energy_df["Value"].cumsum()

fig3, ax3 = plt.subplots(figsize=(3.5, 2))  # 📏 Make graph smaller
ax3.fill_between(energy_df["Time"], energy_df["Cumulative kWh"], color='green', alpha=0.7)
ax3.set_xlabel("Time")
ax3.set_ylabel("kWh")
ax3.tick_params(axis='x', rotation=45)  # 🔄 Rotate x-axis labels
fig3.tight_layout()  # ✅ Prevents overlapping and padding issues
st.pyplot(fig3)

# Section 2: Bar + Box + Heatmap
st.markdown("### 📅 Daily Trends")

colC, colD = st.columns(2)
with colC:
    st.markdown("**📅 Daily Energy Usage**")
    st.caption("Energy used per day (kWh)")
    df["Date"] = df["Time"].dt.date
    daily = df[df["Event Details"].str.lower() == "add electricity"].groupby("Date")["Value"].sum().reset_index()
    fig4 = px.bar(daily, x="Date", y="Value", labels={"Value": "kWh"}, height=250)
    st.plotly_chart(fig4, use_container_width=True)

with colD:
    st.markdown("**📦 Voltage Distribution**")
    st.caption("Boxplot showing voltage ranges and outliers")
    volt_df = df[df["Event Details"].str.lower() == "voltage"]
    fig5, ax5 = plt.subplots(figsize=(3.5, 2.5))
    sns.boxplot(x=volt_df["Value"], ax=ax5, color="lightblue")
    st.pyplot(fig5)

st.markdown("**🔥 Hourly Heatmap**")
st.caption("Hour-by-hour energy use intensity")
energy_df["Hour"] = energy_df["Time"].dt.hour
energy_df["Date"] = energy_df["Time"].dt.date
heatmap_data = energy_df.pivot_table(values="Value", index="Hour", columns="Date", aggfunc="sum")
fig6, ax6 = plt.subplots(figsize=(4, 2.5))
sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax6)
st.pyplot(fig6)

# Section 3: Dual + Scatter
st.markdown("### 🧪 Comparative Insights")

colE, colF = st.columns(2)
with colE:
    st.markdown("**📈 Power vs Voltage Over Time**")
    st.caption("Dual-line comparison on same timeline")
    voltage_df = df[df["Event Details"].str.lower() == "voltage"].sort_values("Time")
    fig7, ax7 = plt.subplots(figsize=(4, 2.5))
    ax7.plot(power_df["Time"], power_df["Value"], color="red", label="Power (W)")
    ax7.set_ylabel("Power", color="red")
    ax8 = ax7.twinx()
    ax8.plot(voltage_df["Time"], voltage_df["Value"], color="blue", label="Voltage (V)")
    ax8.set_ylabel("Voltage", color="blue")
    st.pyplot(fig7)

with colF:
    st.markdown("**🧮 Power vs Voltage Scatter**")
    st.caption("Relationship between voltage and power draw")
    merged = pd.merge(power_df, voltage_df, on="Time", suffixes=("_power", "_voltage"))
    fig8 = px.scatter(merged, x="Value_voltage", y="Value_power", height=250,
                      labels={"Value_voltage": "Voltage (V)", "Value_power": "Power (W)"})
    st.plotly_chart(fig8, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Refined by Shanzia Shabnom Mithun • CSE407</div>", unsafe_allow_html=True)
