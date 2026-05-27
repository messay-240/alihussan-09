import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Omni-Sovereign Ultra v20.0", layout="wide", page_icon="☀️")

# --- CUSTOM CSS FOR PREMIUM INTERFACE ---
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
        padding: 15px; border-radius: 10px; font-size: 0.95rem; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MASSIVE 110+ COUNTRY DATABASE ---
# [Lat, Currency, Sell_Rate, Buy_Rate, Avg_Wind_m/s]
countries_db = {
    "Afghanistan": [33.9, "AFN", 0.05, 0.09, 4.2], "Albania": [41.1, "ALL", 0.08, 0.14, 3.8], "Algeria": [28.0, "DZD", 0.02, 0.04, 4.5],
    "Andorra": [42.5, "EUR", 0.17, 0.20, 3.2], "Angola": [-11.2, "AOA", 0.01, 0.02, 3.5], "Antigua": [17.1, "XCD", 0.15, 0.35, 6.2],
    "Argentina": [-38.4, "ARS", 0.05, 0.08, 5.5], "Armenia": [40.1, "AMD", 0.06, 0.11, 2.9], "Australia": [-25.2, "AUD", 0.18, 0.26, 6.5],
    "Austria": [47.5, "EUR", 0.28, 0.35, 3.1], "Azerbaijan": [40.1, "AZN", 0.04, 0.05, 4.8], "Bahamas": [25.0, "BSD", 0.25, 0.35, 5.8],
    "Bahrain": [26.0, "BHD", 0.06, 0.08, 5.2], "Bangladesh": [23.6, "BDT", 0.08, 0.10, 3.5], "Barbados": [13.1, "BBD", 0.22, 0.31, 6.0],
    "Belarus": [53.7, "BYN", 0.06, 0.09, 3.8], "Belgium": [50.5, "EUR", 0.24, 0.40, 5.8], "Belize": [17.1, "BZD", 0.14, 0.22, 4.2],
    "Benin": [9.3, "XOF", 0.12, 0.21, 3.1], "Bhutan": [27.5, "BTN", 0.01, 0.02, 2.5], "Bolivia": [-16.2, "BOB", 0.05, 0.09, 3.8],
    "Botswana": [-22.3, "BWP", 0.08, 0.10, 4.1], "Brazil": [-14.2, "BRL", 0.11, 0.16, 4.0], "Bulgaria": [42.7, "BGN", 0.12, 0.15, 4.5],
    "Cambodia": [12.5, "KHR", 0.10, 0.15, 3.2], "Cameroon": [7.3, "XAF", 0.12, 0.18, 3.4], "Canada": [56.1, "CAD", 0.08, 0.12, 5.1],
    "Chile": [-35.6, "CLP", 0.14, 0.22, 4.8], "China": [35.8, "CNY", 0.06, 0.08, 3.9], "Colombia": [4.5, "COP", 0.16, 0.21, 3.5],
    "Congo": [-0.2, "CDF", 0.04, 0.07, 2.8], "Costa Rica": [9.7, "CRC", 0.14, 0.17, 4.1], "Croatia": [45.1, "EUR", 0.12, 0.18, 4.0],
    "Cyprus": [35.1, "EUR", 0.24, 0.34, 4.5], "Czechia": [49.8, "CZK", 0.18, 0.35, 4.1], "Denmark": [56.2, "DKK", 0.20, 0.36, 6.2],
    "Ecuador": [-1.8, "USD", 0.06, 0.10, 3.2], "Egypt": [26.8, "EGP", 0.02, 0.03, 4.8], "Estonia": [58.5, "EUR", 0.14, 0.29, 5.5],
    "Ethiopia": [9.1, "ETB", 0.01, 0.02, 4.1], "Fiji": [-17.7, "FJD", 0.15, 0.22, 5.5], "Finland": [61.9, "EUR", 0.08, 0.17, 4.8],
    "France": [46.2, "EUR", 0.16, 0.28, 4.7], "Georgia": [42.3, "GEL", 0.05, 0.07, 3.8], "Germany": [51.1, "EUR", 0.28, 0.41, 5.0],
    "Ghana": [7.9, "GHS", 0.10, 0.14, 3.8], "Greece": [39.0, "EUR", 0.18, 0.25, 4.5], "Guyana": [4.8, "GYD", 0.12, 0.25, 4.8],
    "Haiti": [18.9, "HTG", 0.15, 0.32, 4.2], "Honduras": [15.2, "HNL", 0.18, 0.23, 4.0], "Hungary": [47.1, "HUF", 0.08, 0.11, 3.9],
    "Iceland": [64.9, "ISK", 0.07, 0.18, 7.5], "India": [20.5, "INR", 0.06, 0.08, 4.1], "Indonesia": [-0.7, "IDR", 0.06, 0.09, 2.8],
    "Iraq": [33.2, "IQD", 0.02, 0.02, 4.2], "Ireland": [53.1, "EUR", 0.24, 0.45, 6.1], "Israel": [31.0, "ILS", 0.10, 0.18, 4.5],
    "Italy": [41.8, "EUR", 0.31, 0.42, 3.5], "Jamaica": [18.1, "JMD", 0.18, 0.29, 5.1], "Japan": [36.2, "JPY", 0.16, 0.23, 4.6],
    "Jordan": [30.5, "JOD", 0.08, 0.09, 4.1], "Kazakhstan": [48.0, "KZT", 0.04, 0.06, 4.8], "Kenya": [-1.2, "KES", 0.14, 0.22, 4.5],
    "Kuwait": [29.3, "KWD", 0.03, 0.04, 4.8], "Latvia": [56.8, "EUR", 0.15, 0.28, 4.5], "Lebanon": [33.8, "LBP", 0.10, 0.25, 3.8],
    "Libya": [26.3, "LYD", 0.01, 0.03, 4.5], "Lithuania": [55.1, "EUR", 0.14, 0.28, 4.5], "Luxembourg": [49.8, "EUR", 0.18, 0.26, 4.1],
    "Malaysia": [4.2, "MYR", 0.05, 0.05, 2.5], "Malta": [35.9, "EUR", 0.12, 0.15, 5.2], "Mexico": [23.6, "MXN", 0.08, 0.11, 4.3],
    "Morocco": [31.7, "MAD", 0.08, 0.12, 4.5], "Nepal": [28.3, "NPR", 0.03, 0.04, 3.2], "Netherlands": [52.1, "EUR", 0.18, 0.28, 6.5],
    "New Zealand": [-40.9, "NZD", 0.15, 0.21, 6.2], "Nigeria": [9.0, "NGN", 0.02, 0.04, 3.5], "Norway": [60.4, "NOK", 0.08, 0.16, 5.5],
    "Oman": [21.5, "OMR", 0.03, 0.03, 4.2], "Pakistan": [30.3, "PKR", 0.06, 0.06, 3.7], "Panama": [8.5, "PAB", 0.12, 0.18, 4.1],
    "Peru": [-9.1, "PEN", 0.12, 0.19, 3.8], "Philippines": [12.8, "PHP", 0.12, 0.21, 5.1], "Poland": [51.9, "PLN", 0.20, 0.23, 4.5],
    "Portugal": [39.3, "EUR", 0.12, 0.24, 4.8], "Qatar": [25.3, "QAR", 0.03, 0.03, 4.8], "Romania": [45.9, "RON", 0.16, 0.21, 4.1],
    "Russia": [61.5, "RUB", 0.06, 0.07, 4.2], "Saudi Arabia": [23.8, "SAR", 0.05, 0.05, 4.2], "Singapore": [1.3, "SGD", 0.21, 0.23, 3.5],
    "Slovakia": [48.6, "EUR", 0.20, 0.21, 3.8], "Slovenia": [46.1, "EUR", 0.15, 0.23, 3.5], "South Africa": [-30.5, "ZAR", 0.08, 0.20, 5.2],
    "South Korea": [35.9, "KRW", 0.09, 0.13, 4.1], "Spain": [40.4, "EUR", 0.12, 0.25, 4.1], "Sri Lanka": [7.8, "LKR", 0.07, 0.12, 4.1],
    "Sudan": [12.8, "SDG", 0.01, 0.02, 4.5], "Sweden": [60.1, "EUR", 0.08, 0.24, 4.8], "Switzerland": [46.8, "CHF", 0.22, 0.37, 3.2],
    "Taiwan": [23.6, "TWD", 0.12, 0.10, 4.2], "Thailand": [15.8, "THB", 0.09, 0.13, 3.1], "Turkey": [38.9, "TRY", 0.09, 0.07, 4.2],
    "UAE": [23.4, "AED", 0.08, 0.08, 4.5], "UK": [55.3, "GBP", 0.18, 0.40, 6.0], "USA": [37.0, "USD", 0.12, 0.19, 4.8],
    "Ukraine": [48.3, "UAH", 0.11, 0.08, 4.2], "Uruguay": [-32.5, "UYU", 0.10, 0.25, 5.1], "Uzbekistan": [41.3, "UZS", 0.05, 0.04, 3.8],
    "Vietnam": [14.0, "VND", 0.06, 0.08, 3.4], "Zambia": [-13.1, "ZMW", 0.03, 0.02, 3.2], "Zimbabwe": [-19.0, "USD", 0.12, 0.28, 3.5]
}

# --- SIDEBAR: ULTIMATE CONTROL PANEL ---
with st.sidebar:
    st.title("🛡️ System Architect")
    country = st.selectbox("🌍 Select Nation", sorted(countries_db.keys()))
    c_lat, c_curr, def_sale, def_buy, avg_wind = countries_db[country]
    
    with st.expander("📐 Orientation & Physics", expanded=True):
        st.write(f"Ref Latitude: {c_lat}°")
        tilt = st.slider("Panel Tilt (°)", 0, 90, int(abs(c_lat)))
        azimuth = st.slider("Azimuth (0°=S, 180°=N)", -180, 180, 0)
    
    with st.expander("🛠️ PV Module Specs"):
        p_type = st.selectbox("Technology", ["Mono-PERC", "Poly", "Thin Film", "Bifacial"])
        p_watt = st.number_input("Panel Rating (W)", value=580)
        p_qty = st.number_input("Panel Count", value=24)
        eff_loss = st.slider("System Losses (%)", 5, 40, 14)

    with st.expander("🏠 Load & Storage"):
        daily_load = st.number_input("Daily Load (kWh)", value=55.0)
        has_batt = st.checkbox("Enable Battery Storage", value=True)
        batt_cap = st.number_input("Battery Size (kWh)", value=20.0) if has_batt else 0

# --- MECHANICAL RISK LOGIC ---
# Risk % = (Wind Speed * sin(Tilt Angle)) * Scale Factor
risk_val = (avg_wind * np.sin(np.radians(tilt))) * 15
risk_percentage = min(100, max(2, risk_val))

# --- CALCULATION CORE ---
sys_size = (p_watt * p_qty) / 1000
angle_factor = np.cos(np.radians(tilt - abs(c_lat)))
total_daily_gen = sys_size * 6.5 * ((100 - eff_loss)/100) * max(0.4, angle_factor)

hours = np.arange(24)
gen_curve = [total_daily_gen * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
load_curve = [(daily_load/24) * (2.2 if (h > 18 or h < 7) else 0.8) for h in hours]

# --- MAIN DASHBOARD ---
st.markdown(f"<div class='main-header'>SolarX Omni-Sovereign Ultra: {country}</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("System Peak", f"{sys_size:.2f} kWp")
m2.metric("Daily Production", f"{sum(gen_curve):.1f} kWh")
m3.metric("Avg Wind Speed", f"{avg_wind} m/s")
m4.metric("Damage Risk", f"{risk_percentage:.1f}%")

st.divider()

# --- TABS ---
tab_analytics, tab_finance, tab_weather, tab_ict = st.tabs([
    "📊 Load Usage Graphs", "💰 Multi-Temporal Income", "🌪️ Weather Risk Engine", "⚖️ Ethical Framework"
])

with tab_analytics:
    st.write("### Multi-Temporal Power Analysis")
    d, w, m = st.tabs(["Daily View", "Weekly View", "Monthly View"])
    with d:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=gen_curve, name="Solar Gen (kW)", fill='tozeroy', line=dict(color='#fbbf24', width=4)))
        fig.add_trace(go.Scatter(x=hours, y=load_curve, name="Load Usage (kW)", line=dict(color='#3b82f6', width=2, dash='dot')))
        fig.update_layout(template="plotly_white", height=450)
        st.plotly_chart(fig, use_container_width=True)
    with w:
        st.bar_chart(pd.DataFrame([daily_load * np.random.uniform(0.9, 1.1) for _ in range(7)], index=["M","T","W","T","F","S","S"]), color="#3b82f6")
    with m:
        st.line_chart(pd.DataFrame([daily_load * 30 * np.random.uniform(0.9, 1.1) for _ in range(12)], index=range(1,13)), color="#1e3a8a")

with tab_finance:
    st.write("### Multi-Temporal Income Projection")
    daily_val = sum(gen_curve) * 0.15 # Baseline estimated value
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Daily Income", f"${daily_val:,.2f}")
    f2.metric("Weekly Income", f"${daily_val*7:,.2f}")
    f3.metric("Monthly Income", f"${daily_val*30:,.2f}")
    f4.metric("Annual Income", f"${daily_val*365:,.2f}")

with tab_weather:
    st.write("### 🌪️ Wind & Structural Risk Engine")
    st.markdown(f"""
    <div class='risk-banner'>
    <b>Risk Rating: {'CRITICAL' if risk_percentage > 60 else 'HIGH' if risk_percentage > 40 else 'SAFE'}</b><br>
    The mechanical stress for <b>{country}</b> at a <b>{tilt}° tilt</b> is calculated at <b>{risk_percentage:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"Mechanical Note: At {tilt}°, the solar array surface acts as a sail. Ensure mounting racks are rated for {avg_wind * 1.5:.1f} m/s gusts.")

with tab_ict:
    st.write("### ⚖️ Project Ethical Framework")
    st.markdown("""
    <div class='ethics-box'>
    <b>1. Technical Integrity:</b> The 110+ country database provides localized accuracy for global users.<br>
    <b>2. Safety Responsibility:</b> The risk engine alerts users to mechanical failure threats based on orientation physics.<br>
    <b>3. Professional Ethics:</b> Developed as a non-commercial ICT research tool for sustainable engineering development.
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.write("**Project Team:** Ali Hussaan, Abdual Rehman Abbasi, Ali Sultan, Abdullah")

# --- FOOTER ---
st.markdown("---")
st.caption("SolarX Omni-Sovereign Ultra v20.0 | Mechanical Engineering Dept | Team Ali Hussaan")
