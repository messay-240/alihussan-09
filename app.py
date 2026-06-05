import streamlit as st
st.set_page_config(page_title="Solar Power Estimator Pro", layout="wide", page_icon="⚡")

# --- TERMS & AGREEMENT POPUP - SAB SE PEHLE ---
def show_terms():
    @st.dialog("📄 Terms & Privacy Agreement")
    def terms_dialog():
        st.markdown("""
        ### ⚠️ IMPORTANT DISCLAIMER
        By using this Solar Power Estimator Pro app, you agree that:
        1. **No Liability**: Calculations are for planning only. We are NOT responsible for any financial loss.
        2. **Data Privacy**: We do NOT store your personal data. Location only used for weather API.
        3. **Accuracy**: Solar generation varies ±20% due to weather, panel quality, installation.
        4. **Professional Advice**: Consult certified solar engineer before installation.
        By clicking "I Agree", you accept all terms.
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ I Disagree", use_container_width=True, type="secondary"):
                st.stop()
        with col2:
            if st.button("✅ I Agree", use_container_width=True, type="primary"):
                st.session_state['agreed'] = True
                st.rerun()
    if 'agreed' not in st.session_state:
        terms_dialog()
        st.stop()

show_terms()

# --- IMPORTS ---
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from datetime import datetime
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests
from io import BytesIO

# --- SAFE GEOCODER + WEATHER FUNCTIONS ---
GEO_ENABLED = False
try:
    from geopy.geocoders import Nominatim
    GEO_ENABLED = True
except:
    pass

@st.cache_data(ttl=86400)
def safe_geocode(country_name, c_lat_fallback):
    if not GEO_ENABLED:
        return c_lat_fallback, 70.0, country_name
    try:
        geolocator = Nominatim(user_agent="solarx_app_final_v3", timeout=3)
        location = geolocator.geocode(country_name)
        if location:
            return location.latitude, location.longitude, location.address.split(',')[0]
        else:
            return c_lat_fallback, 70.0, country_name
    except:
        return c_lat_fallback, 70.0, country_name

@st.cache_data(ttl=1800)
def get_7day_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,cloud_cover_mean&timezone=auto"
        r = requests.get(url, timeout=7)
        data = r.json()
        daily = data['daily']
        week_data = []
        for i in range(7):
            week_data.append({
                'date': daily['time'][i],
                'temp_max': daily['temperature_2m_max'][i],
                'temp_min': daily['temperature_2m_min'][i],
                'wind_max': daily['wind_speed_10m_max'][i] * 3.6,
                'cloud': daily['cloud_cover_mean'][i]
            })
        return week_data
    except:
        return None

def calc_wind_load(wind_speed_kmh, tilt_angle, panel_qty):
    wind_ms = wind_speed_kmh / 3.6
    q = 0.613 * wind_ms**2
    cp = 1.2 if tilt_angle > 30 else 0.8
    force_per_panel = q * cp * 2.6 / 1000
    total_force = force_per_panel * panel_qty
    return total_force

def calc_lightning_protection(building_height):
    if building_height > 20:
        rod_height = building_height + 2
        radius = 20
    else:
        rod_height = building_height + 1.5
        radius = 30
    return rod_height, radius
# --- 120+ COUNTRIES DATABASE ---

    
}

panel_db = {
    "Jinko 545W Mono PERC": [21.5, 0.55, 0.28, -0.35, 49.8, 13.8, "Tier-1"],
    "Trina 550W Mono PERC": [21.8, 0.58, 0.29, -0.36, 50.1, 13.9, "Tier-1"],
    "LONGi 540W Hi-MO4": [21.2, 0.52, 0.27, -0.35, 49.5, 13.7, "Tier-1"],
    #... baqi panels...
}

battery_db = {
    "LiFePO4 LFP": [94, 6000, 180, 2.0, 48, "Cobalt Free"],
    "NMC Lithium": [92, 4000, 220, 2.5, 48, "High Energy"],
    "Lead Acid AGM": [85, 1200, 120, 5.0, 24, "Cheap"],
    "No Battery": [0, 0, 0, 0, 0, "Grid Only"]
}
# --- 120+ COUNTRIES DATABASE [Lat, Currency, Export, Import, ESG, Labor, Sourcing, GHI, Elec%, Voltage, Frequency, Wind_kmh, Wind_Zone] ---
db = {
    "Afghanistan": [33.9, "AFN", 5, 12, "B", "High", "Import", 5.2, 98, 220, 50, 45, "High"], "Albania": [41.1, "ALL", 10, 18, "B+", "Medium", "EU Import", 4.1, 100, 230, 50, 25, "Low"],
    "Algeria": [28.0, "DZD", 4, 12, "B", "Medium", "Local", 6.0, 99, 230, 50, 55, "Extreme"], "Andorra": [42.5, "EUR", 0.12, 0.28, "A+", "Very Low", "EU Certified", 4.3, 100, 230, 50, 30, "Moderate"],
    "Angola": [-11.2, "AOA", 15, 30, "C", "High", "Import", 5.5, 42, 220, 50, 35, "Moderate"], "Argentina": [-38.4, "ARS", 25, 65, "B+", "Medium", "Local", 5.1, 100, 220, 50, 70, "Extreme"],
    "Armenia": [40.2, "AMD", 12, 25, "B+", "Medium", "Import", 4.2, 100, 230, 50, 40, "High"], "Australia": [-25.2, "AUD", 0.10, 0.35, "A+", "Very Low", "AU Certified", 5.8, 100, 230, 50, 85, "Extreme"],
    "Austria": [47.5, "EUR", 0.15, 0.45, "A+", "Very Low", "EU Certified", 3.4, 100, 230, 50, 35, "Moderate"], "Azerbaijan": [40.1, "AZN", 0.05, 0.12, "B", "Medium", "Import", 4.8, 100, 220, 50, 50, "High"],
    "Bahrain": [26.0, "BHD", 0.02, 0.06, "A", "Low", "GCC", 5.9, 100, 230, 50, 60, "Extreme"], "Bangladesh": [23.6, "BDT", 7.5, 14.0, "B", "Medium", "Local Assembly", 4.6, 99, 220, 50, 90, "Extreme"],
    "Belgium": [50.5, "EUR", 0.12, 0.52, "A+", "Very Low", "EU Certified", 2.9, 100, 230, 50, 40, "High"], "Bhutan": [27.5, "BTN", 3, 8, "A", "Low", "Hydro+Solar", 4.5, 99, 230, 50, 30, "Moderate"],
    "Bolivia": [-16.2, "BOB", 0.4, 0.9, "B", "Medium", "Import", 5.8, 94, 220, 50, 25, "Low"], "Bosnia": [44.2, "BAM", 0.08, 0.16, "B+", "Medium", "EU Import", 3.6, 100, 230, 50, 45, "High"],
    "Botswana": [-22.3, "BWP", 1.2, 2.4, "B+", "Medium", "Local", 6.1, 72, 230, 50, 50, "High"], "Brazil": [-14.2, "BRL", 0.55, 1.15, "A-", "Low", "Local Mfg", 5.5, 99, 220, 60, 60, "Extreme"],
    "Bulgaria": [42.7, "BGN", 0.09, 0.18, "A-", "Low", "EU Certified", 3.8, 100, 230, 50, 40, "High"], "Burkina Faso": [12.4, "XOF", 85, 170, "C", "High", "Import", 5.8, 19, 220, 50, 55, "Extreme"],
    "Burundi": [-3.4, "BIF", 180, 350, "C", "High", "Import", 5.2, 11, 220, 50, 20, "Low"], "Cambodia": [12.6, "KHR", 600, 1200, "B", "Medium", "Import", 5.0, 89, 230, 50, 70, "Extreme"],
    "Cameroon": [6.3, "XAF", 75, 150, "C", "High", "Import", 5.0, 64, 220, 50, 35, "Moderate"], "Canada": [56.1, "CAD", 0.08, 0.24, "A+", "Very Low", "US/CA Certified", 3.7, 100, 120, 60, 80, "Extreme"],
    "Chile": [-35.6, "CLP", 65, 155, "A", "Low", "Local", 6.2, 100, 220, 50, 75, "Extreme"], "China": [35.8, "CNY", 0.42, 0.72, "C+", "High", "Global Supply", 4.3, 100, 220, 50, 50, "High"],
    "Colombia": [4.5, "COP", 380, 750, "B+", "Medium", "Import", 4.5, 99, 110, 60, 30, "Moderate"], "Croatia": [45.1, "EUR", 0.10, 0.20, "A", "Low", "EU Certified", 3.7, 100, 230, 50, 50, "High"],
    "Cuba": [21.5, "CUP", 2.5, 5.0, "B", "Medium", "Import", 5.4, 100, 120, 60, 100, "Extreme"], "Cyprus": [35.1, "EUR", 0.15, 0.30, "A", "Low", "EU Certified", 5.6, 100, 230, 50, 55, "Extreme"],
    "Czech": [49.8, "CZK", 2.2, 4.8, "A", "Low", "EU Certified", 3.1, 100, 230, 50, 35, "Moderate"], "Denmark": [56.2, "DKK", 0.65, 2.80, "A+", "Very Low", "EU Certified", 2.7, 100, 230, 50, 90, "Extreme"],
    "Djibouti": [11.6, "DJF", 30, 60, "C", "High", "Import", 6.2, 61, 220, 50, 65, "Extreme"], "Dominican": [18.7, "DOP", 8.5, 17, "B", "Medium", "Import", 5.5, 99, 120, 60, 85, "Extreme"],
    "Ecuador": [-1.8, "USD", 0.10, 0.20, "B+", "Medium", "Import", 4.8, 97, 120, 60, 25, "Low"], "Egypt": [26.8, "EGP", 1.2, 2.6, "B", "Medium", "Local Assembly", 6.1, 100, 220, 50, 50, "High"],
    "El Salvador": [13.8, "USD", 0.14, 0.28, "B+", "Medium", "Import", 5.4, 99, 120, 60, 45, "High"], "Estonia": [58.6, "EUR", 0.12, 0.28, "A+", "Very Low", "EU Certified", 2.8, 100, 230, 50, 70, "Extreme"],
    "Ethiopia": [9.1, "ETB", 0.5, 1.2, "B", "Medium", "China Import", 5.9, 51, 220, 50, 40, "High"], "Fiji": [-18.1, "FJD", 0.25, 0.50, "A-", "Low", "Import", 5.3, 99, 240, 50, 95, "Extreme"],
    "Finland": [61.9, "EUR", 0.08, 0.38, "A+", "Very Low", "EU Certified", 2.5, 100, 230, 50, 60, "Extreme"], "France": [46.2, "EUR", 0.15, 0.34, "A+", "Very Low", "EU Certified", 3.5, 100, 230, 50, 45, "High"],
    "Gabon": [-0.8, "XAF", 95, 190, "B", "Medium", "Import", 4.9, 87, 220, 50, 30, "Moderate"], "Georgia": [42.3, "GEL", 0.15, 0.30, "B+", "Medium", "Import", 4.2, 100, 220, 50, 50, "High"],
    "Germany": [51.1, "EUR", 0.12, 0.48, "A+", "Very Low", "EU Certified", 3.0, 100, 230, 50, 55, "Extreme"], "Ghana": [7.9, "GHS", 0.50, 1.0, "B", "Medium", "Import", 5.4, 86, 230, 50, 40, "High"],
    "Greece": [39.0, "EUR", 0.18, 0.38, "A", "Low", "EU Import", 4.5, 100, 230, 50, 65, "Extreme"], "Guatemala": [15.8, "GTQ", 1.2, 2.4, "B", "Medium", "Import", 5.5, 93, 120, 60, 35, "Moderate"],
    "Honduras": [14.1, "HNL", 4.5, 9.0, "B", "Medium", "Import", 5.6, 88, 120, 60, 70, "Extreme"], "Hungary": [47.2, "HUF", 35, 75, "A-", "Low", "EU Certified", 3.4, 100, 230, 50, 40, "High"],
    "Iceland": [64.9, "ISK", 8, 18, "A+", "Very Low", "Geothermal", 2.2, 100, 230, 50, 120, "Extreme"], "India": [20.5, "INR", 6.2, 12.5, "A-", "Low", "Local Mfg", 5.4, 99, 230, 50, 60, "Extreme"],
    "Indonesia": [-0.7, "IDR", 1500, 3400, "B", "Medium", "Local", 4.8, 99, 220, 50, 50, "High"], "Iran": [32.4, "IRR", 800, 2000, "B", "Medium", "Local", 5.6, 100, 220, 50, 70, "Extreme"],
    "Iraq": [33.2, "IQD", 70, 160, "C", "High", "Import", 5.8, 99, 220, 50, 55, "Extreme"], "Ireland": [53.1, "EUR", 0.22, 0.55, "A+", "Very Low", "EU Certified", 2.7, 100, 230, 50, 95, "Extreme"],
    "Israel": [31.0, "ILS", 0.40, 0.60, "A", "Low", "Local", 5.7, 100, 230, 50, 50, "High"], "Italy": [41.8, "EUR", 0.20, 0.50, "A", "Low", "EU Certified", 4.2, 100, 230, 50, 50, "High"],
    "Jamaica": [18.1, "JMD", 25, 50, "B+", "Medium", "Import", 5.6, 99, 110, 50, 100, "Extreme"], "Japan": [36.2, "JPY", 21, 42, "A+", "Very Low", "JP Certified", 3.8, 100, 100, 50, 110, "Extreme"],
    "Jordan": [30.5, "JOD", 0.08, 0.18, "B+", "Medium", "Local", 5.8, 100, 230, 50, 60, "Extreme"], "Kazakhstan": [48.0, "KZT", 8, 18, "B", "Medium", "Local", 4.6, 100, 220, 50, 65, "Extreme"],
    "Kenya": [-1.2, "KES", 12, 28, "B", "Medium", "Import", 5.7, 76, 240, 50, 35, "Moderate"], "Kuwait": [29.3, "KWD", 0.02, 0.08, "A", "Low", "GCC", 5.9, 100, 240, 50, 70, "Extreme"],
    "Kyrgyzstan": [41.2, "KGS", 2.5, 5.0, "B", "Medium", "Import", 4.5, 100, 220, 50, 45, "High"], "Latvia": [56.9, "EUR", 0.11, 0.24, "A", "Low", "EU Certified", 2.8, 100, 230, 50, 60, "Extreme"],
    "Lebanon": [33.9, "LBP", 120, 250, "C", "High", "Import", 5.5, 98, 220, 50, 55, "Extreme"], "Libya": [26.3, "LYD", 0.15, 0.30, "C", "High", "Import", 6.0, 99, 230, 50, 65, "Extreme"],
    "Lithuania": [55.2, "EUR", 0.10, 0.22, "A", "Low", "EU Certified", 2.9, 100, 230, 50, 60, "Extreme"], "Luxembourg": [49.8, "EUR", 0.18, 0.36, "A+", "Very Low", "EU Certified", 3.0, 100, 230, 50, 40, "High"],
    "Madagascar": [-18.8, "MGA", 450, 900, "C", "High", "Import", 5.6, 36, 220, 50, 75, "Extreme"], "Malawi": [-13.9, "MWK", 85, 170, "C", "High", "Import", 5.7, 12, 230, 50, 30, "Moderate"],
    "Malaysia": [4.2, "MYR", 0.38, 0.68, "A-", "Low", "Local Mfg", 4.7, 100, 240, 50, 45, "High"], "Mali": [17.6, "XOF", 90, 180, "C", "High", "Import", 5.9, 38, 220, 50, 50, "High"],
    "Malta": [35.9, "EUR", 0.16, 0.32, "A", "Low", "EU Certified", 5.4, 100, 230, 50, 70, "Extreme"], "Mexico": [23.6, "MXN", 2.2, 4.8, "B+", "Medium", "US Import", 5.6, 99, 127, 60, 80, "Extreme"],
    "Mongolia": [46.9, "MNT", 180, 360, "B", "Medium", "Import", 4.3, 89, 230, 50, 80, "Extreme"], "Morocco": [31.7, "MAD", 1.1, 2.2, "B+", "Medium", "Local", 5.9, 99, 220, 50, 55, "Extreme"],
    "Mozambique": [-18.7, "MZN", 4.5, 9.0, "C", "High", "Import", 5.8, 34, 220, 50, 85, "Extreme"], "Myanmar": [19.7, "MMK", 80, 160, "C", "High", "Import", 5.0, 50, 230, 50, 75, "Extreme"],
    "Namibia": [-22.6, "NAD", 1.8, 3.6, "B+", "Medium", "Import", 6.2, 56, 220, 50, 70, "Extreme"], "Nepal": [28.3, "NPR", 8.2, 18.5, "B", "Medium", "India Import", 4.7, 95, 230, 50, 40, "High"],
    "Netherlands": [52.1, "EUR", 0.16, 0.55, "A+", "Very Low", "EU Certified", 2.8, 100, 230, 50, 85, "Extreme"], "New Zealand": [-40.9, "NZD", 0.11, 0.40, "A+", "Very Low", "AU/NZ", 4.4, 100, 230, 50, 90, "Extreme"],
    "Nicaragua": [12.9, "NIO", 4.2, 8.4, "B", "Medium", "Import", 5.5, 97, 120, 60, 80, "Extreme"], "Niger": [17.6, "XOF", 95, 190, "C", "High", "Import", 6.0, 19, 220, 50, 55, "Extreme"],
    "Nigeria": [9.0, "NGN", 70, 160, "C", "High", "Import", 5.5, 62, 230, 50, 45, "High"], "North Korea": [40.3, "KPW", 5, 10, "C", "High", "Import", 4.2, 26, 220, 60, 60, "Extreme"],
    "Norway": [60.4, "NOK", 0.9, 2.8, "A+", "Very Low", "EU Certified", 2.3, 100, 230, 50, 80, "Extreme"], "Oman": [21.5, "OMR", 0.03, 0.12, "A", "Low", "GCC", 6.0, 100, 240, 50, 65, "Extreme"],
    "Pakistan": [30.3, "PKR", 42.0, 82.0, "B+", "Medium", "China Import", 5.3, 97, 220, 50, 55, "Extreme"], "Palestine": [31.9, "ILS", 0.45, 0.90, "C", "High", "Import", 5.7, 100, 230, 50, 50, "High"],
    "Panama": [8.4, "USD", 0.15, 0.30, "A-", "Low", "Import", 4.9, 94, 120, 60, 45, "High"], "Paraguay": [-23.4, "PYG", 350, 700, "B+", "Medium", "Import", 5.1, 99, 220, 50, 40, "High"],
    "Peru": [-9.1, "PEN", 0.32, 0.68, "B+", "Medium", "Import", 5.4, 99, 220, 60, 35, "Moderate"], "Philippines": [12.8, "PHP", 6.2, 14.0, "B", "Medium", "China Import", 5.1, 94, 220, 60, 95, "Extreme"],
    "Poland": [51.9, "PLN", 0.45, 0.95, "A", "Low", "EU Certified", 3.1, 100, 230, 50, 50, "High"], "Portugal": [39.3, "EUR", 0.14, 0.32, "A", "Low", "EU Certified", 4.3, 100, 230, 50, 55, "Extreme"],
    "Qatar": [25.3, "QAR", 0.15, 0.38, "A", "Low", "GCC", 5.9, 100, 240, 50, 60, "Extreme"], "Romania": [45.9, "RON", 0.45, 0.95, "A-", "Low", "EU Certified", 3.6, 100, 230, 50, 45, "High"],
    "Russia": [61.5, "RUB", 3.5, 6.2, "B", "Medium", "Local", 3.2, 100, 220, 50, 70, "Extreme"], "Rwanda": [-1.9, "RWF", 150, 300, "B+", "Medium", "Import", 5.3, 35, 230, 50, 25, "Low"],
    "Saudi Arabia": [23.8, "SAR", 0.15, 0.32, "A", "Low", "GCC Local", 6.1, 100, 220, 60, 65, "Extreme"], "Senegal": [14.7, "XOF", 85, 170, "B", "Medium", "Import", 5.8, 70, 230, 50, 50, "High"],
    "Serbia": [44.0, "RSD", 6, 12, "B+", "Medium", "Import", 3.7, 100, 230, 50, 45, "High"], "Singapore": [1.3, "SGD", 0.28, 0.45, "A+", "Very Low", "Import", 4.6, 100, 230, 50, 40, "High"],
    "Slovakia": [48.7, "EUR", 0.12, 0.26, "A", "Low", "EU Certified", 3.2, 100, 230, 50, 45, "High"], "Slovenia": [46.1, "EUR", 0.13, 0.27, "A+", "Very Low", "EU Certified", 3.5, 100, 230, 50, 50, "High"],
    "Somalia": [5.1, "SOS", 200, 400, "C", "High", "Import", 6.0, 35, 220, 50, 70, "Extreme"], "South Africa": [-30.5, "ZAR", 1.9, 3.8, "B+", "Medium", "Local", 5.7, 85, 230, 50, 60, "Extreme"],
    "South Korea": [37.5, "KRW", 95, 180, "A+", "Very Low", "KR Certified", 3.8, 100, 220, 60, 75, "Extreme"], "South Sudan": [6.5, "SSP", 25, 50, "C", "High", "Import", 5.9, 7, 230, 50, 40, "High"],
    "Spain": [40.4, "EUR", 0.22, 0.45, "A", "Low", "EU Certified", 4.6, 100, 230, 50, 60, "Extreme"], "Sri Lanka": [7.8, "LKR", 25, 58, "B", "Medium", "India Import", 5.2, 99, 230, 50, 80, "Extreme"],
    "Sudan": [15.5, "SDG", 2.5, 5.0, "C", "High", "Import", 6.1, 52, 230, 50, 60, "Extreme"], "Sweden": [60.1, "SEK", 0.85, 2.40, "A+", "Very Low", "EU Certified", 2.6, 100, 230, 50, 75, "Extreme"],
    "Switzerland": [46.8, "CHF", 0.20, 0.45, "A+", "Very Low", "EU Certified", 3.4, 100, 230, 50, 40, "High"], "Syria": [34.8, "SYP", 35, 70, "C", "High", "Import", 5.8, 89, 220, 50, 55, "Extreme"],
    "Tajikistan": [38.5, "TJS", 0.25, 0.50, "B", "Medium", "Import", 4.6, 100, 220, 50, 50, "High"], "Tanzania": [-6.1, "TZS", 180, 420, "B", "Medium", "Import", 5.6, 38, 230, 50, 40, "High"],
    "Thailand": [15.8, "THB", 2.8, 6.0, "A-", "Low", "Local Mfg", 5.0, 100, 220, 50, 60, "Extreme"], "Tunisia": [34.0, "TND", 0.18, 0.38, "B+", "Medium", "Local", 5.8, 100, 230, 50, 55, "Extreme"],
    "Turkey": [38.9, "TRY", 3.5, 6.5, "B+", "Medium", "Local", 4.9, 100, 230, 50, 50, "High"], "UAE": [23.4, "AED", 0.22, 0.48, "A", "Low", "GCC Local", 5.9, 100, 220, 50, 65, "Extreme"],
    "Uganda": [1.4, "UGX", 580, 1160, "B", "Medium", "Import", 5.5, 42, 240, 50, 30, "Moderate"], "Ukraine": [48.3, "UAH", 1.8, 4.2, "B", "Medium", "EU Import", 3.4, 100, 220, 50, 50, "High"],
    "UK": [55.3, "GBP", 0.22, 0.58, "A+", "Very Low", "UK/EU Certified", 2.8, 100, 230, 50, 80, "Extreme"], "Uruguay": [-32.5, "UYU", 3.8, 7.6, "A", "Low", "Import", 4.8, 100, 230, 50, 70, "Extreme"],
    "USA": [37.0, "USD", 0.14, 0.30, "A+", "Very Low", "US Certified", 4.8, 100, 120, 60, 90, "Extreme"], "Uzbekistan": [41.3, "UZS", 250, 500, "B", "Medium", "Local", 5.2, 100, 220, 50, 50, "High"],
    "Venezuela": [6.4, "VES", 0.02, 0.04, "C", "High", "Import", 5.2, 99, 120, 60, 35, "Moderate"], "Vietnam": [14.0, "VND", 2200, 3800, "B+", "Medium", "Local Mfg", 4.8, 100, 220, 50, 85, "Extreme"],
    "Yemen": [15.4, "YER", 40, 80, "C", "High", "Import", 5.9, 47, 220, 50, 60, "Extreme"], "Zambia": [-13.1, "ZMW", 1.2, 2.4, "B", "Medium", "Import", 5.7, 45, 230, 50, 35, "Moderate"],
    "Zimbabwe": [-19.0, "USD", 0.10, 0.25, "C", "High", "Import", 5.8, 47, 230, 50, 40, "High"]
}
inverter_db = {
    "String Inverter": [97.5, 1.0, 800, "Central MPPT"],
    "Hybrid Inverter": [97.0, 1.02, 1500, "Battery + Grid"],
    "Micro Inverter": [96.8, 1.05, 1200, "Panel Level MPPT"]
}

structure_db = {
    "Low": {"type": "Aluminum Fixed Tilt", "tilt_max": 30, "material": "Anodized AL-6005-T5", "foundation": "Ground Screw", "clamp": "Standard"},
    "Moderate": {"type": "Galvanized Steel", "tilt_max": 25, "material": "Galvanized Steel", "foundation": "Concrete Ballast", "clamp": "Reinforced"},
    "High": {"type": "Galvanized Steel + Bracing", "tilt_max": 20, "material": "Galvanized Steel + Cross Bracing", "foundation": "Concrete Footing", "clamp": "Heavy Duty"},
    "Extreme": {"type": "Steel + Wind Deflector", "tilt_max": 15, "material": "S355 Steel + Wind Deflector", "foundation": "Deep Concrete Pile", "clamp": "Hurricane Rated"}
}

# --- CSS ---
st.markdown("""
<style>
.main-header {color: white; font-size: 42px; font-weight: 900; text-align: center;
background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); padding: 25px; border-radius: 20px; margin-bottom: 30px;}
.stMetric {background: rgba(255,255,255,0.85); border-radius: 15px; padding: 20px; box-shadow: 0 8px 32px rgba(31,38,135,0.15);}
.feature-box {background: rgba(255,255,255,0.9); padding: 28px; border-radius: 20px; margin-bottom: 20px;}
.info-label {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; border-radius: 12px; font-weight: 700;}
</style>
""", unsafe_allow_html=True)  
# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.title("⚡ Solar Estimator Pro")
    country = st.selectbox("🌍 Country - 120+ Options", sorted(db.keys()))
    country_data = list(db[country]) + [None] * 15
    c_lat, c_curr, c_sale, c_buy, esg_rating, labor_risk, sourcing, avg_ghi, elec_access, grid_v, grid_f, wind_kmh_db, wind_zone = country_data[:13]

    st.divider()
    st.markdown("### 🔐 Weather Settings")
    use_live_weather = st.checkbox("🌐 Live Weather + 7 Day Report ON", value=False)
    password = st.text_input("Password for Live Data", type="password", value="")
    LIVE_PASSWORD = "solar2026"

    st.divider()
    panel_type = st.selectbox("Solar Panel", list(panel_db.keys()))
    p_eff, p_cost, voc, p_temp, voc_std, isc, p_note = panel_db[panel_type]
    p_qty = st.number_input("Number of Panels", 1, 1000, 20)

    inverter_type = st.selectbox("Inverter", list(inverter_db.keys()))
    inv_eff, inv_bonus, inv_cost, inv_note = inverter_db[inverter_type]
    tilt = st.slider("Tilt Angle °", 0, 60, 25)
    azimuth = st.slider("Azimuth °", -180, 180, 0)

    building_height = st.number_input("Building Height m", 3.0, 50.0, 6.0)
    wire_length = st.number_input("DC Cable Length m", 10, 200, 50)
    cable_size = st.selectbox("DC Cable mm²", [4, 6, 10, 16, 25])

    st.divider()
    battery_type = st.selectbox("Battery", list(battery_db.keys()))
    b_eff, b_cycles, b_cost, b_degrade, b_voltage, b_note = battery_db[battery_type]
    has_batt = battery_type!= "No Battery"
    b_cap = st.number_input("Battery kWh", 0.0, 500.0, 20.0) if has_batt else 0
    dod = st.slider("DoD %", 50, 95, 85) if has_batt else 0

    h_load = st.number_input("Daily Load kWh", 1.0, 500.0, 55.0)
    sun_h = st.slider("Peak Sun Hours", 3.0, 8.5, float(avg_ghi))
    sys_loss = st.slider("System Losses %", 8, 30, 14)
    soiling = st.slider("Soiling %", 0, 20, 5)
    temp_ambient = st.slider("Temp °C", 15, 50, 28)

    st.divider()
    buy_rate = st.number_input(f"Buy Rate {c_curr}", value=float(c_buy))
    sell_rate = st.number_input(f"Sell Rate {c_curr}", value=float(c_sale))
    tax_val = st.slider("Tax %", 0, 30, 17)
    install_cost = st.number_input(f"Install/kWp {c_curr}", value=42000.0 if country=="Pakistan" else 750.0)
    discount_rate = st.slider("Discount %", 3, 15, 8)

# --- LOCATION LOGIC - WEATHER ON/OFF ---
if use_live_weather and password == LIVE_PASSWORD and GEO_ENABLED:
    lat, lon, location_name = safe_geocode(country, c_lat)
    week_weather = get_7day_weather(lat, lon)
    if week_weather:
        st.sidebar.success(f"🌤️ Live: {location_name}")
        avg_cloud = np.mean([w['cloud'] for w in week_weather])
        avg_wind = np.mean([w['wind_max'] for w in week_weather])
        sun_h = max(3.0, avg_ghi * (1 - avg_cloud/100 * 0.8))
        wind = avg_wind
        cloud = avg_cloud
        show_map = True
    else:
        st.sidebar.warning("⚠️ API fail. DB data use.")
        lat, lon, location_name = c_lat, 70.0, country
        wind, cloud = wind_kmh_db, 20
        week_weather = None
        show_map = False
else:
    lat, lon, location_name = c_lat, 70.0, country # LIVE LOCATION HIDE
    wind, cloud = wind_kmh_db, 20
    week_weather = None
    show_map = False
    if use_live_weather:
        st.sidebar.error("❌ Wrong password. Manual mode.")

# --- CALCULATIONS ---
sys_size = (p_eff * p_qty) / 1000
panels_per_string = int(1000 / voc_std)
strings = math.ceil(p_qty / panels_per_string)
voc_string = voc_std * panels_per_string
isc_string = isc * strings
mppt_voltage = voc_string * 0.8

wind_force = calc_wind_load(wind, tilt, p_qty)
struct = structure_db[wind_zone]
wind_safe = wind_force < (sys_size * 50)

current_dc = (sys_size * 1000) / 400
voltage_drop = (current_dc * wire_length * 0.0175) / cable_size
vd_percent = (voltage_drop / mppt_voltage) * 100 if mppt_voltage > 0 else 0

angle_eff = np.cos(np.radians(tilt - abs(c_lat))) * np.cos(np.radians(azimuth))
temp_loss = 1 + (p_temp/100) * (temp_ambient + 25 - 25)
soiling_loss = 1 - soiling/100
weather_factor = 1 - cloud*0.008 + wind*0.0003

daily_yield = sys_size * sun_h * ((100-sys_loss)/100) * angle_eff * (p_eff/21.5) * temp_loss * soiling_loss * (inv_eff/100) * inv_bonus * weather_factor

hours = np.arange(24)
gen_24 = [daily_yield/12 * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
gen_24 = [max(0, g) for g in gen_24]
load_24 = [(h_load/24) * (2.8 if (h > 18 or h < 7) else 0.7) for h in hours]

soc = []
c_soc = b_cap * (dod/100) if has_batt else 0
for g, l in zip(gen_24, load_24):
    if has_batt:
        diff = g - l
        c_soc = max(0, min(b_cap, c_soc + diff * (b_eff/100)))
    soc.append(c_soc)

export_24 = [max(0, g - l - (soc[i]-soc[i-1] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_24, load_24))]
import_24 = [max(0, l - g - (soc[i-1]-soc[i] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_24, load_24))]

rod_height, protection_radius = calc_lightning_protection(building_height)

battery_cost = b_cap * b_cost if has_batt else 0
panel_cost = sys_size * 1000 * p_cost
inverter_cost = sys_size * inv_cost
structure_cost = sys_size * 150
cable_cost = wire_length * cable_size * 2.5
lightning_cost = rod_height * 80
gross_cost = panel_cost + battery_cost + inverter_cost + structure_cost + cable_cost + lightning_cost + sys_size*install_cost
net_cost = gross_cost * (1 - 30/100 if country=="Pakistan" else 1)

years = np.arange(25)
yearly_gen = [sum(gen_24)*365 * (1-b_degrade/100)**y for y in years]
yearly_profit = [y * ((1-sum(export_24)/sum(gen_24))*buy_rate + (sum(export_24)/sum(gen_24))*sell_rate) * (1-tax_val/100) for y in yearly_gen]
payback = net_cost / yearly_profit[0] if yearly_profit[0] > 0 else 99
npv = sum([p/((1+discount_rate/100)**i) for i,p in enumerate(yearly_profit)]) - net_cost

# 7 DIN KA OUTPUT
if week_weather:
    weekly_output = []
    for w in week_weather:
        day_sun = max(3.0, avg_ghi * (1 - w['cloud']/100 * 0.8))
        day_factor = 1 - w['cloud']*0.008 + w['wind_max']*0.0003
        day_gen = sys_size * day_sun * ((100-sys_loss)/100) * angle_eff * (p_eff/21.5) * temp_loss * soiling_loss * (inv_eff/100) * inv_bonus * day_factor
        weekly_output.append({'Date': w['date'], 'Gen kWh': round(day_gen, 2), 'Cloud %': w['cloud'], 'Wind km/h': round(w['wind_max'], 1), 'Risk': "🔴" if w['wind_max']>80 else "🟠" if w['wind_max']>50 else "🟢"})
    weekly_df = pd.DataFrame(weekly_output)
else:
    weekly_df = pd.DataFrame({'Date': ['Manual Mode'], 'Gen kWh': [round(daily_yield*7, 2)], 'Cloud %': [cloud], 'Wind km/h': [wind], 'Risk': ['N/A']})
# --- HEADER ---
st.markdown(f"<div class='main-header'>⚡ Solar Power Estimator Pro: {country}</div>", unsafe_allow_html=True)

# --- KPI 10 METRICS ---
k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = st.columns(10)
k1.metric("System kWp", f"{sys_size:.2f}")
k2.metric("Daily Gen", f"{sum(gen_24):.1f} kWh")
k3.metric("Weekly Gen", f"{daily_yield*7:.1f} kWh")
k4.metric("VOC String", f"{voc_string:.0f} V")
k5.metric("VD Loss", f"{vd_percent:.2f}%")
k6.metric("Battery", battery_type.split()[0] if has_batt else "None")
k7.metric("Self Use", f"{(1-sum(import_24)/h_load)*100:.1f}%")
k8.metric("ESG", esg_rating)
k9.metric("Wind Force", f"{wind_force:.1f} kN")
k10.metric("Wind Risk", wind_zone, f"{wind:.0f} km/h", delta_color="inverse" if wind_zone in ["High","Extreme"] else "normal")
st.divider()

# --- 7 TABS ---
tabs = st.tabs(["📊 7 Day Report", "⚡ Energy", "🔧 Technical", "💰 Financial", "🌿 Eco", "⚙️ Protection", "📄 Export"])

with tabs[0]:
    st.markdown("<span class='info-label'>7 DIN KA WEATHER + GENERATION REPORT</span>", unsafe_allow_html=True)
    if week_weather and show_map:
        st.success(f"✅ Live Weather Active for {location_name}")
        col1, col2 = st.columns([1, 1])
        with col1:
            m = folium.Map(location=[lat, lon], zoom_start=8)
            folium.Marker([lat, lon], popup=country).add_to(m)
            st_folium(m, height=350, width=400)
        with col2:
            st.dataframe(weekly_df, use_container_width=True, height=350)
            st.metric("7 Day Total Gen", f"{weekly_df['Gen kWh'].sum():.1f} kWh")
            st.metric("Avg Cloud", f"{weekly_df['Cloud %'].mean():.0f}%")
            st.metric("Avg Wind", f"{weekly_df['Wind km/h'].mean():.1f} km/h")
    else:
        st.info("💡 Manual Mode: Weather OFF hai. Sidebar inputs se calculation ho rahi hai.")
        st.dataframe(weekly_df, use_container_width=True)

with tabs[1]:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=gen_24, name="Solar Gen", fill='tozeroy', line=dict(color='#667eea', width=4)))
    fig.add_trace(go.Scatter(x=hours, y=load_24, name="Load", line=dict(color='#f5576c', width=3)))
    if has_batt:
        fig.add_trace(go.Scatter(x=hours, y=soc, name="Battery SOC", line=dict(color='#4ade80', width=3)))
    fig.update_layout(height=500, plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)')
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='feature-box'><b>Panel:</b><br>{panel_type}<br>Eff: {p_eff}%<br>VOC: {voc}V<br>ISC: {isc}A</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='feature-box'><b>Array:</b><br>Panels: {p_qty}<br>Strings: {strings}<br>Per String: {panels_per_string}<br>Area: {p_qty*2.2:.1f} m²</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='feature-box'><b>Electrical:</b><br>DC Voltage: {voc_string:.0f}V<br>DC Current: {isc_string:.1f}A<br>MPPT: {mppt_voltage:.0f}V</div>", unsafe_allow_html=True)

with tabs[3]:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Cost", f"{gross_cost:,.0f} {c_curr}")
    col2.metric("After Subsidy", f"{net_cost:,.0f} {c_curr}")
    col3.metric("Payback", f"{payback:.1f} Years")
    col4.metric("25Yr NPV", f"{npv:,.0f} {c_curr}")
    st.progress(min(1.0, payback/12))

with tabs[4]:
    co2_annual = sum(gen_24) * 365 * 0.82 / 1000
    st.success(f"CO2 Avoided: **{co2_annual:.2f} Tons/Year** | Trees: {int(co2_annual * 18)}")
    st.metric("ESG Rating", esg_rating)
    st.write(f"Sourcing: {sourcing} | Labor Risk: {labor_risk}")

with tabs[5]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='feature-box'><b>Structure:</b><br>{struct['type']}<br>Max Tilt: {struct['tilt_max']}°<br>Wind Zone: {wind_zone}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='feature-box'><b>Material:</b><br>{struct['material']}<br>Clamp: {struct['clamp']}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='feature-box'><b>Lightning:</b><br>Rod Height: {rod_height:.1f} m<br>Radius: {protection_radius} m<br>Cost: {lightning_cost:.0f} {c_curr}</div>", unsafe_allow_html=True)
    if tilt > struct['tilt_max']:
        st.error(f"⚠️ WARNING: Tilt {tilt}° exceeds max {struct['tilt_max']}° for {wind_zone} zone!")
    if not wind_safe:
        st.error(f"⚠️ HIGH WIND LOAD: {wind_force:.1f} kN detected!")

with tabs[6]:
    st.markdown("<span class='info-label'>📤 EXPORT REPORT</span>", unsafe_allow_html=True)
    df = pd.DataFrame({
        "Hour": hours,
        "Generation_kW": [round(x, 3) for x in gen_24],
        "Load_kW": [round(x, 3) for x in load_24],
        "Export_kW": [round(x, 3) for x in export_24],
        "Import_kW": [round(x, 3) for x in import_24],
        "Battery_SOC_kWh": [round(x, 3) for x in soc]
    })
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, file_name=f"SolarX_{country}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
    st.dataframe(df, height=350, use_container_width=True)    
