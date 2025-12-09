# app.py
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Bangladesh Real-time AQI Calculator", page_icon="🌍", layout="centered")

st.title("Real-time Air Quality Index (AQI) Calculator")
st.markdown("Enter your sensor readings below to get instant AQI and health recommendations")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pollutants")
    pm25 = st.number_input("PM2.5 (µg/m³)", 0.0, 1000.0, 25.0, step=0.1)
    pm10 = st.number_input("PM10 (µg/m³)", 0.0, 1000.0, 54.0, step=0.1)
    co_ppm = st.number_input("CO (ppm)", 0.0, 50.0, 1.0, step=0.1)
    o3_ppb = st.number_input("O₃ (ppb)", 0.0, 400.0, 60.0, step=1.0)
    no2_ppb = st.number_input("NO₂ (ppb)", 0.0, 2000.0, 40.0, step=1.0)

with col2:
    st.subheader("Weather (Optional)")
    temp = st.number_input("Temperature (°C)", -10.0, 50.0, 28.0, step=0.5)
    humidity = st.number_input("Humidity (%)", 0.0, 100.0, 70.0, step=1.0)


# ==================== AQI Calculation (US EPA Standard) ====================
def calculate_sub_aqi(C, breakpoints):
    for low_c, high_c, low_i, high_i in breakpoints:
        if low_c <= C <= high_c:
            return low_i + (high_i - low_i) * (C - low_c) / (high_c - low_c)
    return 500 if C > breakpoints[-1][1] else 0


def get_aqi(pm25=None, pm10=None, co=None, o3=None, no2=None):
    aqi_list = []

    # PM2.5
    if pm25 is not None:
        bp = [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
              (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 500.4, 301, 500)]
        aqi_list.append(("PM2.5", calculate_sub_aqi(pm25, bp)))

    # PM10
    if pm10 is not None:
        bp = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
              (255, 354, 151, 200), (355, 424, 201, 300), (425, 604, 301, 500)]
        aqi_list.append(("PM10", calculate_sub_aqi(pm10, bp)))

    # CO (8-hour average in ppm)
    if co is not None:
        bp = [(0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150),
              (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300), (30.5, 50.4, 301, 500)]
        aqi_list.append(("CO", calculate_sub_aqi(co, bp)))

    # Ozone O₃ (ppb, 8-hour)
    if o3 is not None:
        bp = [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150),
              (86, 105, 151, 200), (106, 200, 201, 300), (201, 604, 301, 500)]
        aqi_list.append(("O₃", calculate_sub_aqi(o3, bp)))

    # NO₂ (ppb, 1-hour)
    if no2 is not None:
        bp = [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150),
              (361, 649, 151, 200), (650, 1249, 201, 300), (1250, 2049, 301, 500)]
        aqi_list.append(("NO₂", calculate_sub_aqi(no2, bp)))

    if not aqi_list:
        return 0, "No data"

    overall_aqi = max([val for _, val in aqi_list])
    main_pollutant = [pol for pol, val in aqi_list if val == overall_aqi][0]

    return round(overall_aqi), main_pollutant


# ==================== Predict Button ====================
if st.button("Calculate AQI", type="primary", use_container_width=True):
    aqi, pollutant = get_aqi(pm25, pm10, co_ppm, o3_ppb, no2_ppb)

    # Category & Color
    if aqi <= 50:
        category = "Good"
        color = "#00e400"
    elif aqi <= 100:
        category = "Moderate"
        color = "#ffff00"
    elif aqi <= 150:
        category = "Unhealthy for Sensitive Groups"
        color = "#ff7e00"
    elif aqi <= 200:
        category = "Unhealthy"
        color = "#ff0000"
    elif aqi <= 300:
        category = "Very Unhealthy"
        color = "#8f3f97"
    else:
        category = "Hazardous"
        color = "#7e0023"

    # Clean Gauge Chart (NO DELTA)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi,
        number={'font': {'size': 72, 'color': color}},
        gauge={
            'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': '#00e400'},
                {'range': [51, 100], 'color': '#ffff00'},
                {'range': [101, 150], 'color': '#ff7e00'},
                {'range': [151, 200], 'color': '#ff0000'},
                {'range': [201, 300], 'color': '#8f3f97'},
                {'range': [301, 500], 'color': '#7e0023'}
            ],
            'threshold': {'line': {'color': "red", 'width': 6}, 'thickness': 0.75, 'value': aqi}
        },
        title={
            'text': f"<b>AQI: {aqi}</b><br>{category}<br>Main Pollutant: {pollutant}",
            'font': {'size': 24}
        }
    ))
    fig.update_layout(height=500, margin=dict(l=20, r=20, t=80, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # Health Recommendations (English)
    st.markdown("### Health Recommendations")
    recommendations = {
        "Good": "Air quality is satisfactory. Enjoy outdoor activities!",
        "Moderate": "Air quality is acceptable. Sensitive people should consider reducing prolonged outdoor exertion.",
        "Unhealthy for Sensitive Groups": "Sensitive groups (children, elderly, asthma patients) should limit outdoor activities.",
        "Unhealthy": "Everyone may begin to experience health effects. Limit outdoor activities and wear N95 mask.",
        "Very Unhealthy": "Health alert! Avoid outdoor activities. Stay indoors with windows closed. Use air purifier.",
        "Hazardous": "Emergency conditions. Everyone must stay indoors. Wear N95/KN95 mask if going outside is unavoidable."
    }
    st.success(recommendations[category])


# Footer
st.markdown("---")
st.caption("Made with Team NetZERO Emission | Based on US EPA AQI Standards | Open Source on GitHub")
