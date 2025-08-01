
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Fridge Energy Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>⚡ Fridge Energy Monitoring Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Load and clean data
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
    st.header("⚙️ Settings")
    toggle = st.toggle("Fridge Power Status", value=True)
    st.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))
    st.markdown("---")
    st.image("https://cdn-icons-png.flaticon.com/512/2813/2813676.png", width=100)

# Metrics Section
st.subheader("📊 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.2f} V")
col2.metric("Average Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.2f} W")
col3.metric("Average Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.2f} mA")
col4.metric("Min Electricity", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# Charts
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📈 Energy Consumption by Type")
    pie_labels = df["Event Details"].value_counts().index
    pie_sizes = df["Event Details"].value_counts().values
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

with col_b:
    st.markdown("### ⏱️ Power Trend Over Time")
    power_df = df[df["Event Details"].str.lower() == "power"].sort_values("Time")
    fig2, ax2 = plt.subplots()
    ax2.plot(power_df["Time"], power_df["Value"], color="orange")
    ax2.set_ylabel("Watts")
    ax2.set_xlabel("Time")
    ax2.grid(True)
    st.pyplot(fig2)

# Trend charts for each type
with st.expander("📉 Detailed Trends by Local Time", expanded=False):
    event_groups = ["voltage", "power", "current", "add electricity"]
    for event in event_groups:
        st.markdown(f"**Average {event.capitalize()} by Localtime**")
        subset = df[df["Event Details"].str.lower() == event].copy()
        subset["Localtime"] = subset["Time"].dt.strftime("%H:%M")
        grouped = subset.groupby("Localtime")["Value"].mean()
        st.line_chart(grouped)

# Daily Summary
st.markdown("---")
st.markdown("### 📅 Daily Energy Usage Summary")
df["Date"] = df["Time"].dt.date
daily = df[df["Event Details"].str.lower() == "add electricity"].groupby("Date")["Value"].sum().reset_index()
daily.columns = ["Date", "Total kWh"]
st.dataframe(daily)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Developed by Shanzia Shabnom Mithun | CSE407 - Green Computing</div>", unsafe_allow_html=True)
