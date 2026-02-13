# 🔥 RiskRadar - Forest Fire Risk Monitoring & Early Warning System

A complete Streamlit application for real-time forest fire risk assessment with interactive heatmap visualization.

## 🌟 Features

- **Single Unified Dashboard** - Clean, centered card layout with all key metrics
- **Dynamic Risk Assessment** - Real-time calculation based on environmental parameters
- **Interactive Heatmap** - Folium-powered visualization showing fire risk intensity
- **10-Star Rating System** - Visual risk indicator with color coding
- **Three Risk Zones** - Safe (Green), Moderate (Orange), Danger (Red)
- **Smart Alerts** - Context-aware warnings based on risk levels
- **4 Pre-configured Locations** - Patiala, Dehradun, Nagpur, Shimla
- **Database-Ready Architecture** - Easy to integrate with real data sources

## 📋 Requirements

- Python 3.8 or higher
- pip package manager

## 🚀 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit folium streamlit-folium numpy pandas
```

### Step 2: Run the Application

```bash
streamlit run riskradar_app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

## 🎮 How to Use

### Sidebar Controls

1. **📍 Select Location** - Choose from 4 cities:
   - Patiala, Punjab
   - Dehradun, Uttarakhand
   - Nagpur, Maharashtra
   - Shimla, Himachal Pradesh

2. **Environmental Parameters**:
   - 🌡️ **Temperature** (10-50°C) - Higher temps increase fire risk
   - 💧 **Humidity** (0-100%) - Lower humidity increases risk
   - 💨 **Wind Speed** (0-50 km/h) - Higher winds spread fires faster
   - 🌾 **Vegetation Dryness** (0.0-1.0) - Drier vegetation ignites easier

### Dashboard Elements

- **Blue Header Strip** - Application title
- **Location Display** - Shows currently selected location
- **Zone Title** - Dynamic risk zone (SAFE/MODERATE/DANGER)
- **Risk Score** - Calculated score from 0-10
- **Star Rating** - Visual representation (10 stars max)
- **Heatmap** - Interactive fire risk visualization
- **Alert Section** - Actionable warnings based on risk level

## 🧮 Risk Calculation Formula

```
risk_score = (
    0.30 × normalized_temperature +
    0.25 × (1 - normalized_humidity) +
    0.20 × normalized_wind_speed +
    0.15 × normalized_dryness +
    0.10 × historical_fire_probability
) × 10
```

### Risk Zones

| Risk Score | Zone | Color | Action |
|------------|------|-------|--------|
| 0-3 | SAFE ZONE | 🟢 Green | Conditions stable |
| 4-6 | MODERATE RISK | 🟠 Orange | Increase monitoring |
| 7-10 | DANGER ZONE | 🔴 Red | Deploy patrol units |

## 🗺️ Heatmap Features

- **Dynamic Intensity** - Scales with risk score
- **Color Gradient** - Green → Yellow → Orange → Red → Dark Red
- **Interactive Markers** - Click location pin for detailed info popup
- **Simulated Hotspots** - Shows potential fire danger areas
- **Database-Ready** - `get_heatmap_data()` function ready for real data integration

## 🔧 Customization

### Adding New Locations

Edit the `LOCATION_COORDS` dictionary in `riskradar_app.py`:

```python
LOCATION_COORDS = {
    "Your City, State": {
        "lat": 12.3456,  # Latitude
        "lon": 78.9012,  # Longitude
        "fire_prob": 0.35  # Historical fire probability (0-1)
    }
}
```

### Connecting to Database

Replace the `get_heatmap_data()` function to fetch real hotspot data:

```python
def get_heatmap_data(location, risk_score):
    # Your database query here
    # Return format: [[lat, lon, intensity], ...]
    query = f"SELECT lat, lon, intensity FROM hotspots WHERE location='{location}'"
    results = database.execute(query)
    return [[row.lat, row.lon, row.intensity] for row in results]
```

## 📊 Technical Architecture

```
├── riskradar_app.py         # Main application
├── requirements.txt          # Python dependencies
└── README.md                # This file

Components:
├── Sidebar Controls         # User inputs
├── Risk Calculator          # Weighted formula
├── Zone Classifier          # Risk categorization
├── Main Dashboard UI        # Centered card layout
├── Heatmap Generator        # Folium visualization
└── Alert System             # Dynamic warnings
```

## 🎨 UI Components

- **Custom CSS Styling** - Professional gradient headers, rounded cards
- **Responsive Layout** - Wide layout with centered content
- **Color-Coded Zones** - Visual risk indication
- **Unicode Star Ratings** - ⭐ for filled, ☆ for empty
- **Folium Integration** - Interactive maps with HeatMap plugin

## 🔐 Security Notes

- No sensitive data stored in application
- All calculations performed client-side
- Database connection code commented for security
- Ready for authentication layer integration

## 📱 Browser Compatibility

Tested and working on:
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

### Port already in use
```bash
streamlit run riskradar_app.py --server.port 8502
```

### Map not loading
- Check internet connection (Folium uses OpenStreetMap tiles)
- Try different map tiles in `create_folium_map()` function

## 🚀 Future Enhancements

- [ ] Real-time satellite data integration
- [ ] Historical fire incident database
- [ ] Multi-day forecast predictions
- [ ] SMS/Email alert system
- [ ] User authentication & role management
- [ ] Export reports as PDF
- [ ] Mobile app version
- [ ] API endpoint for third-party integration

## 📄 License

This project is provided as-is for educational and monitoring purposes.

## 🤝 Support

For issues or questions, please refer to:
- Streamlit Docs: https://docs.streamlit.io
- Folium Docs: https://python-visualization.github.io/folium/

## 📊 Version

**RiskRadar v1.0** - February 2026

---

**Built with ❤️ for Forest Fire Safety**
