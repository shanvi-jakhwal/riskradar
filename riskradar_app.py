import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="RiskRadar - Forest Fire Risk Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-card {
        background-color: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-width: 900px;
        margin: 20px auto;
    }
    .header-strip {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
        font-size: 28px;
        font-weight: bold;
    }
    .location-text {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 20px;
    }
    .zone-title {
        text-align: center;
        font-size: 48px;
        font-weight: bold;
        margin: 30px 0;
    }
    .risk-score-text {
        text-align: center;
        font-size: 24px;
        color: #333;
        margin-bottom: 20px;
    }
    .star-container {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin: 30px 0;
    }
    .star-rating {
        font-size: 40px;
        letter-spacing: 8px;
    }
    .alert-box {
        padding: 20px;
        border-radius: 12px;
        margin-top: 30px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    .alert-safe {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .alert-moderate {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .alert-danger {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    </style>
""", unsafe_allow_html=True)

# Location coordinates database
LOCATION_COORDS = {
    "Patiala, Punjab": {"lat": 30.3398, "lon": 76.3869, "fire_prob": 0.25},
    "Dehradun, Uttarakhand": {"lat": 30.3165, "lon": 78.0322, "fire_prob": 0.45},
    "Nagpur, Maharashtra": {"lat": 21.1458, "lon": 79.0882, "fire_prob": 0.35},
    "Shimla, Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734, "fire_prob": 0.40}
}

def get_heatmap_data(location, risk_score):
    """
    Generate simulated heatmap data based on location and risk score.
    Later this will fetch real hotspot data from database.
    Returns list of [latitude, longitude, intensity]
    """
    coords = LOCATION_COORDS[location]
    base_lat = coords["lat"]
    base_lon = coords["lon"]
    
    # Generate random hotspots around the location
    np.random.seed(42)  # For consistency
    num_hotspots = int(15 + risk_score * 3)  # More hotspots for higher risk
    
    heatmap_data = []
    
    for _ in range(num_hotspots):
        # Random offset within ~50km radius
        lat_offset = np.random.uniform(-0.3, 0.3)
        lon_offset = np.random.uniform(-0.3, 0.3)
        
        # Intensity scales with risk score
        base_intensity = risk_score / 10.0
        intensity = np.random.uniform(base_intensity * 0.5, base_intensity * 1.2)
        intensity = min(intensity, 1.0)
        
        heatmap_data.append([
            base_lat + lat_offset,
            base_lon + lon_offset,
            intensity
        ])
    
    return heatmap_data

def create_folium_map(location, risk_score, temperature, humidity, wind_speed, dryness):
    """
    Create Folium map with heatmap visualization
    """
    coords = LOCATION_COORDS[location]
    
    # Create base map
    m = folium.Map(
        location=[coords["lat"], coords["lon"]],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Get heatmap data
    heatmap_data = get_heatmap_data(location, risk_score)
    
    # Add heatmap layer
    HeatMap(
        heatmap_data,
        min_opacity=0.3,
        max_opacity=0.8,
        radius=25,
        blur=20,
        gradient={
            0.0: 'green',
            0.3: 'yellow',
            0.5: 'orange',
            0.7: 'red',
            1.0: 'darkred'
        }
    ).add_to(m)
    
    # Add main location marker with popup
    popup_html = f"""
    <div style="font-family: Arial; font-size: 14px;">
        <b>{location}</b><br>
        <hr style="margin: 5px 0;">
        <b>Risk Score:</b> {risk_score:.1f}/10<br>
        <b>Temperature:</b> {temperature}°C<br>
        <b>Humidity:</b> {humidity}%<br>
        <b>Wind Speed:</b> {wind_speed} km/h<br>
        <b>Dryness Index:</b> {dryness:.2f}
    </div>
    """
    
    # Determine marker color based on risk
    if risk_score <= 3:
        marker_color = 'green'
    elif risk_score <= 6:
        marker_color = 'orange'
    else:
        marker_color = 'red'
    
    folium.Marker(
        location=[coords["lat"], coords["lon"]],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=location,
        icon=folium.Icon(color=marker_color, icon='info-sign')
    ).add_to(m)
    
    return m

# ========== SIDEBAR CONTROLS ==========
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

# Location selector
location = st.sidebar.selectbox(
    "📍 Select Location",
    options=list(LOCATION_COORDS.keys()),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Environmental Parameters")

# Temperature slider
temperature = st.sidebar.slider(
    "🌡️ Temperature (°C)",
    min_value=10,
    max_value=50,
    value=30,
    step=1
)

# Humidity slider
humidity = st.sidebar.slider(
    "💧 Humidity (%)",
    min_value=0,
    max_value=100,
    value=40,
    step=1
)

# Wind speed slider
wind_speed = st.sidebar.slider(
    "💨 Wind Speed (km/h)",
    min_value=0,
    max_value=50,
    value=15,
    step=1
)

# Vegetation dryness slider
dryness = st.sidebar.slider(
    "🌾 Vegetation Dryness Index",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.01,
    format="%.2f"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Adjust parameters to see real-time risk assessment")

# ========== RISK SCORE CALCULATION ==========
# Normalize inputs to 0-1 range
norm_temp = (temperature - 10) / (50 - 10)
norm_humidity = humidity / 100
norm_wind = wind_speed / 50
norm_dryness = dryness

# Get historical fire probability
historical_fire_prob = LOCATION_COORDS[location]["fire_prob"]

# Calculate risk score using weighted formula
risk_score = (
    0.30 * norm_temp +
    0.25 * (1 - norm_humidity) +
    0.20 * norm_wind +
    0.15 * norm_dryness +
    0.10 * historical_fire_prob
)

# Scale to 0-10
risk_score = risk_score * 10
risk_score_rounded = round(risk_score)

# ========== ZONE CLASSIFICATION ==========
if risk_score <= 3:
    zone_name = "SAFE ZONE"
    zone_color = "#28a745"  # Green
    alert_class = "alert-safe"
    alert_icon = "✅"
    alert_message = "LOW RISK – Conditions stable."
elif risk_score <= 6:
    zone_name = "MODERATE RISK"
    zone_color = "#fd7e14"  # Orange
    alert_class = "alert-moderate"
    alert_icon = "⚠️"
    alert_message = "MODERATE RISK – Increase monitoring frequency."
else:
    zone_name = "DANGER ZONE"
    zone_color = "#dc3545"  # Red
    alert_class = "alert-danger"
    alert_icon = "🚨"
    alert_message = "HIGH FIRE RISK ALERT – Immediate surveillance recommended. Deploy patrol units immediately."

# ========== MAIN DASHBOARD UI ==========
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Blue header strip
st.markdown('<div class="header-strip">🔥 RiskRadar – Forest Fire Risk Monitoring</div>', unsafe_allow_html=True)

# Location text
st.markdown(f'<div class="location-text">📍 Location: <b>{location}</b></div>', unsafe_allow_html=True)

# Zone title with dynamic color
st.markdown(f'<div class="zone-title" style="color: {zone_color};">{zone_name}</div>', unsafe_allow_html=True)

# Risk score text
st.markdown(f'<div class="risk-score-text">Risk Score: <b>{risk_score:.1f}/10</b></div>', unsafe_allow_html=True)

# Star rating container
star_display = "⭐" * risk_score_rounded + "☆" * (10 - risk_score_rounded)
st.markdown(f'''
    <div class="star-container">
        <div class="star-rating" style="color: {zone_color};">
            {star_display}
        </div>
    </div>
''', unsafe_allow_html=True)

# ========== HEATMAP VISUALIZATION ==========
st.markdown("### 🗺️ Fire Risk Heatmap")
st.markdown("---")

# Create and render Folium map
folium_map = create_folium_map(location, risk_score, temperature, humidity, wind_speed, dryness)
st_folium(folium_map, width=800, height=500)

# ========== ALERT SECTION ==========
st.markdown(f'''
    <div class="alert-box {alert_class}">
        {alert_icon} {alert_message}
    </div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <small>RiskRadar v1.0 | Real-time Forest Fire Risk Assessment System | © 2026</small>
    </div>
""", unsafe_allow_html=True)
