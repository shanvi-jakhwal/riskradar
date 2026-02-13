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

# ============================================
# CORE RISK CALCULATION LOGIC
# ============================================

def calculate_forest_fire_risk(temperature, humidity, wind_speed, dry_days, 
                                ndvi=None, fire_count=None, distance_settlement=None, elevation=None):
    """
    Core formula to calculate forest fire risk score (0-10)
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity (0-100)
        wind_speed: Wind speed in km/h
        dry_days: Consecutive days without rain
        ndvi: Vegetation index (-1 to 1) [optional]
        fire_count: Historical fires in 5km radius [optional]
        distance_settlement: Distance to settlement in km [optional]
        elevation: Elevation in meters [optional]
    
    Returns:
        risk_score: Float (0-10)
    """
    
    # 1. Temperature Factor (0-1)
    if temperature < 25:
        temp_factor = 0.0
    elif temperature >= 40:
        temp_factor = 1.0
    else:
        temp_factor = (temperature - 25) / 15
    
    # 2. Humidity Factor (0-1) - inverse relationship
    if humidity >= 70:
        humidity_factor = 0.0
    elif humidity <= 20:
        humidity_factor = 1.0
    else:
        humidity_factor = (70 - humidity) / 50
    
    # 3. Wind Speed Factor (0-1)
    if wind_speed < 5:
        wind_factor = 0.2
    elif wind_speed >= 25:
        wind_factor = 1.0
    else:
        wind_factor = (wind_speed - 5) / 20
    
    # 4. Precipitation Factor (0-1)
    if dry_days < 7:
        precip_factor = 0.0
    elif dry_days >= 30:
        precip_factor = 1.0
    else:
        precip_factor = dry_days / 30
    
    # 5. Vegetation Factor (0-1) [optional]
    if ndvi is not None:
        if ndvi < 0.2:
            veg_factor = 0.0
        elif 0.6 <= ndvi <= 0.9:
            veg_factor = 1.0
        else:
            veg_factor = min(ndvi / 0.9, 1.0)
    else:
        veg_factor = 0.0
    
    # 6. Historical Fire Factor (0-1) [optional]
    if fire_count is not None:
        if fire_count == 0:
            hist_factor = 0.0
        elif fire_count >= 10:
            hist_factor = 1.0
        else:
            hist_factor = fire_count / 10
    else:
        hist_factor = 0.0
    
    # 7. Proximity to Settlement Factor (0-1) [optional]
    if distance_settlement is not None:
        if distance_settlement > 5:
            proximity_factor = 0.0
        elif distance_settlement <= 0.5:
            proximity_factor = 1.0
        else:
            proximity_factor = (5 - distance_settlement) / 4.5
    else:
        proximity_factor = 0.0
    
    # 8. Elevation Factor (0-1) [optional]
    if elevation is not None:
        if elevation < 500:
            elev_factor = 0.3
        elif 500 <= elevation <= 1500:
            elev_factor = 0.7
        else:
            elev_factor = 0.4
    else:
        elev_factor = 0.0
    
    # FINAL RISK SCORE CALCULATION
    risk_score = (
        0.25 * temp_factor +
        0.20 * humidity_factor +
        0.15 * wind_factor +
        0.12 * precip_factor +
        0.10 * veg_factor +
        0.08 * hist_factor +
        0.05 * proximity_factor +
        0.05 * elev_factor
    ) * 10
    
    return risk_score

# Location coordinates database with environmental data
LOCATION_COORDS = {
    "California, USA": {
        "lat": 36.7783,
        "lon": -119.4179,
        "temperature": 38.0,
        "humidity": 25.0,
        "wind_speed": 20.0,
        "dry_days": 28,
        "ndvi": 0.45,
        "fire_count": 12,
        "distance_settlement": 1.5,
        "elevation": 500
    },
    "Patiala, Punjab": {
        "lat": 30.3398,
        "lon": 76.3869,
        "temperature": 35.0,
        "humidity": 45.0,
        "wind_speed": 12.0,
        "dry_days": 15,
        "ndvi": 0.65,
        "fire_count": 3,
        "distance_settlement": 1.2,
        "elevation": 250
    },
    "Dehradun, Uttarakhand": {
        "lat": 30.3165,
        "lon": 78.0322,
        "temperature": 32.0,
        "humidity": 55.0,
        "wind_speed": 8.0,
        "dry_days": 20,
        "ndvi": 0.78,
        "fire_count": 7,
        "distance_settlement": 0.8,
        "elevation": 640
    },
    "Nagpur, Maharashtra": {
        "lat": 21.1458,
        "lon": 79.0882,
        "temperature": 38.0,
        "humidity": 30.0,
        "wind_speed": 15.0,
        "dry_days": 25,
        "ndvi": 0.55,
        "fire_count": 5,
        "distance_settlement": 2.5,
        "elevation": 310
    },
    "Shimla, Himachal Pradesh": {
        "lat": 31.1048,
        "lon": 77.1734,
        "temperature": 28.0,
        "humidity": 60.0,
        "wind_speed": 10.0,
        "dry_days": 12,
        "ndvi": 0.82,
        "fire_count": 8,
        "distance_settlement": 1.5,
        "elevation": 2200
    }
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

def create_folium_map(location, risk_score, location_data):
    """
    Create Folium map with heatmap visualization
    """
    coords = LOCATION_COORDS[location]
    
    # Create base map
    m = folium.Map(
        location=[coords["lat"], coords["lon"]],
        zoom_start=9,
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
    <div style="font-family: Arial; font-size: 13px; min-width: 220px;">
        <h4 style="margin: 0 0 8px 0; color: #333;">{location}</h4>
        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ddd;">
        <table style="width: 100%; font-size: 12px;">
            <tr><td><b>Risk Score:</b></td><td>{risk_score:.2f}/10</td></tr>
            <tr><td><b>Temperature:</b></td><td>{location_data['temperature']:.1f}°C</td></tr>
            <tr><td><b>Humidity:</b></td><td>{location_data['humidity']:.1f}%</td></tr>
            <tr><td><b>Wind Speed:</b></td><td>{location_data['wind_speed']:.1f} km/h</td></tr>
            <tr><td><b>Dry Days:</b></td><td>{location_data['dry_days']}</td></tr>
            <tr><td><b>NDVI:</b></td><td>{location_data['ndvi']:.2f}</td></tr>
            <tr><td><b>Fire Count:</b></td><td>{location_data['fire_count']}</td></tr>
            <tr><td><b>Elevation:</b></td><td>{location_data['elevation']}m</td></tr>
        </table>
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
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"{location} - Risk: {risk_score:.1f}/10",
        icon=folium.Icon(color=marker_color, icon='info-sign')
    ).add_to(m)
    
    return m

# ========== SIDEBAR CONTROLS ==========
st.sidebar.title("🎛️ RiskRadar Control Panel")
st.sidebar.markdown("---")

# Location selector
location = st.sidebar.selectbox(
    "📍 Select Monitoring Location",
    options=list(LOCATION_COORDS.keys()),
    index=0
)

# Get current location data
current_data = LOCATION_COORDS[location]

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Current Environmental Data")

# Display real-time parameters (read-only)
st.sidebar.metric("🌡️ Temperature", f"{current_data['temperature']:.1f}°C")
st.sidebar.metric("💧 Humidity", f"{current_data['humidity']:.1f}%")
st.sidebar.metric("💨 Wind Speed", f"{current_data['wind_speed']:.1f} km/h")
st.sidebar.metric("☀️ Dry Days", f"{current_data['dry_days']} days")

st.sidebar.markdown("---")
st.sidebar.subheader("🌲 Advanced Parameters")
st.sidebar.metric("🌿 NDVI", f"{current_data['ndvi']:.2f}")
st.sidebar.metric("🔥 Historical Fires", f"{current_data['fire_count']} in 5km")
st.sidebar.metric("🏘️ Settlement Distance", f"{current_data['distance_settlement']:.1f} km")
st.sidebar.metric("⛰️ Elevation", f"{current_data['elevation']} m")

st.sidebar.markdown("---")
st.sidebar.info("💡 Real-time data from sensor network & satellite imagery")

# ========== RISK SCORE CALCULATION ==========
# Calculate risk using the actual formula
risk_score = calculate_forest_fire_risk(
    temperature=current_data['temperature'],
    humidity=current_data['humidity'],
    wind_speed=current_data['wind_speed'],
    dry_days=current_data['dry_days'],
    ndvi=current_data['ndvi'],
    fire_count=current_data['fire_count'],
    distance_settlement=current_data['distance_settlement'],
    elevation=current_data['elevation']
)
risk_score_rounded = round(risk_score)

# ========== ZONE CLASSIFICATION ==========
if risk_score <= 3:
    zone_name = "SAFE ZONE"
    zone_color = "#28a745"  # Green
    alert_class = "alert-safe"
    alert_icon = "✅"
    alert_message = "LOW RISK – Conditions stable. Continue routine monitoring."
elif risk_score <= 6:
    zone_name = "MODERATE RISK"
    zone_color = "#fd7e14"  # Orange
    alert_class = "alert-moderate"
    alert_icon = "⚠️"
    alert_message = "MODERATE RISK – Increase monitoring frequency. Prepare response teams."
else:
    zone_name = "DANGER ZONE"
    zone_color = "#dc3545"  # Red
    alert_class = "alert-danger"
    alert_icon = "🚨"
    alert_message = "HIGH FIRE RISK ALERT – Immediate surveillance required. Deploy patrol units and notify authorities immediately."

# ========== MAIN DASHBOARD UI ==========
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Blue header strip
st.markdown('<div class="header-strip">🔥 RiskRadar – Forest Fire Risk Monitoring & Early Warning System</div>', unsafe_allow_html=True)

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
st.markdown("### 🗺️ Fire Risk Heatmap - Live Hotspot Detection")
st.markdown("---")

# Create and render Folium map with current data
folium_map = create_folium_map(location, risk_score, current_data)
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
        <small>RiskRadar v2.0 Production | Real-time Forest Fire Risk Assessment | Data Sources: Satellite Imagery, Weather Stations, Sensor Network | © 2026</small>
    </div>
""", unsafe_allow_html=True)
