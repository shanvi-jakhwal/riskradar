import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="RiskRadar - Forest Fire Risk Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSV FILE PATHS - CHANGE THESE IF NEEDED
# ============================================

NASA_FIRMS_CSV = "nasa_firms_data.csv"
WEATHER_DATA_CSV = "weather_data.csv"

# ============================================
# CUSTOM CSS STYLING
# ============================================

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
    .csv-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING FUNCTIONS
# ============================================

@st.cache_data
def load_nasa_firms_data():
    """Load NASA FIRMS CSV data"""
    try:
        df = pd.read_csv(NASA_FIRMS_CSV)
        
        required_columns = ['latitude', 'longitude', 'bright_t31', 'frp', 'daynight']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing columns in NASA FIRMS CSV: {missing_columns}")
            return pd.DataFrame()
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ NASA FIRMS CSV file not found: {NASA_FIRMS_CSV}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading NASA FIRMS data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_weather_data():
    """Load Weather CSV data"""
    try:
        df = pd.read_csv(WEATHER_DATA_CSV)
        
        required_columns = ['weather_type', 'wind_speed', 'precipitation', 'temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing columns in Weather CSV: {missing_columns}")
            return pd.Series()
        
        # Get most recent weather data (last row)
        current_weather = df.iloc[-1]
        return current_weather
        
    except FileNotFoundError:
        st.error(f"❌ Weather CSV file not found: {WEATHER_DATA_CSV}")
        return pd.Series()
    except Exception as e:
        st.error(f"❌ Error loading weather data: {str(e)}")
        return pd.Series()

# ============================================
# RISK CALCULATION FROM WEATHER DATA
# ============================================

def calculate_risk_from_weather(weather_data):
    """
    Calculate risk score based on weather CSV data
    Uses: weather_type, wind_speed, precipitation, temperature
    """
    
    if weather_data.empty:
        return 5.0  # Default moderate risk if no data
    
    # Extract weather parameters from CSV
    temperature = float(weather_data['temperature'])
    wind_speed = float(weather_data['wind_speed'])
    precipitation = float(weather_data['precipitation'])
    weather_type = str(weather_data['weather_type']).lower()
    
    # 1. Temperature Factor (0-1)
    if temperature < 25:
        temp_factor = 0.0
    elif temperature >= 40:
        temp_factor = 1.0
    else:
        temp_factor = (temperature - 25) / 15
    
    # 2. Wind Speed Factor (0-1)
    if wind_speed < 5:
        wind_factor = 0.2
    elif wind_speed >= 25:
        wind_factor = 1.0
    else:
        wind_factor = (wind_speed - 5) / 20
    
    # 3. Precipitation Factor (0-1) - inverse relationship
    if precipitation > 10:
        precip_factor = 0.0
    elif precipitation <= 0:
        precip_factor = 1.0
    else:
        precip_factor = (10 - precipitation) / 10
    
    # 4. Weather Type Factor (0-1)
    weather_risk = {
        'clear': 0.8,
        'sunny': 0.8,
        'cloudy': 0.4,
        'partly cloudy': 0.5,
        'overcast': 0.3,
        'rain': 0.0,
        'drizzle': 0.2,
        'thunderstorm': 0.1,
        'fog': 0.3,
        'mist': 0.3
    }
    weather_factor = weather_risk.get(weather_type, 0.5)
    
    # FINAL RISK CALCULATION
    # Weighted formula based on 4 weather parameters
    risk_score = (
        0.35 * temp_factor +
        0.30 * wind_factor +
        0.20 * precip_factor +
        0.15 * weather_factor
    ) * 10
    
    return risk_score

# ============================================
# HEATMAP FROM NASA FIRMS DATA
# ============================================

def create_heatmap_from_firms(firms_data):
    """
    Create heatmap data from NASA FIRMS CSV
    Uses: latitude, longitude, bright_t31, frp
    """
    
    if firms_data.empty:
        # Return dummy data if CSV not loaded
        return [[36.7783, -119.4179, 0.5]]
    
    heatmap_data = []
    
    # Process each hotspot from NASA FIRMS
    for idx, row in firms_data.iterrows():
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        
        # Calculate intensity from brightness and FRP
        brightness = float(row['bright_t31'])
        frp = float(row['frp'])
        
        # Normalize brightness (typically 300-400K range)
        brightness_norm = (brightness - 300) / 100
        brightness_norm = max(0, min(brightness_norm, 1))
        
        # Normalize FRP (typically 0-100 MW range)
        frp_norm = frp / 100
        frp_norm = max(0, min(frp_norm, 1))
        
        # Combined intensity (weighted average)
        intensity = (0.6 * frp_norm + 0.4 * brightness_norm)
        intensity = max(0.1, min(intensity, 1.0))
        
        heatmap_data.append([lat, lon, intensity])
    
    return heatmap_data

# ============================================
# MAP CREATION
# ============================================

def create_california_map(firms_data, risk_score, weather_data):
    """Create Folium map with NASA FIRMS heatmap overlay"""
    
    # California center coordinates
    california_center = [36.7783, -119.4179]
    
    # Create base map
    m = folium.Map(
        location=california_center,
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Add heatmap from NASA FIRMS data
    heatmap_data = create_heatmap_from_firms(firms_data)
    
    HeatMap(
        heatmap_data,
        min_opacity=0.3,
        max_opacity=0.85,
        radius=20,
        blur=18,
        gradient={
            0.0: '#00ff00',
            0.3: '#ffff00',
            0.5: '#ff9900',
            0.7: '#ff0000',
            1.0: '#8B0000'
        }
    ).add_to(m)
    
    # Determine marker color based on risk
    if risk_score <= 3:
        marker_color = 'green'
    elif risk_score <= 6:
        marker_color = 'orange'
    else:
        marker_color = 'red'
    
    # Create popup with weather data
    if not weather_data.empty:
        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; min-width: 220px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">California Fire Risk</h4>
            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ddd;">
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>Risk Score:</b></td><td>{risk_score:.2f}/10</td></tr>
                <tr><td><b>Temperature:</b></td><td>{weather_data['temperature']:.1f}°C</td></tr>
                <tr><td><b>Wind Speed:</b></td><td>{weather_data['wind_speed']:.1f} km/h</td></tr>
                <tr><td><b>Precipitation:</b></td><td>{weather_data['precipitation']:.1f} mm</td></tr>
                <tr><td><b>Weather:</b></td><td>{weather_data['weather_type']}</td></tr>
                <tr><td><b>Hotspots:</b></td><td>{len(firms_data)} detected</td></tr>
            </table>
        </div>
        """
    else:
        popup_html = "<b>California</b><br>Weather data not available"
    
    # Add main marker
    folium.Marker(
        location=california_center,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"California - Risk: {risk_score:.1f}/10",
        icon=folium.Icon(color=marker_color, icon='fire', prefix='fa')
    ).add_to(m)
    
    return m

# ============================================
# MAIN APPLICATION
# ============================================

# Sidebar
st.sidebar.title("🎛️ RiskRadar Control Panel")
st.sidebar.markdown("---")

st.sidebar.subheader("📍 Monitoring Location")
st.sidebar.info("**California, USA**")

st.sidebar.markdown("---")

# Load CSV data
st.sidebar.subheader("📊 Data Sources")

firms_data = load_nasa_firms_data()
weather_data = load_weather_data()

# Display data status
if not firms_data.empty:
    st.sidebar.success(f"🛰️ NASA FIRMS: {len(firms_data)} hotspots")
else:
    st.sidebar.error("❌ NASA FIRMS data not loaded")

if not weather_data.empty:
    st.sidebar.success(f"🌤️ Weather data loaded")
else:
    st.sidebar.error("❌ Weather data not loaded")

st.sidebar.markdown("---")

# Display current weather parameters
if not weather_data.empty:
    st.sidebar.subheader("📊 Current Weather Data")
    st.sidebar.metric("🌡️ Temperature", f"{weather_data['temperature']:.1f}°C")
    st.sidebar.metric("💨 Wind Speed", f"{weather_data['wind_speed']:.1f} km/h")
    st.sidebar.metric("💧 Precipitation", f"{weather_data['precipitation']:.1f} mm")
    st.sidebar.metric("☁️ Weather Type", weather_data['weather_type'])
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Real-time data from CSV files")

# Calculate risk score
risk_score = calculate_risk_from_weather(weather_data)
risk_score_rounded = round(risk_score)

# Zone classification
if risk_score <= 3:
    zone_name = "SAFE ZONE"
    zone_color = "#28a745"
    alert_class = "alert-safe"
    alert_icon = "✅"
    alert_message = "LOW RISK – Conditions stable. Continue routine monitoring."
elif risk_score <= 6:
    zone_name = "MODERATE RISK"
    zone_color = "#fd7e14"
    alert_class = "alert-moderate"
    alert_icon = "⚠️"
    alert_message = "MODERATE RISK – Increase monitoring frequency. Prepare response teams."
else:
    zone_name = "DANGER ZONE"
    zone_color = "#dc3545"
    alert_class = "alert-danger"
    alert_icon = "🚨"
    alert_message = "HIGH FIRE RISK ALERT – Immediate surveillance required. Deploy patrol units and notify authorities immediately."

# ========== MAIN DASHBOARD UI ==========
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Header
st.markdown('<div class="header-strip">🔥 RiskRadar – Forest Fire Risk Monitoring & Early Warning System</div>', unsafe_allow_html=True)

# Location
st.markdown('<div class="location-text">📍 Location: <b>California, USA</b></div>', unsafe_allow_html=True)

# CSV File Status Warning
if firms_data.empty or weather_data.empty:
    st.markdown("""
        <div class="csv-warning">
            <h4>⚠️ CSV Files Required</h4>
            <p><b>Please ensure these CSV files are in the same directory:</b></p>
            <ul>
                <li>📁 <code>nasa_firms_data.csv</code> - NASA FIRMS hotspot data</li>
                <li>📁 <code>weather_data.csv</code> - California weather data</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Zone title
st.markdown(f'<div class="zone-title" style="color: {zone_color};">{zone_name}</div>', unsafe_allow_html=True)

# Risk score
st.markdown(f'<div class="risk-score-text">Risk Score: <b>{risk_score:.2f}/10</b></div>', unsafe_allow_html=True)

# Star rating
star_display = "⭐" * risk_score_rounded + "☆" * (10 - risk_score_rounded)
st.markdown(f'''
    <div class="star-container">
        <div class="star-rating" style="color: {zone_color};">
            {star_display}
        </div>
    </div>
''', unsafe_allow_html=True)

# Heatmap visualization
st.markdown("### 🗺️ NASA FIRMS Fire Risk Heatmap - Live Hotspot Detection")
st.markdown("---")

# Create and render map
california_map = create_california_map(firms_data, risk_score, weather_data)
st_folium(california_map, width=800, height=500)

# Alert section
st.markdown(f'''
    <div class="alert-box {alert_class}">
        {alert_icon} {alert_message}
    </div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <small>RiskRadar v2.0 Production | Real-time Forest Fire Risk Assessment | Data Sources: NASA FIRMS, Weather Stations | © 2026</small>
    </div>
""", unsafe_allow_html=True)

# Debug Information
with st.expander("🔧 Debug Information - CSV Data Preview"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("NASA FIRMS Data Sample")
        if not firms_data.empty:
            st.dataframe(firms_data.head(10))
            st.info(f"Total hotspots: {len(firms_data)}")
        else:
            st.warning("No NASA FIRMS data loaded")
    
    with col2:
        st.subheader("Weather Data")
        if not weather_data.empty:
            st.json(weather_data.to_dict())
        else:
            st.warning("No weather data loaded")
