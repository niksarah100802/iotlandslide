import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# Classify threat levels based on sensor values
def classify_threat_level(row):
    if row['tilt_angle_deg'] > 10 or row['soil_moisture_pct'] > 90 or row['rainfall_mm'] > 40:
        return 'DANGER'
    elif row['tilt_angle_deg'] > 5 or row['soil_moisture_pct'] > 70 or row['rainfall_mm'] > 30:
        return 'MEDIUM'
    else:
        return 'MILD'

# Load data
st.set_page_config(page_title="Landslide IoT Monitoring Dashboard", layout="wide")
st.title("🚨 Landslide Monitoring Dashboard - Genting Highlands Road")

# File uploader
st.sidebar.header("Upload Your CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Add an upload button to trigger loading
if st.sidebar.button("Upload and Process"):
    if uploaded_file:
        df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

        # Classify threat levels if not in CSV
        if 'threat_level' not in df.columns:
            df['threat_level'] = df.apply(classify_threat_level, axis=1)

        # Sidebar filter
        st.sidebar.header("Filters")
        threat_filter = st.sidebar.multiselect("Select Threat Levels:", ['MILD', 'MEDIUM', 'DANGER'], default=['MILD', 'MEDIUM', 'DANGER'])
        df_filtered = df[df['threat_level'].isin(threat_filter)]

        # Show latest threat level
        latest = df.iloc[-1]
        st.metric("Latest Tilt Angle (deg)", f"{latest['tilt_angle_deg']:.2f}")
        st.metric("Latest Soil Moisture (%)", f"{latest['soil_moisture_pct']:.2f}")
        st.metric("Latest Rainfall (mm)", f"{latest['rainfall_mm']:.2f}")
        st.metric("Current Threat Level", latest['threat_level'])

        # Time-series visualization
        st.subheader("Sensor Readings Over Time")
        chart = alt.Chart(df_filtered).transform_fold(
            ['tilt_angle_deg', 'soil_moisture_pct', 'rainfall_mm']
        ).mark_line().encode(
            x='timestamp:T',
            y='value:Q',
            color='key:N'
        ).properties(
            width=900,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)

        # Threat level distribution
        st.subheader("Threat Level Distribution")
        threat_count = df_filtered['threat_level'].value_counts().reset_index()
        threat_count.columns = ['Threat Level', 'Count']
        st.bar_chart(threat_count.set_index('Threat Level'))

        # Data table
        st.subheader("Raw Data Table")
        st.dataframe(df_filtered.tail(50), use_container_width=True)

        # Downloadable data
        st.download_button("Download CSV", data=df_filtered.to_csv(index=False), file_name="landslide_sensor_data_filtered.csv")
    else:
        st.warning("Please upload a CSV file to proceed.")
