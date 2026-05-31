import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Solar Power Estemaiter", layout="wide", page_icon="⚡")

# --- THEME ---
st.markdown("""
    <style>
.stApp { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; }
[data-testid="stMetricValue"] { color: #fbbf24!important; font-size: 32px; font-weight: 900; }
.stMetric { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 2px solid rgba(255,255,255,0.2); border-radius: 20px; padding: 24px; }
.main-header { color: white; font-size: 48px; font-weight: 900; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); margin-bottom: 40px; }
.feature-box { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border: 2px solid rgba(255,255,255,0.3); padding: 28px; border-radius: 20px; margin-bottom: 26px; }
.info-label { background: #fbbf24; color: #0c4a6e; padding: 8px 16px; border-radius: 12px; font-size: 0.95rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 120+ COUNTRIES DATABASE [Lat, Currency, Export, Import, ESG, Labor, Sourcing, GHI, Elec%, Voltage, Frequency] ---
db = {
    "Afghanistan": [33.9, "AFN", 5, 12, "B", "High", "Import", 5.2, 98, 220, 50], "Albania": [41.1, "ALL", 10, 18, "B+", "Medium", "EU Import", 4.1, 100, 230, 50],
    "Algeria": [28.0, "DZD", 4, 12, "B", "Medium", "Local", 6.0, 99, 230, 50], "Andorra": [42.5, "EUR", 0.12, 0.28, "A+", "Very Low", "EU Certified", 4.3, 100, 230, 50],
    "Angola": [-11.2, "AOA", 15, 30, "C", "High", "Import", 5.5, 42, 220, 50], "Argentina": [-38.4, "ARS", 25, 65, "B+", "Medium", "Local", 5.1, 100, 220, 50],
    "Armenia": [40.2, "AMD", 12, 25, "B+", "Medium", "Import", 4.2, 100, 230, 50], "Australia": [-25.2, "AUD", 0.10, 0.35, "A+", "Very Low", "AU Certified", 5.8, 100, 230, 50],
    "Austria": [47.5, "EUR", 0.15, 0.45, "A+", "Very Low", "EU Certified", 3.4, 100, 230, 50], "Azerbaijan": [40.1, "AZN", 0.05, 0.12, "B", "Medium", "Import", 4.8, 100, 220, 50],
    "Bahrain": [26.0, "BHD", 0.02, 0.06, "A", "Low", "GCC", 5.9, 100, 230, 50], "Bangladesh": [23.6, "BDT", 7.5, 14.0, "B", "Medium", "Local Assembly", 4.6, 99, 220, 50],
    "Belgium": [50.5, "EUR", 0.12, 0.52, "A+", "Very Low", "EU Certified", 2.9, 100, 230, 50], "Bhutan": [27.5, "BTN", 3, 8, "A", "Low", "Hydro+Solar", 4.5, 99, 230, 50],
    "Bolivia": [-16.2, "BOB", 0.4, 0.9, "B", "Medium", "Import", 5.8, 94, 220, 50], "Bosnia": [44.2, "BAM", 0.08, 0.16, "B+", "Medium", "EU Import", 3.6, 100, 230, 50],
    "Botswana": [-22.3, "BWP", 1.2, 2.4, "B+", "Medium", "Local", 6.1, 72, 230, 50], "Brazil": [-14.2, "BRL", 0.55, 1.15, "A-", "Low", "Local Mfg", 5.5, 99, 220, 60],
    "Bulgaria": [42.7, "BGN", 0.09, 0.18, "A-", "Low", "EU Certified", 3.8, 100, 230, 50], "Burkina Faso": [12.4, "XOF", 85, 170, "C", "High", "Import", 5.8, 19, 220, 50],
    "Burundi": [-3.4, "BIF", 180, 350, "C", "High", "Import", 5.2, 11, 220, 50], "Cambodia": [12.6, "KHR", 600, 1200, "B", "Medium", "Import", 5.0, 89, 230, 50],
    "Cameroon": [6.3, "XAF", 75, 150, "C", "High", "Import", 5.0, 64, 220, 50], "Canada": [56.1, "CAD", 0.08, 0.24, "A+", "Very Low", "US/CA Certified", 3.7, 100, 120, 60],
    "Chile": [-35.6, "CLP", 65, 155, "A", "Low", "Local", 6.2, 100, 220, 50], "China": [35.8, "CNY", 0.42, 0.72, "C+", "High", "Global Supply", 4.3, 100, 220, 50],
    "Colombia": [4.5, "COP", 380, 750, "B+", "Medium", "Import", 4.5, 99, 110, 60], "Croatia": [45.1, "EUR", 0.10, 0.20, "A", "Low", "EU Certified", 3.7, 100, 230, 50],
    "Cuba": [21.5, "CUP", 2.5, 5.0, "B", "Medium", "Import", 5.4, 100, 120, 60], "Cyprus": [35.1, "EUR", 0.15, 0.30, "A", "Low", "EU Certified", 5.6, 100, 230, 50],
    "Czech": [49.8, "CZK", 2.2, 4.8, "A", "Low", "EU Certified", 3.1, 100, 230, 50], "Denmark": [56.2, "DKK", 0.65, 2.80, "A+", "Very Low", "EU Certified", 2.7, 100, 230, 50],
    "Djibouti": [11.6, "DJF", 30, 60, "C", "High", "Import", 6.2, 61, 220, 50], "Dominican": [18.7, "DOP", 8.5, 17, "B", "Medium", "Import", 5.5, 99, 120, 60],
    "Ecuador": [-1.8, "USD", 0.10, 0.20, "B+", "Medium", "Import", 4.8, 97, 120, 60], "Egypt": [26.8, "EGP", 1.2, 2.6, "B", "Medium", "Local Assembly", 6.1, 100, 220, 50],
    "El Salvador": [13.8, "USD", 0.14, 0.28, "B+", "Medium", "Import", 5.4, 99, 120, 60], "Estonia": [58.6, "EUR", 0.12, 0.28, "A+", "Very Low", "EU Certified", 2.8, 100, 230, 50],
    "Ethiopia": [9.1, "ETB", 0.5, 1.2, "B", "Medium", "China Import", 5.9, 51, 220, 50], "Fiji": [-18.1, "FJD", 0.25, 0.50, "A-", "Low", "Import", 5.3, 99, 240, 50],
    "Finland": [61.9, "EUR", 0.08, 0.38, "A+", "Very Low", "EU Certified", 2.5, 100, 230, 50], "France": [46.2, "EUR", 0.15, 0.34, "A+", "Very Low", "EU Certified", 3.5, 100, 230, 50],
    "Gabon": [-0.8, "XAF", 95, 190, "B", "Medium", "Import", 4.9, 87, 220, 50], "Georgia": [42.3, "GEL", 0.15, 0.30, "B+", "Medium", "Import", 4.2, 100, 220, 50],
    "Germany": [51.1, "EUR", 0.12, 0.48, "A+", "Very Low", "EU Certified", 3.0, 100, 230, 50], "Ghana": [7.9, "GHS", 0.50, 1.0, "B", "Medium", "Import", 5.4, 86, 230, 50],
    "Greece": [39.0, "EUR", 0.18, 0.38, "A", "Low", "EU Import", 4.5, 100, 230, 50], "Guatemala": [15.8, "GTQ", 1.2, 2.4, "B", "Medium", "Import", 5.5, 93, 120, 60],
    "Honduras": [14.1, "HNL", 4.5, 9.0, "B", "Medium", "Import", 5.6, 88, 120, 60], "Hungary": [47.2, "HUF", 35, 75, "A-", "Low", "EU Certified", 3.4, 100, 230, 50],
    "Iceland": [64.9, "ISK", 8, 18, "A+", "Very Low", "Geothermal", 2.2, 100, 230, 50], "India": [20.5, "INR", 6.2, 12.5, "A-", "Low", "Local Mfg", 5.4, 99, 230, 50],
    "Indonesia": [-0.7, "IDR", 1500, 3400, "B", "Medium", "Local", 4.8, 99, 220, 50], "Iran": [32.4, "IRR", 800, 2000, "B", "Medium", "Local", 5.6, 100, 220, 50],
    "Iraq": [33.2, "IQD", 70, 160, "C", "High", "Import", 5.8, 99, 220, 50], "Ireland": [53.1, "EUR", 0.22, 0.55, "A+", "Very Low", "EU Certified", 2.7, 100, 230, 50],
    "Israel": [31.0, "ILS", 0.40, 0.60, "A", "Low", "Local", 5.7, 100, 230, 50], "Italy": [41.8, "EUR", 0.20, 0.50, "A", "Low", "EU Certified", 4.2, 100, 230, 50],
    "Jamaica": [18.1, "JMD", 25, 50, "B+", "Medium", "Import", 5.6, 99, 110, 50], "Japan": [36.2, "JPY", 21, 42, "A+", "Very Low", "JP Certified", 3.8, 100, 100, 50],
    "Jordan": [30.5, "JOD", 0.08, 0.18, "B+", "Medium", "Local", 5.8, 100, 230, 50], "Kazakhstan": [48.0, "KZT", 8, 18, "B", "Medium", "Local", 4.6, 100, 220, 50],
    "Kenya": [-1.2, "KES", 12, 28, "B", "Medium", "Import", 5.7, 76, 240, 50], "Kuwait": [29.3, "KWD", 0.02, 0.08, "A", "Low", "GCC", 5.9, 100, 240, 50],
    "Kyrgyzstan": [41.2, "KGS", 2.5, 5.0, "B", "Medium", "Import", 4.5, 100, 220, 50], "Latvia": [56.9, "EUR", 0.11, 0.24, "A", "Low", "EU Certified", 2.8, 100, 230, 50],
    "Lebanon": [33.9, "LBP", 120, 250, "C", "High", "Import", 5.5, 98, 220, 50], "Libya": [26.3, "LYD", 0.15, 0.30, "C", "High", "Import", 6.0, 99, 230, 50],
    "Lithuania": [55.2, "EUR", 0.10, 0.22, "A", "Low", "EU Certified", 2.9, 100, 230, 50], "Luxembourg": [49.8, "EUR", 0.18, 0.36, "A+", "Very Low", "EU Certified", 3.0, 100, 230, 50],
    "Madagascar": [-18.8, "MGA", 450, 900, "C", "High", "Import", 5.6, 36, 220, 50], "Malawi": [-13.9, "MWK", 85, 170, "C", "High", "Import", 5.7, 12, 230, 50],
    "Malaysia": [4.2, "MYR", 0.38, 0.68, "A-", "Low", "Local Mfg", 4.7, 100, 240, 50], "Mali": [17.6, "XOF", 90, 180, "C", "High", "Import", 5.9, 38, 220, 50],
    "Malta": [35.9, "EUR", 0.16, 0.32, "A", "Low", "EU Certified", 5.4, 100, 230, 50], "Mexico": [23.6, "MXN", 2.2, 4.8, "B+", "Medium", "US Import", 5.6, 99, 127, 60],
    "Mongolia": [46.9, "MNT", 180, 360, "B", "Medium", "Import", 4.3, 89, 230, 50], "Morocco": [31.7, "MAD", 1.1, 2.2, "B+", "Medium", "Local", 5.9, 99, 220, 50],
    "Mozambique": [-18.7, "MZN", 4.5, 9.0, "C", "High", "Import", 5.8, 34, 220, 50], "Myanmar": [19.7, "MMK", 80, 160, "C", "High", "Import", 5.0, 50, 230, 50],
    "Namibia": [-22.6, "NAD", 1.8, 3.6, "B+", "Medium", "Import", 6.2, 56, 220, 50], "Nepal": [28.3, "NPR", 8.2, 18.5, "B", "Medium", "India Import", 4.7, 95, 230, 50],
    "Netherlands": [52.1, "EUR", 0.16, 0.55, "A+", "Very Low", "EU Certified", 2.8, 100, 230, 50], "New Zealand": [-40.9, "NZD", 0.11, 0.40, "A+", "Very Low", "AU/NZ", 4.4, 100, 230, 50],
    "Nicaragua": [12.9, "NIO", 4.2, 8.4, "B", "Medium", "Import", 5.5, 97, 120, 60], "Niger": [17.6, "XOF", 95, 190, "C", "High", "Import", 6.0, 19, 220, 50],
    "Nigeria": [9.0, "NGN", 70, 160, "C", "High", "Import", 5.5, 62, 230, 50], "North Korea": [40.3, "KPW", 5, 10, "C", "High", "Import", 4.2, 26, 220, 60],
    "Norway": [60.4, "NOK", 0.9, 2.8, "A+", "Very Low", "EU Certified", 2.3, 100, 230, 50], "Oman": [21.5, "OMR", 0.03, 0.12, "A", "Low", "GCC", 6.0, 100, 240, 50],
    "Pakistan": [30.3, "PKR", 42.0, 82.0, "B+", "Medium", "China Import", 5.3, 97, 220, 50], "Palestine": [31.9, "ILS", 0.45, 0.90, "C", "High", "Import", 5.7, 100, 230, 50],
    "Panama": [8.4, "USD", 0.15, 0.30, "A-", "Low", "Import", 4.9, 94, 120, 60], "Paraguay": [-23.4, "PYG", 350, 700, "B+", "Medium", "Import", 5.1, 99, 220, 50],
    "Peru": [-9.1, "PEN", 0.32, 0.68, "B+", "Medium", "Import", 5.4, 99, 220, 60], "Philippines": [12.8, "PHP", 6.2, 14.0, "B", "Medium", "China Import", 5.1, 94, 220, 60],
    "Poland": [51.9, "PLN", 0.45, 0.95, "A", "Low", "EU Certified", 3.1, 100, 230, 50], "Portugal": [39.3, "EUR", 0.14, 0.32, "A", "Low", "EU Certified", 4.3, 100, 230, 50],
    "Qatar": [25.3, "QAR", 0.15, 0.38, "A", "Low", "GCC", 5.9, 100, 240, 50], "Romania": [45.9, "RON", 0.45, 0.95, "A-", "Low", "EU Certified", 3.6, 100, 230, 50],
    "Russia": [61.5, "RUB", 3.5, 6.2, "B", "Medium", "Local", 3.2, 100, 220, 50], "Rwanda": [-1.9, "RWF", 150, 300, "B+", "Medium", "Import", 5.3, 35, 230, 50],
    "Saudi Arabia": [23.8, "SAR", 0.15, 0.32, "A", "Low", "GCC Local", 6.1, 100, 220, 60], "Senegal": [14.7, "XOF", 85, 170, "B", "Medium", "Import", 5.8, 70, 230, 50],
    "Serbia": [44.0, "RSD", 6, 12, "B+", "Medium", "Import", 3.7, 100, 230, 50], "Singapore": [1.3, "SGD", 0.28, 0.45, "A+", "Very Low", "Import", 4.6, 100, 230, 50],
    "Slovakia": [48.7, "EUR", 0.12, 0.26, "A", "Low", "EU Certified", 3.2, 100, 230, 50], "Slovenia": [46.1, "EUR", 0.13, 0.27, "A+", "Very Low", "EU Certified", 3.5, 100, 230, 50],
    "Somalia": [5.1, "SOS", 200, 400, "C", "High", "Import", 6.0, 35, 220, 50], "South Africa": [-30.5, "ZAR", 1.9, 3.8, "B+", "Medium", "Local", 5.7, 85, 230, 50],
    "South Korea": [37.5, "KRW", 95, 180, "A+", "Very Low", "KR Certified", 3.8, 100, 220, 60], "South Sudan": [6.5, "SSP", 25, 50, "C", "High", "Import", 5.9, 7, 230, 50],
    "Spain": [40.4, "EUR", 0.22, 0.45, "A", "Low", "EU Certified", 4.6, 100, 230, 50], "Sri Lanka": [7.8, "LKR", 25, 58, "B", "Medium", "India Import", 5.2, 99, 230, 50],
    "Sudan": [15.5, "SDG", 2.5, 5.0, "C", "High", "Import", 6.1, 52, 230, 50], "Sweden": [60.1, "SEK", 0.85, 2.40, "A+", "Very Low", "EU Certified", 2.6, 100, 230, 50],
    "Switzerland": [46.8, "CHF", 0.20, 0.45, "A+", "Very Low", "EU Certified", 3.4, 100, 230, 50], "Syria": [34.8, "SYP", 35, 70, "C", "High", "Import", 5.8, 89, 220, 50],
    "Tajikistan": [38.5, "TJS", 0.25, 0.50, "B", "Medium", "Import", 4.6, 100, 220, 50], "Tanzania": [-6.1, "TZS", 180, 420, "B", "Medium", "Import", 5.6, 38, 230, 50],
    "Thailand": [15.8, "THB", 2.8, 6.0, "A-", "Low", "Local Mfg", 5.0, 100, 220, 50], "Tunisia": [34.0, "TND", 0.18, 0.38, "B+", "Medium", "Local", 5.8, 100, 230, 50],
    "Turkey": [38.9, "TRY", 3.5, 6.5, "B+", "Medium", "Local", 4.9, 100, 230, 50], "UAE": [23.4, "AED", 0.22, 0.48, "A", "Low", "GCC Local", 5.9, 100, 220, 50],
    "Uganda": [1.4, "UGX", 580, 1160, "B", "Medium", "Import", 5.5, 42, 240, 50], "Ukraine": [48.3, "UAH", 1.8, 4.2, "B", "Medium", "EU Import", 3.4, 100, 220, 50],
    "UK": [55.3, "GBP", 0.22, 0.58, "A+", "Very Low", "UK/EU Certified", 2.8, 100, 230, 50], "Uruguay": [-32.5, "UYU", 3.8, 7.6, "A", "Low", "Import", 4.8, 100, 230, 50],
    "USA": [37.0, "USD", 0.14, 0.30, "A+", "Very Low", "US Certified", 4.8, 100, 120, 60], "Uzbekistan": [41.3, "UZS", 250, 500, "B", "Medium", "Local", 5.2, 100, 220, 50],
    "Venezuela": [6.4, "VES", 0.02, 0.04, "C", "High", "Import", 5.2, 99, 120, 60], "Vietnam": [14.0, "VND", 2200, 3800, "B+", "Medium", "Local Mfg", 4.8, 100, 220, 50],
    "Yemen": [15.4, "YER", 40, 80, "C", "High", "Import", 5.9, 47, 220, 50], "Zambia": [-13.1, "ZMW", 1.2, 2.4, "B", "Medium", "Import", 5.7, 45, 230, 50],
    "Zimbabwe": [-19.0, "USD", 0.10, 0.25, "C", "High", "Import", 5.8, 47, 230, 50]
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ Solar Power Estemaiter ")
    country = st.selectbox("🌍 Country - 120+ Options", sorted(db.keys()))
    c_lat, c_curr, c_sale, c_buy, esg_rating, labor_risk, sourcing, avg_ghi, elec_access, grid_v, grid_f = db[country]

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

# --- HEADER ---
st.markdown(f"<div class='main-header'>⚡ Solar Power Estemaitor: {country}</div>", unsafe_allow_html=True)

# --- KPI 9 METRICS ---
k1, k2, k3, k4, k5, k6, k7, k8, k9 = st.columns(9)
k1.metric("System kWp", f"{sys_size:.2f}")
k2.metric("Panel", panel_type.split()[0])
k3.metric("Inverter", inverter_type.split()[0])
k4.metric("Daily Gen", f"{sum(gen_24):.1f} kWh")
k5.metric("Battery", battery_type.split()[0] if has_batt else "None")
k6.metric("VOC String", f"{voc_string:.0f} V")
k7.metric("VD Loss", f"{vd_percent:.2f}%")
k8.metric("Self Use", f"{(1-sum(import_24)/h_load)*100:.1f}%")
k9.metric("ESG", esg_rating)

st.divider()

# --- 13 TABS ---
tabs = st.tabs([
    "📊 Energy", "🔧 Technical", "🔌 Inverter", "🔋 Battery", "⚡ Electrical",
    "💰 Financial", "🌿 Eco", "🛡️ Ethics", "📈 Net Metering", "🤖 AI",
    "🌤️ Weather", "⚙️ Protection", "📄 Export"
])

with tabs[0]:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=gen_24, name="Solar Gen", fill='tozeroy', line=dict(color='#fbbf24', width=4)))
    fig.add_trace(go.Scatter(x=hours, y=load_24, name="Load", line=dict(color='white', width=3)))
    if has_batt: fig.add_trace(go.Scatter(x=hours, y=soc, name="Battery", line=dict(color='#22c55e', width=3)))
    fig.update_layout(height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
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
    if pr > 80:
        st.success("✅ Excellent design")

with tabs[10]:
    cloud = st.slider("Cloud Cover %", 0, 100, 20)
    wind = st.slider("Wind km/h", 0, 100, 15)
    weather_factor = 1 - cloud*0.008 + wind*0.0003
    st.metric("Weather Yield", f"{daily_yield*weather_factor:.1f} kWh", f"{(weather_factor-1)*100:.1f}%")

with tabs[11]:
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

with tabs[12]:
    df = pd.DataFrame({"Hour": hours, "Gen_kW": gen_24, "Load_kW": load_24, "Export_kW": export_24, "Battery_kWh": soc})
    csv = df.to_csv(index=False)
    st.download_button("📊 Download CSV", csv, file_name=f"SolarX_{country}.csv")
    st.dataframe(df, height=400)

st.markdown("---")
st.caption(f"Solar Power Estemaiter | 120+ Countries | Complete Solar Solution")
