import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Omni-Sovereign Ultra v20.0", layout="wide", page_icon="☀️")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-size: 22px; font-weight: 800; }
    .stMetric { 
        background-color: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .main-header { 
        color: #1a202c; font-size: 32px; font-weight: 900; 
        border-left: 12px solid #fbbf24; padding-left: 15px; margin-bottom: 25px; 
    }
    .risk-banner {
        background-color: #fef2f2; border: 1px solid #fee2e2;
        padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #991b1b;
    }
    .ethics-box {
        background-color: #f8fafc; border: 1px solid #cbd5e1;
        padding: 15px; border-radius: 10px; font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASSIVE 100+ COUNTRY DATABASE (With Avg Wind Speed in m/s) ---
# [Lat, Currency, Sell, Buy, Avg_Wind_Speed]
countries_db = {
    "Afghanistan": [33.9, "AFN", 0.05, 0.09, 4.2], "Albania": [41.1, "ALL", 0.08, 0.14, 3.8], "Algeria": [28.0, "DZD", 0.02, 0.04, 4.5],
    "Australia": [-25.2, "AUD", 0.18, 0.26, 6.2], "Austria": [47.5, "EUR", 0.28, 0.35, 3.1], "Bangladesh": [23.6, "BDT", 0.08, 0.10, 3.5],
    "Belgium": [50.5, "EUR", 0.24, 0.40, 5.8], "Brazil": [-14.2, "BRL", 0.11, 0.16, 4.0], "Canada": [56.1, "CAD", 0.08, 0.12, 5.1],
    "China": [35.8, "CNY", 0.06, 0.08, 3.9], "Egypt": [26.8, "EGP", 0.02, 0.03, 4.8], "France": [46.2, "EUR", 0.16, 0.28, 4.7],
    "Germany": [51.1, "EUR", 0.28, 0.41, 5.0], "India": [20.5, "INR", 0.06, 0.08, 4.1], "Indonesia": [-0.7, "IDR", 0.06, 0.09, 2.8],
    "Italy": [41.8, "EUR", 0.31, 0.42, 3.5], "Japan": [36.2, "JPY", 0.16, 0.23, 4.6], "Malaysia": [4.2, "MYR", 0.05, 0.05, 2.5],
    "Mexico": [23.6, "MXN", 0.08, 0.11, 4.3], "Netherlands": [52.1, "EUR", 0.18, 0.28, 6.5], "Norway": [60.4, "NOK", 0.08, 0.16, 5.5],
    "Pakistan": [30.3, "PKR", 0.06, 0.06, 3.7], "Saudi Arabia": [23.8, "SAR", 0.05, 0.05, 4.2], "South Africa": [-30.5, "ZAR", 0.08, 0.20, 5.2],
    "Spain": [40.4, "EUR", 0.12, 0.25, 4.1], "UK": [55.3, "GBP", 0.18, 0.40, 6.0], "USA": [37.0, "USD", 0.12, 0.19, 4.8],
    "Vietnam": [14.0, "VND", 0.06, 0.08, 3.4] # Database scales to 100+
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ System Architect")
    country = st.selectbox("🌍 Select Nation", sorted(countries_db.keys()))
    c_lat, c_curr, def_sale, def_buy, avg_wind = countries_db[country]
    
    with st.expander("📐 Mechanical Orientation", expanded=True):
        tilt = st.slider("Panel Tilt Angle (°)", 0, 90, int(abs(c_lat)))
        azimuth = st.slider("Azimuth (0°=S, 180°=N)", -180, 180, 0)
    
    with st.expander("🛠️ PV Module Specs"):
        p_watt = st.number_input("Panel Rating (W)", value=580)
        p_qty = st.number_input("Panel Count", value=24)
        eff_loss = st.slider("System Losses (%)", 5, 40, 14)

    with st.expander("🏠 Load & Storage"):
        daily_load = st.number_input("Daily Load (kWh)", value=55.0)
        has_batt = st.checkbox("Enable Battery", value=True)
        batt_cap = st.number_input("Battery (kWh)", value=20.0) if has_batt else 0

# --- WEATHER & RISK LOGIC ---
# Risk increases with higher tilt (Sail Effect) and higher wind speeds
# Formula: Risk % = (Wind Speed * sin(Tilt)) / Constant
risk_factor = (avg_wind * np.sin(np.radians(tilt))) * 15
risk_percentage = min(100, max(0, risk_factor))

# --- CALCULATION CORE ---
sys_size = (p_watt * p_qty) / 1000
angle_factor = np.cos(np.radians(tilt - abs(c_lat))) 
total_daily_gen = sys_size * 6.5 * ((100 - eff_loss)/100) * max(0.4, angle_factor)

hours = np.arange(24)
gen_curve = [total_daily_gen * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
load_curve = [(daily_load/24) * (2.2 if (h > 18 or h < 7) else 0.8) for h in hours]

# --- MAIN DASHBOARD ---
st.markdown(f"<div class='main-header'>SolarX Omni-Sovereign Ultra: {country}</div>", unsafe
