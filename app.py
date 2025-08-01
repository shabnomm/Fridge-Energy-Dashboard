
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Fridge Energy Dashboard", layout="wide")
st.title("⚡ Power Monitoring Dashboard")

# Load dataset
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip()
df["Event Details"] = df["Event Details"].str.strip()
df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
df = df.dropna(subset=["Time", "Event Details", "DP ID"])

# Clean DP ID values
def clean_dp(dp_str):
    try:
        return float(''.join([c for c in str(dp_str) if c.isdigit() or c == '.' or c == '-']))
    except:
        return None

df["Value"] = df["DP ID"].apply(clean_dp)

# Sidebar toggle
st.sidebar.header("PowerFilter")
toggle = st.sidebar.toggle("Fridge Power Status", value=True)
st.sidebar.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))

# Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Voltage", f"{df[df['Event Details'].str.lower()=='voltage']['Value'].mean():.2f} V")
col2.metric("Average Power", f"{df[df['Event Details'].str.lower()=='power']['Value'].mean():.2f} W")
col3.metric("Average Current", f"{df[df['Event Details'].str.lower()=='current']['Value'].mean():.2f} mA")
col4.metric("Min Electricity", f"{df[df['Event Details'].str.lower()=='add electricity']['Value'].min():.2f} kWh")

# Pie chart
st.subheader("Energy Consumption by Type")
pie_labels = df["Event Details"].value_counts().index
pie_sizes = df["Event Details"].value_counts().values

fig1, ax1 = plt.subplots()
ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# Time trends
st.subheader("Trends by Localtime")
event_groups = ["voltage", "power", "current", "add electricity"]

for event in event_groups:
    st.markdown(f"**Average {event.capitalize()} by Localtime**")
    subset = df[df["Event Details"].str.lower() == event].copy()
    subset["Localtime"] = subset["Time"].dt.strftime("%H:%M")
    grouped = subset.groupby("Localtime")["Value"].mean()
    st.line_chart(grouped)

# Summary table
st.subheader("Daily Summary Table")
df["Date"] = df["Time"].dt.date
daily = df[df["Event Details"].str.lower() == "add electricity"].groupby("Date")["Value"].sum().reset_index()
daily.columns = ["Date", "Total kWh"]
st.dataframe(daily)

# Status
st.subheader("Device Control")
st.write("Power is currently: ", "🟢 ON" if toggle else "🔴 OFF")
