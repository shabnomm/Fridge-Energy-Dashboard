
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Fridge Energy Dashboard", layout="wide")
st.title("⚡ Power Monitoring Dashboard")

# Load dataset
df = pd.read_csv("data.csv", parse_dates=["Time"])
df.dropna(inplace=True)

# Convert DP ID to float
df["DP ID"] = df["DP ID"].str.replace("mA", "").str.replace("W", "").str.replace("V", "").str.replace("kwh", "")
df["DP ID"] = pd.to_numeric(df["DP ID"], errors="coerce")

# Sidebar filter
st.sidebar.header("PowerFilter")
toggle = st.sidebar.toggle("Fridge Power Status", value=True)
st.sidebar.markdown("### Status: {}".format("🟢 ON" if toggle else "🔴 OFF"))

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Voltage", f"{df[df['Event Details']=='Voltage']['DP ID'].mean():.2f} V")
col2.metric("Average Power", f"{df[df['Event Details']=='Power']['DP ID'].mean():.2f} W")
col3.metric("Average Current", f"{df[df['Event Details']=='Current']['DP ID'].mean():.2f} mA")
col4.metric("Min Electricity", f"{df[df['Event Details']=='Add Electricity']['DP ID'].min():.2f} kWh")

# Pie chart
st.subheader("Energy Consumption by Type")
pie_labels = df["Event Details"].value_counts().index
pie_sizes = df["Event Details"].value_counts().values

fig1, ax1 = plt.subplots()
ax1.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# Time-based trends
st.subheader("Trends by Localtime")
event_groups = ["Voltage", "Power", "Current", "Add Electricity"]

for event in event_groups:
    st.markdown(f"**Average {event} by Localtime**")
    subset = df[df["Event Details"] == event].copy()
    subset["Localtime"] = subset["Time"].dt.strftime("%H:%M")
    grouped = subset.groupby("Localtime")["DP ID"].mean()
    st.line_chart(grouped)

# Summary table
st.subheader("Daily Summary Table")
df["Date"] = df["Time"].dt.date
daily = df[df["Event Details"] == "Add Electricity"].groupby("Date")["DP ID"].sum().reset_index()
daily.columns = ["Date", "Total kWh"]
st.dataframe(daily)

# Device status
st.subheader("Device Control")
st.write("Power is currently: ", "🟢 ON" if toggle else "🔴 OFF")
