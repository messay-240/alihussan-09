import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Solar Power Estemaiter", layout="wide", page_icon="⚡")

# --- DARK PREMIUM THEME ---
st.markdown("""
    <style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 75%, #f5576c 100%); 
    background-attachment: fixed;
    color: #1a1a2e; 
}

.main-header { 
    color: white; 
    font-size: 52px; 
    font-weight: 900; 
    text-shadow: 0 8px 32px rgba(0,0,0,0.3); 
    margin-bottom: 40px; 
    text-align: center;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    padding: 30px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.3);
}

[data-testid="stMetricValue"] { 
    color: #667eea!important; 
    font-size: 36px; 
    font-weight: 900; 
}

.stMetric { 
    background: rgba(255,255,255,0.85); 
    backdrop-filter: blur(20px); 
    border: 1px solid rgba(255,255,255,0.5); 
    border-radius: 20px; 
    padding: 24px; 
    box-shadow: 0 8px 32px rgba(31,38,135,0.15);
    transition: transform 0.3s;
}
.stMetric:hover { transform: translateY(-5px); }

.feature-box { 
    background: rgba(255,255,255,0.9); 
    backdrop-filter: blur(20px); 
    border: 1px solid rgba(255,255,255,0.6); 
    padding: 28px; 
    border-radius: 20px; 
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(31,38,135,0.12);
}

.info-label { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    color: white; 
    padding: 10px 20px; 
    border-radius: 12px; 
    font-size: 1rem; 
    font-weight: 700;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4);
}

div[data-testid="stTabs"] button {
    background: rgba(255,255,255,0.7);
    color: #667eea;
    border-radius: 12px;
    font-weight: 600;
    margin: 4px;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.sidebar .sidebar-content {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(20px);
}
    </style>
""", unsafe_allow_html=True)

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

panel_db = {
    "Mono PERC": [21.5, 0.55, 0.28, -0.35, 49.8, 13.8, "Standard"],
    "TOPCon N-Type": [23.8, 0.40, 0.32, -0.29, 50.2, 13.5, "High Eff"],
    "HJT Heterojunction": [24.5, 0.30, 0.38, -0.24, 49.5, 13.2, "Best Eff"],
    "Bifacial TOPCon": [24.0, 0.38, 0.35, -0.29, 50.0, 13.6, "Dual Glass"],
    "IBC Back Contact": [25.2, 0.25, 0.42, -0.22, 51.0, 12.8, "Premium"],
    "Perovskite Tandem": [29.5, 0.80, 0.55, -0.20, 52.0, 12.5, "Future"],
    "Thin Film CdTe": [18.5, 0.70, 0.22, -0.25, 48.0, 14.5, "Low Cost"]
}

battery_db = {
    "LiFePO4 LFP": [94, 6000, 180, 2.0, 48, "Cobalt Free"],
    "NMC Lithium": [92, 4000, 220, 2.5, 48, "High Energy"],
    "Lead Acid AGM": [85, 1200, 120, 5.0, 24, "Cheap"],
    "Sodium Ion": [90, 3000, 150, 3.0, 48, "Emerging"],
    "Solid State": [96, 8000, 350, 1.5, 48, "Future"],
    "No Battery": [0, 0, 0, 0, 0, "Grid Only"]
}

inverter_db = {
    "String Inverter": [97.5, 1.0, 800, "Central MPPT"],
    "Micro Inverter": [96.8, 1.05, 1200, "Panel Level MPPT"],
    "Hybrid Inverter": [97.0, 1.02, 1500, "Battery + Grid"],
    "Power Optimizer": [98.0, 1.03, 1400, "DC Optimizer"],
    "Central Inverter": [98.5, 0.98, 600, "Large Scale"]
}

# --- STRUCTURE & MATERIAL DATABASE based on Wind Zone ---
structure_db = {
    "Low": {"type": "Aluminum Fixed Tilt", "tilt_max": 30, "material": "Anodized AL-6005-T5", "foundation": "Ground Screw", "clamp": "Standard Mid/End"},
    "Moderate": {"type": "Galvanized Steel", "tilt_max": 25, "material": "Hot Dip Galvanized Steel Q235", "foundation": "Concrete Ballast", "clamp": "Reinforced Clamp"},
    "High": {"type": "Galvanized Steel + Bracing", "tilt_max": 20, "material": "Galvanized Steel + Cross Bracing", "foundation": "Concrete Footing", "clamp": "Heavy Duty Clamp"},
    "Extreme": {"type": "Steel Structure + Wind Deflector", "tilt_max": 15, "material": "S355 Steel + Wind Deflector", "foundation": "Deep Concrete Pile", "clamp": "Hurricane Rated Clamp"}
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Solar Power Estemaiter")
    country = st.selectbox("🌍 Country - 120+ Options", sorted(db.keys()))
    c_lat, c_curr, c_sale, c_buy, esg_rating, labor_risk, sourcing, avg_ghi, elec_access, grid_v, grid_f, wind_kmh, wind_zone = db[country]

    with st.expander("📐 Solar Array", expanded=True):
        panel_type = st.selectbox("Panel Technology", list(panel_db.keys()))
        p_eff, p_degrade, p_cost, p_temp, voc, isc, p_note = panel_db[panel_type]
        tilt = st.slider("Tilt °", 0, 90, int(abs(c_lat)))
        azimuth = st.slider("Azimuth °", -180, 180, 0)
        p_watt = st.number_input("Panel Wp", value=585)
        p_qty = st.number_input("Panel Qty", value=24)
        strings = st.number_input("Strings", value=2, min_value=1)
        panels_per_string = p_qty // strings if strings > 0 else p_qty

    with st.expander("🔌 Inverter System"):
        inverter_type = st.selectbox("Inverter Type", list(inverter_db.keys()))
        inv_eff, inv_bonus, inv_cost, inv_note = inverter_db[inverter_type]
        mppt_count = st.number_input("MPPT Channels", value=2, min_value=1)
        ac_output = st.selectbox("AC Output", ["Single Phase", "Three Phase"])

    with st.expander("🔋 Battery"):
        battery_type = st.selectbox("Battery Type", list(battery_db.keys()))
        b_eff, b_cycles, b_cost, b_degrade, b_voltage, b_note = battery_db[battery_type]
        has_batt = battery_type!= "No Battery"
        b_cap = st.number_input("Battery kWh", value=20.0) if has_batt else 0
        dod = st.slider("DoD %", 50, 95, 85) if has_batt else 0

    with st.expander("🏠 Load & Net Metering"):
        h_load = st.number_input("Daily Load kWh", value=55.0)
        net_metering = st.checkbox("Net Metering", value=True)
        subsidy = st.slider("Subsidy %", 0, 50, 30 if country=="Pakistan" else 0)

    with st.expander("🌤️ Environment"):
        sun_h = st.slider("Peak Sun Hours", 3.0, 8.5, float(avg_ghi))
        sys_loss = st.slider("System Losses %", 8, 30, 14)
        soiling = st.slider("Soiling %", 0, 20, 5)
        temp_ambient = st.slider("Temp °C", 15, 50, 28)
        wire_length = st.number_input("Wire Length m", value=50)
        cable_size = st.selectbox("DC Cable mm²", [4, 6, 10, 16, 25])

    with st.expander("💹 Financial"):
        buy_rate = st.number_input(f"Buy Rate {c_curr}", value=float(c_buy))
        sell_rate = st.number_input(f"Sell Rate {c_curr}", value=float(c_sale))
        tax_val = st.slider("Tax %", 0, 30, 17)
        install_cost = st.number_input(f"Install/kWp {c_curr}", value=42000.0 if country=="Pakistan" else 750.0)
        discount_rate = st.slider("Discount %", 3, 15, 8)

# --- CALCULATIONS ---
sys_size = (p_watt * p_qty) / 1000
voc_string = voc * panels_per_string
isc_string = isc * strings
mppt_voltage = voc_string * 0.8

track_bonus = 1.0
angle_eff = np.cos(np.radians(tilt - abs(c_lat))) * np.cos(np.radians(azimuth))
temp_loss = 1 + (p_temp/100) * (temp_ambient + 25 - 25)
soiling_loss = 1 - soiling/100

daily_yield = sys_size * sun_h * ((100-sys_loss)/100) * track_bonus * angle_eff * (p_eff/21.5) * temp_loss * soiling_loss * (inv_eff/100) * inv_bonus

hours = np.arange(24)
gen_24 = [daily_yield/12 * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
gen_24 = [max(0, g) for g in gen_24]
load_24 = [(h_load/24) * (2.8 if (h > 18 or h < 7) else 0.7) for h in hours]

# Battery SOC
soc = []
c_soc = b_cap * (dod/100) if has_batt else 0
for g, l in zip(gen_24, load_24):
    if has_batt:
        diff = g - l
        c_soc = max(0, min(b_cap, c_soc + diff * (b_eff/100)))
    soc.append(c_soc)

export_24 = [max(0, g - l - (soc[i]-soc[i-1] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_24, load_24))]
import_24 = [max(0, l - g - (soc[i-1]-soc[i] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_24, load_24))]

# Wire sizing
current_dc = isc_string * 1.25
voltage_drop = (current_dc * wire_length * 0.0175) / cable_size
vd_percent = (voltage_drop / mppt_voltage) * 100 if mppt_voltage > 0 else 0

years = np.arange(25)
yearly_gen = [sum(gen_24)*365 * (1-p_degrade/100)**y for y in years]
yearly_profit = [y * ((1-sum(export_24)/sum(gen_24))*buy_rate + (sum(export_24)/sum(gen_24))*sell_rate) * (1-tax_val/100) for y in yearly_gen]

# Get structure based on wind zone
struct = structure_db[wind_zone]

# --- HEADER ---
st.markdown(f"<div class='main-header'>⚡ Solar Power Estemaiter: {country}</div>", unsafe_allow_html=True)

# --- KPI 10 METRICS with WIND THREAT ---
k1, k2, k3, k4, k5, k6, k7, k8, k9, k10 = st.columns(10)
k1.metric("System kWp", f"{sys_size:.2f}")
k2.metric("Panel", panel_type.split()[0])
k3.metric("Inverter", inverter_type.split()[0])
k4.metric("Daily Gen", f"{sum(gen_24):.1f} kWh")
k5.metric("Battery", battery_type.split()[0] if has_batt else "None")
k6.metric("VOC String", f"{voc_string:.0f} V")
k7.metric("VD Loss", f"{vd_percent:.2f}%")
k8.metric("Self Use", f"{(1-sum(import_24)/h_load)*100:.1f}%")
k9.metric("ESG", esg_rating)

# WIND THREAT KPI
if wind_zone == "Extreme":
    k10.metric("Wind Risk", "EXTREME", f"{wind_kmh} km/h", delta_color="inverse")
elif wind_zone == "High":
    k10.metric("Wind Risk", "HIGH", f"{wind_kmh} km/h", delta_color="inverse")
elif wind_zone == "Moderate":
    k10.metric("Wind Risk", "MODERATE", f"{wind_kmh} km/h")
else:
    k10.metric("Wind Risk", "LOW", f"{wind_kmh} km/h", delta_color="normal")
st.divider()

# --- 14 TABS - New "Structure" tab added ---
tabs = st.tabs([
    "📊 Energy", "🔧 Technical", "🔌 Inverter", "🔋 Battery", "⚡ Electrical",
    "💰 Financial", "🌿 Eco", "🛡️ Ethics", "📈 Net Metering", "🤖 AI",
    "🌤️ Weather", "🏗️ Structure", "⚙️ Protection", "📄 Export"
])

with tabs[0]:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=gen_24,
        name="Solar Gen",
        fill='tozeroy',
        line=dict(color='#667eea', width=4),
        fillcolor='rgba(102,126,234,0.3)'
    ))
    fig.add_trace(go.Scatter(
        x=hours,
        y=load_24,
        name="Load",
        line=dict(color='#f5576c', width=3)
    ))
    if has_batt:
        fig.add_trace(go.Scatter(
            x=hours,
            y=soc,
            name="Battery",
            line=dict(color='#4ade80', width=3)
        ))
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(255,255,255,0.8)',
        paper_bgcolor='rgba(255,255,255,0)',
        font_color='#1a1a2e'
    )
    st.plotly_chart(fig, use_container_width=True)
with tabs[1]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='feature-box'><b>Panel:</b><br>{panel_type}<br>Eff: {p_eff}%<br>VOC: {voc}V<br>ISC: {isc}A</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='feature-box'><b>Array:</b><br>Panels: {p_qty}<br>Strings: {strings}<br>Per String: {panels_per_string}<br>Area: {p_qty*2.2:.1f} m²</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='feature-box'><b>Conditions:</b><br>Tilt: {tilt}°<br>Azimuth: {azimuth}°<br>Temp: {temp_ambient}°C<br>GHI: {avg_ghi} kWh/m²</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<span class='info-label'>INVERTER DESIGN</span>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Inverter Type", inverter_type)
        st.metric("Efficiency", f"{inv_eff}%")
        st.metric("MPPT Channels", mppt_count)
    with c2:
        st.metric("AC Output", ac_output)
        st.metric("Grid Voltage", f"{grid_v}V {grid_f}Hz")
        st.metric("Inverter Bonus", f"+{(inv_bonus-1)*100:.1f}%")
    with c3:
        st.markdown(f"<div class='feature-box'><b>Notes:</b><br>{inv_note}<br><br>DC Input: {voc_string:.0f}V<br>AC Output: {sys_size*inv_eff/100:.2f} kW</div>", unsafe_allow_html=True)

with tabs[3]:
    if has_batt:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Battery Type", battery_type)
            st.metric("Capacity", f"{b_cap} kWh")
            st.metric("Voltage", f"{b_voltage}V")
        with c2:
            st.metric("Efficiency", f"{b_eff}%")
            st.metric("DoD", f"{dod}%")
            st.metric("Cycles", f"{b_cycles:,}")
        with c3:
            st.markdown(f"<div class='feature-box'><b>Notes:</b><br>{b_note}<br><br>Backup: {b_cap/h_load*24:.1f} hours</div>", unsafe_allow_html=True)
    else:
        st.info("Grid-Tied System - No Battery")

with tabs[4]:
    st.markdown("<span class='info-label'>ELECTRICAL DESIGN</span>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("VOC String", f"{voc_string:.1f} V")
        st.metric("ISC String", f"{isc_string:.1f} A")
        st.metric("MPPT Voltage", f"{mppt_voltage:.1f} V")
    with c2:
        st.metric("DC Current", f"{current_dc:.1f} A")
        st.metric("Cable Size", f"{cable_size} mm²")
        st.metric("Voltage Drop", f"{voltage_drop:.2f} V")
    with c3:
        st.metric("VD %", f"{vd_percent:.2f}%")
        if vd_percent > 3:
            st.error("⚠️ VD > 3% - Increase cable")
        else:
            st.success("✅ VD OK")

with tabs[5]:
    battery_cost = b_cap * b_cost if has_batt else 0
    panel_cost = sys_size * 1000 * p_cost
    inverter_cost = sys_size * inv_cost
    gross_cost = panel_cost + battery_cost + inverter_cost + sys_size*install_cost
    net_cost = gross_cost * (1 - subsidy/100)
    payback = net_cost / yearly_profit[0] if yearly_profit[0] > 0 else 99
    npv = sum([p/((1+discount_rate/100)**i) for i,p in enumerate(yearly_profit)]) - net_cost

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Cost", f"{gross_cost:,.0f} {c_curr}")
    col2.metric("After Subsidy", f"{net_cost:,.0f} {c_curr}")
    col3.metric("Payback", f"{payback:.1f} Years")
    col4.metric("25Yr NPV", f"{npv:,.0f} {c_curr}")
    st.progress(min(1.0, payback/12))

with tabs[6]:
    co2_annual = sum(gen_24) * 365 * 0.82 / 1000
    st.success(f"CO2 Avoided: **{co2_annual:.2f} Tons/Year** | Trees: {int(co2_annual * 18)}")

with tabs[7]:
    st.markdown("<div class='feature-box'><b>🛡️ ESG Compliance</b></div>", unsafe_allow_html=True)
    st.metric("ESG Rating", esg_rating)
    st.write(f"Sourcing: {sourcing} | Labor Risk: {labor_risk}")

with tabs[8]:
    st.markdown("<span class='info-label'>NET METERING</span>", unsafe_allow_html=True)
    if net_metering:
        st.success("✅ Net Metering Active")
        st.metric("Export to Grid", f"{sum(export_24):.1f} kWh/day")
        st.metric("Credit Value", f"{sum(export_24)*sell_rate:,.0f} {c_curr}/day")
    else:
        st.warning("⚠️ Net Metering Off")

with tabs[9]:
    st.markdown("<div class='feature-box'><b>🤖 AI Diagnosis</b></div>", unsafe_allow_html=True)
    pr = (sum(gen_24) / (sys_size * sun_h)) * 100 if sys_size * sun_h > 0 else 0
    st.metric("Performance Ratio", f"{pr:.1f}%")
    if vd_percent > 3:
        st.write("⚠️ Increase cable size")
    if tilt > struct["tilt_max"]:
        st.warning(f"⚠️ Tilt {tilt}° > Max {struct['tilt_max']}° for {wind_zone} wind zone")
    if pr > 80:
        st.success("✅ Excellent design")

with tabs[10]:
    st.markdown("<span class='info-label'>WEATHER & WIND ANALYSIS</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        cloud = st.slider("Cloud Cover %", 0, 100, 20)
        wind_speed = st.slider("Wind Speed km/h", 0, 150, wind_kmh, key='wind_speed')
        weather_factor = 1 - cloud*0.008 + wind_speed*0.0003
        st.metric("Weather Yield", f"{daily_yield*weather_factor:.1f} kWh", f"{(weather_factor-1)*100:.1f}%")

    with col2:
        st.markdown(f"<b>🌪️ Wind Threat: {wind_zone} Zone</b>", unsafe_allow_html=True)
        st.metric("Avg Wind Speed", f"{wind_kmh} km/h")
        if wind_zone == "Extreme":
            st.error("🔴 EXTREME: >80 km/h - Structure damage risk!")
            st.write("• Use hurricane rated mounting")
            st.write("• Reduce tilt to <15°")
            st.write("• Add wind deflectors")
        elif wind_zone == "High":
            st.warning("🟠 HIGH: 50-80 km/h - Strong winds")
            st.write("• Cross bracing required")
            st.write("• Check bolts monthly")
        elif wind_zone == "Moderate":
            st.info("🟡 MODERATE: 30-50 km/h")
        else:
            st.success("🟢 LOW: <30 km/h - Safe")

with tabs[11]:
    st.markdown("<span class='info-label'>STRUCTURE & MATERIAL SPEC</span>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='feature-box'><b>Structure Type:</b><br>{struct['type']}<br><br><b>Max Tilt:</b> {struct['tilt_max']}°<br><b>Wind Zone:</b> {wind_zone}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='feature-box'><b>Material:</b><br>{struct['material']}<br><br><b>Clamp Type:</b><br>{struct['clamp']}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='feature-box'><b>Foundation:</b><br>{struct['foundation']}<br><br><b>Wind Load:</b> {wind_kmh} km/h</div>", unsafe_allow_html=True)

    if tilt > struct['tilt_max']:
        st.error(f"⚠️ WARNING: Selected tilt {tilt}° exceeds max {struct['tilt_max']}° for {wind_zone} wind zone. Reduce tilt or upgrade structure!")

with tabs[12]:
    st.markdown("<span class='info-label'>PROTECTION</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.write("**DC Protection:**")
        st.write(f"• DC Fuse: {current_dc*1.56:.0f} A")
        st.write(f"• DC Isolator: 1000V DC")
        st.write(f"• SPD: {voc_string*1.2:.0f}V")
    with c2:
        st.write("**AC Protection:**")
        st.write(f"• AC Breaker: {sys_size*1000/grid_v*1.25:.0f} A")
        st.write(f"• RCD: 30mA")
        st.write(f"• Earthing: <5 Ohms")

with tabs[13]:
    df = pd.DataFrame({"Hour": hours, "Gen_kW": gen_24, "Load_kW": load_24, "Export_kW": export_24, "Battery_kWh": soc})
    csv = df.to_csv(index=False)
    st.download_button("📊 Download CSV", csv, file_name=f"SolarX_{country}.csv")
    st.dataframe(df, height=400)

st.markdown("---")
st.caption(f"SolarX Pro v23 | 120+ Countries | Wind Threat + Structure + Material Spec")
                 
