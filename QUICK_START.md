# 🚀 RiskRadar - Quick Start Guide

## ✅ Complete Package - Ready to Run!

Tu bas 3 files upload kar aur run kar!

---

## 📦 Files Tumhe Mile:

1. ✅ **app.py** - Complete working app
2. ✅ **nasa_firms_data.csv** - 30 California hotspots (dummy data)
3. ✅ **weather_data.csv** - 8 weather records (dummy data)

---

## 🚀 GitHub Codespaces Mein Setup (Step-by-Step):

### **Step 1: Upload Files**

Codespaces mein left panel (Explorer) mein:
1. **app.py** upload karo
2. **nasa_firms_data.csv** upload karo  
3. **weather_data.csv** upload karo

Sab files **ek hi folder** mein honi chahiye!

```
your-repo/
├── app.py
├── nasa_firms_data.csv
├── weather_data.csv
└── requirements.txt
```

---

### **Step 2: Terminal Mein Install Karo**

```bash
pip install streamlit folium streamlit-folium numpy pandas
```

---

### **Step 3: Run Karo**

```bash
streamlit run app.py
```

---

### **Step 4: Open Karo**

- Popup aayega → **"Open in Browser"** click karo
- Ya PORTS tab mein port 8501 pe globe icon click karo

---

## ✅ **Kya Dikhega:**

✅ **30 California hotspots** on heatmap  
✅ **Temperature: 40.2°C** (from last row of weather CSV)  
✅ **Wind: 22.5 km/h**  
✅ **Precipitation: 0.0 mm**  
✅ **Weather: Clear**  
✅ **Risk Score: ~8.5/10** (DANGER ZONE - Red)  
✅ **8 stars filled** out of 10  
✅ **Alert: Deploy patrol units**  

---

## 🔄 Apni Real Data Kaise Daale:

### **NASA FIRMS Data:**

1. **Download** from: https://firms.modaps.eosdis.nasa.gov/
2. **Format** chahiye:
   ```csv
   latitude,longitude,bright_t31,frp,daynight
   36.7783,-119.4179,342.5,45.2,D
   ```
3. **Replace** `nasa_firms_data.csv` with your file

### **Weather Data:**

1. **Format** chahiye:
   ```csv
   weather_type,wind_speed,precipitation,temperature
   Clear,20.1,0.0,38.7
   Sunny,22.5,0.0,40.2
   ```
2. **Last row** use hogi as current weather
3. **Replace** `weather_data.csv` with your file

---

## 🎯 How It Works:

```
CSV Files
    ↓
nasa_firms_data.csv → Heatmap (30 points California pe)
    ↓
weather_data.csv → Risk Calculation (4 factors)
    ↓
Risk Score → SAFE/MODERATE/DANGER
    ↓
Map + Stars + Alert
```

---

## 🔧 Troubleshooting:

**"CSV file not found"**
- Check files same folder mein hain
- Filenames exactly match: `nasa_firms_data.csv` and `weather_data.csv`

**"Missing columns"**
- Open CSV aur check column names
- Must match exactly (case-sensitive!)

**"No data showing"**
- Click "Debug Information" expander at bottom
- Check CSV data preview

---

## 💡 Quick Test Commands:

```bash
# Check files exist
ls -la

# Should show:
# app.py
# nasa_firms_data.csv
# weather_data.csv

# Run app
streamlit run app.py
```

---

## 🎉 That's It!

Bas 3 files upload kar, install kar, aur run kar!

**Questions?** Check debug section in app (bottom mein expander hai) 🚀
