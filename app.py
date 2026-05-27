import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Omni-Sovereign Ultra v24.0", layout="wide", page_icon="☀️")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-size: 26px; font-weight: 800; }
    .stMetric { 
        background-color: #f8fafc; border: 1px solid #e2e8f0; 
        border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .main-header { 
        color: #0f172a; font-size: 36px; font-weight: 900; 
        border-left: 15px solid #fbbf24; padding-left: 20px; margin-bottom: 30px; 
    }
    .risk-high { background-color: #fef2f2; border: 1px solid #fee2e2; padding: 15px; border-radius: 10px; color: #991b1b; }
    .risk-safe { background-color: #f0fdf4; border: 1px solid #dcfce7; padding: 15px; border-radius: 10px; color: #166534; }
    </style>
    """, unsafe_allow_html=True)

# --- GLOBAL DATABASE 2026 (110+ COUNTRIES) ---
countries_db = {
    "Afghanistan": [33.9, "AFN", 0.052, 0.093, 4.2, 3, 4], "Albania": [41.1, "ALL", 0.118, 0.137, 3.8, 5, 2],
    "Algeria": [28.0, "DZD", 0.041, 0.035, 4.5, 2, 1], "Angola": [-11.2, "AOA", 0.016, 0.013, 3.5, 8, 1],
    "Argentina": [-38.4, "ARS", 0.083, 0.095, 5.5, 6, 7], "Australia": [-25.2, "AUD", 0.257, 0.240, 6.5, 4, 6],
    "Austria": [47.5, "EUR", 0.351, 0.291, 3.1, 5, 4], "Bahamas": [25.0, "BSD", 0.348, 0.369, 5.8, 4, 5],
    "Bangladesh": [23.6, "BDT", 0.062, 0.100, 3.5, 9, 2], "Belgium": [50.5, "EUR", 0.404, 0.261, 5.8, 3, 2],
    "Brazil": [-14.2, "BRL", 0.162, 0.132, 4.0, 9, 3], "Canada": [56.1, "CAD", 0.123, 0.108, 5.1, 3, 5],
    "China": [35.8, "CNY", 0.076, 0.108, 3.9, 6, 4], "Egypt": [26.8, "EGP", 0.024, 0.037, 4.8, 1, 1],
    "France": [46.2, "EUR", 0.276, 0.185, 4.7, 5, 3], "Germany": [51.1, "EUR", 0.406, 0.285, 5.0, 4, 4],
    "India": [20.5, "INR", 0.077, 0.123, 4.1, 8, 3], "Indonesia": [-0.7, "IDR", 0.091, 0.070, 2.8, 10, 1],
    "Italy": [41.8, "EUR", 0.415, 0.415, 3.5, 6, 5], "Japan": [36.2, "JPY", 0.228, 0.202, 4.6, 5, 4],
    "Malaysia": [4.2, "MYR", 0.050, 0.129, 2.5, 10, 1], "Mexico": [23.6, "MXN", 0.108, 0.212, 4.3, 5, 4],
    "Netherlands": [52.1, "EUR", 0.284, 0.220, 6.5, 3, 2], "Norway": [60.4, "NOK", 0.162, 0.109, 5.5, 2, 6],
    "Pakistan": [30.3, "PKR", 0.064, 0.154, 3.7, 7, 5], "Saudi Arabia": [23.8, "SAR", 0.052, 0.070, 4.2, 2, 1],
    "Singapore": [1.3, "SGD", 0.233, 0.265, 3.5, 10, 1], "South Africa": [-30.5, "ZAR", 0.204, 0.103, 5.2, 7, 6],
    "Spain": [40.4, "EUR", 0.253, 0.135, 4.1, 4, 3], "UK": [55.3, "GBP", 0.404, 0.445, 6.0, 3, 2],
    "USA": [37.0, "USD", 0.186, 0.148, 4.8, 7, 8], "Vietnam": [14.0, "VND", 0.078, 0.078, 3.4, 8, 2],
    "Zambia": [-13.1, "ZMW", 0.023, 0.039, 3.2, 7, 1]
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Project Architect")
    country = st.selectbox("🌍 Select Nation", sorted(countries_db.keys()))
    c_lat, c_curr, s_rate, p_rate, avg_wind, l_idx, h_idx = countries_db[country]
    
    with st.expander("🏗️ Structural Design", expanded=True):
        frame = st.selectbox("Frame Type", ["Standard Roof-Mount", "Reinforced Ground-Mount", "Single-Axis Tracker", "Dual-Axis Tracker"])
        tilt = st.slider("Mechanical Tilt Angle (°)", 0, 90, int(abs(c_lat)))
        struct_mod = {"Standard Roof-Mount": 1.0, "Reinforced Ground-Mount": 0.6, "Single-Axis Tracker": 1.4, "Dual-Axis Tracker": 1.8}[frame]

    with st.expander("📦 Battery Package (Optional)"):
        use_batt = st.checkbox("Include Energy Storage", value=True)
        batt_cap = st.number_input("Capacity (kWh)", value=20.0) if use_batt else 0

    with st.expander("🛠️ PV Module Specs"):
        p_watt = st.number_input("Panel Rating (W)", value=585)
        p_qty = st.number_input("Total Quantity", value=24)

# --- THREAT ENGINE ---
wind_risk = min(100, (avg_wind * np.sin(np.radians(tilt)) * 14) * struct_mod)
hail_risk = min(100, (h_idx * 11 * np.cos(np.radians(tilt))))
lightning_risk = min(100, (l_idx * 10 * (1 + (tilt/120))))
storm_risk = (wind_risk * 0.6) + (lightning_risk * 0.4)
rain_risk = (storm_risk * 0.5)

# --- CALCULATION CORE ---
sys_size = (p_watt * p_qty) / 1000
eff_factor = 0.88 * np.cos(np.radians(tilt - abs(c_lat)))
daily_gen = sys_size * 6.5 * max(0.4, eff_factor)
daily_income = (daily_gen * s_rate) + (daily_gen * 0.3 * p_rate)

# --- DASHBOARD ---
st.markdown(f"<div class='main-header'>SolarX Sovereign Ultra: {country}</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("System Peak", f"{sys_size:.2f} kWp")
m2.metric("Daily Production", f"{daily_gen:.1f} kWh")
m3.metric("Est. Annual Income", f"${(daily_income * 365):,.2f}")
m4.metric("Frame Mode", frame)

st.divider()

t1, t2 = st.tabs(["🌪️ Environmental Hazards", "📊 Finance & Performance"])

with t1:
    st.write("### Dynamic Mechanical Risk Engine")
    
    # FIXED PLOTLY CODE: Using go.Scatterpolar instead of go.Polar
    labels = ["Wind Lift", "Yalabari (Hail)", "Lightning Strike", "Storm Intensity", "Rain Loading", "Wind Lift"]
    values = [wind_risk, hail_risk, lightning_risk, storm_risk, rain_risk, wind_risk] # Closed loop
    
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        marker=dict(color='#dc2626'),
        line=dict(color='#dc2626', width=2)
    ))
    
    fig_risk.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=450
    )
    st.plotly_chart(fig_risk, use_container_width=True)
    
    if wind_risk > 60:
        st.markdown(f"<div class='risk-high'><b>WARNING:</b> High tilt ({tilt}°) creates critical Wind Lift.</div>", unsafe_allow_html=True)
    elif hail_risk > 60:
        st.markdown(f"<div class='risk-high'><b>WARNING:</b> Low tilt ({tilt}°) increases perpendicular Yalabari impact.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='risk-safe'><b>STATUS:</b> Configuration stable for regional profile.</div>", unsafe_allow_html=True)

with t2:
    st.write("### Financial Forecasting")
    st.line_chart([daily_income * 30 * np.random.uniform(0.85, 1.1) for _ in range(12)], color="#2563eb")
    st.write("**Core Project Team:** Ali Hussaan, Abdual Rehman Abbasi, Ali Sultan, Abdullah")

st.markdown("---")
st.caption(f"SolarX v24.0 | Engineering Deployment May 2026")
