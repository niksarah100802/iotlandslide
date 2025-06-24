import streamlit as st
import pandas as pd
import altair as alt

# Page setup
st.set_page_config(page_title="Landslide IoT Monitoring", layout="wide")
st.title("🌧️ Landslide Monitoring Dashboard")

# Define threat level classification
def classify_threat_level(row):
    if row['tilt_angle_deg'] > 10 or row['soil_moisture_pct'] > 50 or row['rainfall_mm'] > 40:
        return 'HIGH'
    elif row['tilt_angle_deg'] > 5 or row['soil_moisture_pct'] > 30 or row['rainfall_mm'] > 30:
        return 'LOW'
    else:
        return 'MILD'

# Sidebar - file upload
st.sidebar.header("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Process after upload button click
if st.sidebar.button("Upload and Analyze"):
    if uploaded_file is not None:
        # Load data
        df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

        # Classify if needed
        if 'threat_level' not in df.columns:
            df['threat_level'] = df.apply(classify_threat_level, axis=1)

        # Sidebar filter for threat level
        st.sidebar.subheader("Filter by Threat Level")
        levels = ['MILD', 'LOW', 'HIGH']
        selected_levels = st.sidebar.multiselect("Select levels to view:", levels, default=levels)

        # Filtered DataFrame
        filtered_df = df[df['threat_level'].isin(selected_levels)]

        # Show latest metrics
        st.subheader("📊 Latest Sensor Readings")
        latest = df.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tilt Angle (°)", f"{latest['tilt_angle_deg']:.2f}")
        col2.metric("Soil Moisture (%)", f"{latest['soil_moisture_pct']:.2f}")
        col3.metric("Rainfall (mm)", f"{latest['rainfall_mm']:.2f}")
        col4.metric("Threat Level", latest['threat_level'])

        # Line chart of sensor values over time
        st.subheader("📈 Sensor Trends Over Time")
        chart = alt.Chart(filtered_df).transform_fold(
            ['tilt_angle_deg', 'soil_moisture_pct', 'rainfall_mm']
        ).mark_line().encode(
            x='timestamp:T',
            y='value:Q',
            color='key:N'
        ).properties(width=900, height=400)
        st.altair_chart(chart, use_container_width=True)

        # Bar chart of threat level distribution
        st.subheader("📊 Threat Level Distribution")
        threat_count = filtered_df['threat_level'].value_counts().reset_index()
        threat_count.columns = ['Threat Level', 'Count']
        st.bar_chart(threat_count.set_index('Threat Level'))

        # Raw data table
        st.subheader("🧾 Raw Data")
        st.dataframe(filtered_df.tail(50), use_container_width=True)

        # Download button
        st.download_button(
            label="Download Filtered CSV",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_landslide_data.csv",
            mime='text/csv'
        )
    else:
        st.warning("⚠️ Please upload a CSV file first.")
