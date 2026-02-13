import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="RiskRadar - Forest Fire Risk Monitoring",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 🔴 CSV FILE PATHS - UPDATE THESE!
# ============================================

# NASA FIRMS DATA - Must have columns: latitude, longitude, bright_t31, frp, daynight, acq_date
# acq_date format should be: YYYY-MM-DD (e.g., 2026-01-15)
NASA_FIRMS_CSV = "nasa_firms_data.csv"

# WEATHER DATA - Must have columns: date, location, temperature, humidity, wind_speed, precipitation
# date format should be: YYYY-MM-DD (e.g., 2026-01-15)
WEATHER_DATA_CSV = "weather_data.csv"

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
    <style>
    
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
    
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# 🔴 DATA LOADING FUNCTIONS
# ============================================

@st.cache_data
def load_nasa_firms_data():
    """
    🔴 Load NASA FIRMS CSV data (Jan 1 - Feb 12, 2026)
    Required columns: latitude, longitude, bright_t31, frp, daynight, acq_date
    """
    try:
        df = pd.read_csv(NASA_FIRMS_CSV)
        
        required_columns = ['latitude', 'longitude', 'bright_t31', 'frp', 'daynight', 'acq_date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing columns in NASA FIRMS CSV: {missing_columns}")
            st.info(f"📋 Available columns: {list(df.columns)}")
            return pd.DataFrame()
        
        # Convert date column to datetime
        df['acq_date'] = pd.to_datetime(df['acq_date'], format="%d-%m-%Y", errors="coerce")
        
        st.success(f"✅ NASA FIRMS data loaded: {len(df)} total hotspots")
        return df
        
    except FileNotFoundError:
        st.error(f"❌ NASA FIRMS CSV file not found: {NASA_FIRMS_CSV}")
        st.warning("📁 Please upload your NASA FIRMS CSV file")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading NASA FIRMS data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_weather_data():
    """
    🔴 Load Weather CSV data (Jan 1 - Feb 12, 2026)
    Required columns: date, location, temperature, humidity, wind_speed, precipitation
    """
    try:
        df = pd.read_csv(WEATHER_DATA_CSV)
        
        required_columns = ['date', 'location', 'temperature', 'humidity', 'wind_speed', 'precipitation']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Missing columns in Weather CSV: {missing_columns}")
            st.info(f"📋 Available columns: {list(df.columns)}")
            return pd.DataFrame()
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y", errors="coerce")
        
        st.success(f"✅ Weather data loaded: {len(df)} records")
        return df
        
    except FileNotFoundError:
        st.error(f"❌ Weather CSV file not found: {WEATHER_DATA_CSV}")
        st.warning("📁 Please upload your Weather CSV file")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading weather data: {str(e)}")
        return pd.DataFrame()

# ============================================
# 🔴 DATA FILTERING FUNCTIONS
# ============================================

def filter_firms_by_date(firms_data, selected_date):
    """Filter NASA FIRMS data by selected date"""
    if firms_data.empty:
        return pd.DataFrame()
    
    # Convert selected_date to datetime
    selected_datetime = pd.to_datetime(selected_date)
    
    # Filter data for selected date
    filtered = firms_data[firms_data['acq_date'].dt.date == selected_datetime.date()]
    
    return filtered

def get_weather_by_date_location(weather_data, selected_date, location):
    """Get weather data for specific date and location"""
    if weather_data.empty:
        return pd.Series()
    
    # Convert selected_date to datetime
    selected_datetime = pd.to_datetime(selected_date)
    
    # Filter by date and location
    filtered = weather_data[
        (weather_data['date'].dt.date == selected_datetime.date()) &
        (weather_data['location'].str.lower() == location.lower())
    ]
    
   
    if filtered.empty:
        st.warning(f"You have selected {location} on {selected_date}")
        return pd.Series()
    
    return filtered.iloc[0]

# ============================================
# 🔴 RISK CALCULATION FROM WEATHER DATA
# ============================================

def calculate_risk_from_weather(weather_data):
    """
    Calculate risk score based on weather CSV data
    Uses: temperature, humidity, wind_speed, precipitation
    """
    
    if weather_data.empty:
        return 5.0
    
    # Extract weather parameters
    temperature = float(weather_data['temperature'])
    humidity = float(weather_data['humidity'])
    wind_speed = float(weather_data['wind_speed'])
    precipitation = float(weather_data['precipitation'])
    
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
    
    # 4. Precipitation Factor (0-1) - inverse relationship
    if precipitation > 10:
        precip_factor = 0.0
    elif precipitation <= 0:
        precip_factor = 1.0
    else:
        precip_factor = (10 - precipitation) / 10
    
    # FINAL RISK CALCULATION
    risk_score = (
        0.35 * temp_factor +
        0.25 * humidity_factor +
        0.25 * wind_factor +
        0.15 * precip_factor
    ) * 10
    
    return risk_score

# ============================================
# 🔴 HEATMAP FROM NASA FIRMS DATA
# ============================================

def create_heatmap_from_firms(firms_data):
    """
    Create heatmap data from NASA FIRMS CSV (filtered by date)
    Uses: latitude, longitude, bright_t31, frp
    """
    
    if firms_data.empty:
        return [[36.7783, -119.4179, 0.1]]
    
    heatmap_data = []
    
    # Process each hotspot
    for idx, row in firms_data.iterrows():
        lat = float(row['latitude'])
        lon = float(row['longitude'])
        brightness = float(row['bright_t31'])
        frp = float(row['frp'])
        
        # Normalize brightness (300-400K range)
        brightness_norm = (brightness - 300) / 100
        brightness_norm = max(0, min(brightness_norm, 1))
        
        # Normalize FRP (0-100 MW range)
        frp_norm = frp / 100
        frp_norm = max(0, min(frp_norm, 1))
        
        # Combined intensity
        intensity = (0.6 * frp_norm + 0.4 * brightness_norm)
        intensity = max(0.1, min(intensity, 1.0))
        
        heatmap_data.append([lat, lon, intensity])
    
    return heatmap_data

# ============================================
# LOCATION COORDINATES
# ============================================

LOCATION_COORDS = {
    "California": {"lat": 36.7783, "lon": -119.4179, "zoom": 6},
    "Texas": {"lat": 31.9686, "lon": -99.9018, "zoom": 6},
    "Florida": {"lat": 27.6648, "lon": -81.5158, "zoom": 6},
    "Oregon": {"lat": 43.8041, "lon": -120.5542, "zoom": 6},
    "Washington": {"lat": 47.7511, "lon": -120.7401, "zoom": 6},
}

# ============================================
# MAP CREATION
# ============================================

def create_fire_map(firms_data, risk_score, weather_data, location, selected_date):
    """Create Folium map with NASA FIRMS heatmap overlay"""
    
    coords = LOCATION_COORDS.get(location, LOCATION_COORDS["California"])
    
    # Create base map
    m = folium.Map(
        location=[coords["lat"], coords["lon"]],
        zoom_start=coords["zoom"],
        tiles='OpenStreetMap'
    )
    
    # Add heatmap
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
    
    # Marker color
    if risk_score <= 3:
        marker_color = 'green'
    elif risk_score <= 6:
        marker_color = 'orange'
    else:
        marker_color = 'red'
    
    # Create popup
    if not weather_data.empty:
        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; min-width: 220px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">{location} Fire Risk</h4>
            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ddd;">
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>Date:</b></td><td>{selected_date}</td></tr>
                <tr><td><b>Risk Score:</b></td><td>{risk_score:.2f}/10</td></tr>
                <tr><td><b>Temperature:</b></td><td>{weather_data['temperature']:.1f}°C</td></tr>
                <tr><td><b>Humidity:</b></td><td>{weather_data['humidity']:.1f}%</td></tr>
                <tr><td><b>Wind Speed:</b></td><td>{weather_data['wind_speed']:.1f} km/h</td></tr>
                <tr><td><b>Precipitation:</b></td><td>{weather_data['precipitation']:.1f} mm</td></tr>
                <tr><td><b>Hotspots:</b></td><td>{len(firms_data)} detected</td></tr>
            </table>
        </div>
        """
    else:
        popup_html = f"<b>{location}</b><br>Date: {selected_date}<br>Weather data not available"
    
    folium.Marker(
        location=[coords["lat"], coords["lon"]],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"{location} - {selected_date}",
        icon=folium.Icon(color=marker_color, icon='fire', prefix='fa')
    ).add_to(m)
    
    return m

# ============================================
# MAIN APPLICATION
# ============================================

# Load all data
firms_data_full = load_nasa_firms_data()
weather_data_full = load_weather_data()

# ========== SIDEBAR ==========
st.sidebar.title(" RiskRadar Control Panel")
st.sidebar.markdown("---")

# 🔴 LOCATION DROPDOWN
st.sidebar.subheader("📍 Select Location")
location = st.sidebar.selectbox(
    "Choose State",
    options=list(LOCATION_COORDS.keys()),
    index=0  # California default
)

st.sidebar.markdown("---")

# 🔴 DATE DROPDOWN
st.sidebar.subheader("📅 Select Date")

# Get available dates from data
if not firms_data_full.empty:
    available_dates = sorted(firms_data_full['acq_date'].dt.date.unique())
    
    # Convert to date objects for selector
    selected_date = st.sidebar.selectbox(
        "Choose Date",
        options=available_dates,
        index=len(available_dates)-1 if available_dates else 0,  # Latest date default
        format_func=lambda x: x.strftime("%B %d, %Y")  # Format: January 15, 2026
    )
else:
    # Fallback if no data
    selected_date = st.sidebar.date_input(
        "Choose Date",
        value=date(2026, 2, 12),
        min_value=date(2026, 1, 1),
        max_value=date(2026, 2, 12)
    )

st.sidebar.markdown("---")

# Filter data by selected date and location
firms_filtered = filter_firms_by_date(firms_data_full, selected_date)
weather_filtered = get_weather_by_date_location(weather_data_full, selected_date, location)





# Display current weather parameters
if not weather_filtered.empty:
    st.sidebar.subheader("📊 Weather Data")
    st.sidebar.metric("🌡️ Temperature", f"{weather_filtered['temperature']:.1f}°C")
    st.sidebar.metric("💧 Humidity", f"{weather_filtered['humidity']:.1f}%")
    st.sidebar.metric("💨 Wind Speed", f"{weather_filtered['wind_speed']:.1f} km/h")
    st.sidebar.metric("🌧️ Precipitation", f"{weather_filtered['precipitation']:.1f} mm")

st.sidebar.markdown("---")
st.sidebar.info("💡 Data: Jan 1 - Feb 12, 2026")

# Calculate risk score
risk_score = calculate_risk_from_weather(weather_filtered)
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

# ========== MAIN DASHBOARD ==========
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# Header
st.markdown('<div class="header-strip">🔥 RiskRadar – Forest Fire Risk Monitoring & Early Warning System</div>', unsafe_allow_html=True)

# Location and Date
st.markdown(f'<div class="location-text">📍 Location: <b>{location}</b> | 📅 Date: <b>{selected_date.strftime("%B %d, %Y")}</b></div>', unsafe_allow_html=True)

# Warning if data missing
if firms_filtered.empty or weather_filtered.empty:
    st.markdown("""
        <div class="csv-warning">
            
            
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

# Heatmap
st.markdown("### 🗺️ NASA FIRMS Fire Risk Heatmap - Live Hotspot Detection")
st.markdown("---")

fire_map = create_fire_map(firms_filtered, risk_score, weather_filtered, location, selected_date)
st_folium(fire_map, width=800, height=500)

# Alert
st.markdown(f'''
    <div class="alert-box {alert_class}">
        {alert_icon} {alert_message}
    </div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 20px;">
        <small>RiskRadar v3.0 Production | Data Period: January 1 - February 12, 2026 | Sources: NASA FIRMS, Weather Stations | © 2026</small>
    </div>
""", unsafe_allow_html=True)

# Debug Information
with st.expander("🔧 Debug Information - Filtered Data Preview"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"NASA FIRMS - {selected_date}")
        if not firms_filtered.empty:
            st.dataframe(firms_filtered.head(10))
            st.info(f"Hotspots on this date: {len(firms_filtered)}")
        else:
            st.warning("No hotspots for selected date")
    
    with col2:
        st.subheader(f"Weather - {location}")
        if not weather_filtered.empty:
            st.json(weather_filtered.to_dict())
        else:
            st.warning("No weather data for selected location/date")
