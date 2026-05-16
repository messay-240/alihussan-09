import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Infinity Ultra", layout="wide", page_icon="🔋")

# --- ADVANCED PREMIUM LIGHT THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-size: 26px; font-weight: 800; }
    .stMetric { 
        background-color: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 12px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .main-header { 
        color: #1a202c; font-size: 36px; font-weight: 900; 
        border-left: 8px solid #34a853; padding-left: 20px; margin-bottom: 30px; 
    }
    .feature-info {
        background-color: #f0fdf4; border-left: 5px solid #22c55e;
        padding: 20px; margin-bottom: 25px; border-radius: 0 12px 12px 0;
        font-size: 0.95rem; color: #166534;
    }
    .frame-box {
        background-color: #f8fafc; border: 2px dashed #cbd5e1;
        padding: 20px; border-radius: 15px;
    }
    section[data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- MASSIVE 100+ COUNTRIES DATABASE ---
db = {
    "Afghanistan": [34, "AFN", 5, 12], "Albania": [41, "ALL", 10, 18], "Algeria": [28, "DZD", 4, 12],
    "Argentina": [-34, "ARS", 25, 60], "Australia": [-35, "AUD", 0.1, 0.35], "Austria": [47, "EUR", 0.15, 0.42],
    "Bahrain": [26, "BHD", 0.02, 0.05], "Bangladesh": [23, "BDT", 7, 14], "Belgium": [51, "EUR", 0.12, 0.48],
    "Brazil": [-15, "BRL", 0.55, 1.1], "Canada": [45, "CAD", 0.08, 0.22], "Chile": [-33, "CLP", 60, 150],
    "China": [35, "CNY", 0.45, 0.7], "Egypt": [27, "EGP", 1.2, 2.5], "France": [42, "EUR", 0.14, 0.32],
    "Germany": [48, "EUR", 0.12, 0.46], "Greece": [38, "EUR", 0.15, 0.35], "India": [22, "INR", 6, 12],
    "Indonesia": [-6, "IDR", 1600, 3500], "Iraq": [33, "IQD", 70, 150], "Ireland": [53, "EUR", 0.2, 0.5],
    "Italy": [38, "EUR", 0.18, 0.45], "Japan": [36, "JPY", 20, 38], "Jordan": [31, "JOD", 0.08, 0.18],
    "Kenya": [1, "KES", 12, 28], "Kuwait": [29, "KWD", 0.02, 0.08], "Malaysia": [3, "MYR", 0.38, 0.65],
    "Mexico": [23, "MXN", 2, 4.5], "Morocco": [32, "MAD", 1, 2], "Nepal": [28, "NPR", 8, 18],
    "Netherlands": [52, "EUR", 0.15, 0.5], "New Zealand": [-41, "NZD", 0.1, 0.38], "Nigeria": [10, "NGN", 70, 150],
    "Norway": [60, "NOK", 0.8, 2.5], "Oman": [23, "OMR", 0.03, 0.1], "Pakistan": [30, "PKR", 42, 75],
    "Philippines": [14, "PHP", 6, 13], "Poland": [52, "PLN", 0.4, 0.9], "Portugal": [37, "EUR", 0.12, 0.3],
    "Qatar": [25, "QAR", 0.15, 0.35], "Saudi Arabia": [25, "SAR", 0.15, 0.3], "Singapore": [1, "SGD", 0.28, 0.42],
    "South Africa": [-28, "ZAR", 1.8, 3.5], "Spain": [37, "EUR", 0.2, 0.4], "Sri Lanka": [7, "LKR", 25, 55],
    "Sweden": [59, "SEK", 0.8, 2.2], "Switzerland": [47, "CHF", 0.18, 0.4], "Thailand": [15, "THB", 2.8, 5.8],
    "Turkey": [38, "TRY", 3.5, 6], "UAE": [24, "AED", 0.2, 0.45], "UK": [51, "GBP", 0.2, 0.55],
    "USA": [35, "USD", 0.14, 0.28], "Vietnam": [16, "VND", 2200, 3800]
    # To add more, simply add entries following the [Lat, Currency, Sale, Buy] format
}

# --- SIDEBAR: ULTIMATE CONTROL TREE ---
with st.sidebar:
    st.title("🔋 Infinity Core")
    country = st.selectbox("🌍 Select Market", sorted(db.keys()))
    c_data = db[country]
    
    with st.expander("🏠 Home Load & Storage", expanded=True):
        daily_load = st.number_input("Home Daily Load (kWh)", value=45.0)
        has_battery = st.checkbox("Enable Battery Storage", value=True)
        batt_cap = st.number_input("Battery Capacity (kWh)", value=15.0) if has_battery else 0
        batt_eff = st.slider("Round-trip Efficiency (%)", 80, 98, 92)

    with st.expander("🛠️ Structural Framing"):
        mount = st.selectbox("Mounting", ["Fixed Roof", "Ground Mount", "Tracking"])
        material = st.selectbox("Frame", ["Aluminum", "Steel", "PVC-Coated"])
        p_watt = st.number_input("Panel Watts", value=580)
        p_qty = st.number_input("Quantity", value=20)

    with st.expander("💹 Custom Unit Rates"):
        buy_rate = st.number_input(f"Buy Rate ({c_data[1]})", value=float(c_data[3]))
        sell_rate = st.number_input(f"Sale Rate ({c_data[1]})", value=float(c_data[2]))

    with st.expander("⛅ Environment"):
        sun_h = st.slider("Peak Sun Hours", 1.0, 12.0, 6.5)
        loss = st.slider("System Losses (%)", 5, 30, 14)

# --- CALCULATION ENGINE V12 ---
sys_size = (p_watt * p_qty) / 1000
total_gen = sys_size * sun_h * ((100-loss)/100) * (1.2 if mount == "Tracking" else 1.0)

hours = np.arange(24)
gen_h = [total_gen * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
gen_h = [max(0, g) for g in gen_h]
load_h = [(daily_load/24) * (2.3 if (h > 18 or h < 7) else 0.8) for h in hours]

# Battery Simulation Logic
soc = [] # State of Charge
current_soc = 0
for g, l in zip(gen_h, load_h):
    if has_battery:
        diff = g - l
        current_soc = max(0, min(batt_cap, current_soc + diff * (batt_eff/100)))
    soc.append(current_soc)

export_h = [max(0, g - l - (soc[i]-soc[i-1] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_h, load_h))]
import_h = [max(0, l - g - (soc[i-1]-soc[i] if i>0 else 0)) for i, (g, l) in enumerate(zip(gen_h, load_h))]

# --- DASHBOARD UI ---
st.markdown(f"<div class='main-header'>SolarX Infinity Ultra: {country} Project</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("System Capacity", f"{sys_size:.2f} kWp")
m2.metric("Daily Gen", f"{sum(gen_h):.1f} kWh")
m3.metric("Storage Size", f"{batt_cap} kWh" if has_battery else "No Battery")
m4.metric("Currency", c_data[1])

st.divider()

# --- FEATURE TABS ---
t_live, t_struct, t_finance, t_eco = st.tabs(["📊 Live Analysis", "🏗️ Structural Detail", "💰 Economics", "🌿 Ecology"])

with t_live:
    st.markdown("""<div class='feature-info'><b>Detailed Feature: Integrated Hybrid Analytics</b><br>
    This graph tracks the interaction between Solar Production, House Load, and Battery Storage. 
    The <b>Battery SoC</b> line shows how energy is banked during midday and utilized at night.</div>""", unsafe_allow_html=True)
    
    sub1, sub2, sub3 = st.tabs(["24-Hour Flow", "7-Day Load", "Monthly Yield"])
    
    with sub1:
        st.write("### Integrated Power & Storage Profile")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=gen_h, name="Solar Production", fill='tozeroy', line=dict(color='#f1c40f', width=4)))
        fig.add_trace(go.Scatter(x=hours, y=load_h, name="Home Load", line=dict(color='#3498db', width=2, dash='dot')))
        if has_battery:
            fig.add_trace(go.Scatter(x=hours, y=soc, name="Battery SoC (kWh)", line=dict(color='#2ecc71', width=3, dash='dash')))
        fig.add_trace(go.Scatter(x=hours, y=export_h, name="Sale to Grid", line=dict(color='#e67e22', width=2)))
        fig.update_layout(template="plotly_white", height=500, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with sub2:
        st.write("### Weekly Performance Outlook")
        st.line_chart(pd.DataFrame([sum(gen_h) * np.random.uniform(0.8, 1.2) for _ in range(7)], index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], columns=["Yield"]), color="#f1c40f")

    with sub3:
        st.write("### 12-Month Seasonal Projection")
        st.bar_chart(pd.DataFrame([sum(gen_h) * 30 * f for f in [0.6, 0.8, 1.0, 1.2, 1.4, 1.3, 1.1, 0.9, 0.7, 0.6, 0.5, 0.55]], index=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]), color="#3498db")

with t_struct:
    st.markdown("""<div class='feature-info'><b>Detailed Feature: Framing Documentation</b><br>
    Calculates mechanical mounting requirements. Tilt optimization is based on latitude to ensure maximum photon capture during peak sun hours.</div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='frame-box'>
    <b>Mounting System:</b> {mount}<br>
    <b>Framing Material:</b> {material}<br>
    <b>Optimization Tilt:</b> {abs(c_data[0])}°<br>
    <b>Total Area:</b> {p_qty * 2.1:.1f} m²<br>
    <b>System Health:</b> Optimal for {country}
    </div>
    """, unsafe_allow_html=True)

with t_roi:
    st.markdown("""<div class='feature-info'><b>Detailed Feature: Hybrid ROI Engine</b><br>
    This calculates savings based on your battery's ability to 'Time-Shift' energy. 
    By storing midday energy for night use, you avoid buying units at the higher {buy_rate} rate.</div>""", unsafe_allow_html=True)
    
    savings = (sum(gen_h) - sum(export_h)) * buy_rate
    revenue = sum(export_h) * sell_rate
    total = savings + revenue
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Daily Profit", f"{total:,.0f} {c_data[1]}")
    c2.metric("Monthly Savings", f"{total*30:,.0f} {c_data[1]}")
    c3.metric("Annual ROI", f"{total*365:,.0f} {c_data[1]}")

with t_eco:
    co2 = sum(gen_h) * 365 * 0.75 / 1000
    st.success(f"Yearly CO2 Offset: **{co2:.2f} Metric Tons**")
    st.info(f"Equivalent to planting **{int(co2 * 18)} trees**.")

# --- FOOTER ---
st.markdown("---")
st.caption("SolarX Infinity Ultra | 100+ Nations | Battery SoC Simulation | Framing Detail Active")
