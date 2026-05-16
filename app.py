import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Global Sovereign", layout="wide", page_icon="🌐")

# --- PREMIUM LIGHT THEME STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    [data-testid="stMetricValue"] { color: #0d6efd !important; font-size: 28px; }
    .stMetric { 
        background-color: #ffffff; 
        border: 1px solid #edf2f7; 
        border-radius: 12px; 
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    }
    .section-header { 
        color: #1a202c; 
        font-size: 30px; 
        font-weight: 800; 
        border-left: 5px solid #ffc107; 
        padding-left: 15px; 
        margin-bottom: 25px; 
    }
    .spec-box { 
        background-color: #f7fafc; 
        border: 1px solid #e2e8f0; 
        padding: 25px; 
        border-radius: 16px; 
        color: #2d3748;
        line-height: 1.8;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- EXPANDED 100+ COUNTRIES DATABASE ---
# [Optimal Tilt, Currency, Avg Sale Rate, Avg Purchase Rate]
db = {
    "Afghanistan": [34, "AFN", 5.0, 10.0], "Albania": [41, "ALL", 8.0, 15.0], "Algeria": [28, "DZD", 4.0, 12.0],
    "Angola": [-12, "AOA", 15, 30], "Argentina": [-34, "ARS", 25.0, 60.0], "Armenia": [40, "AMD", 20, 45],
    "Australia": [-35, "AUD", 0.08, 0.32], "Austria": [47, "EUR", 0.12, 0.38], "Azerbaijan": [40, "AZN", 0.06, 0.12],
    "Bahrain": [26, "BHD", 0.02, 0.05], "Bangladesh": [23, "BDT", 6.0, 12.0], "Belarus": [53, "BYN", 0.15, 0.30],
    "Belgium": [51, "EUR", 0.08, 0.45], "Bolivia": [-16, "BOB", 0.5, 1.2], "Brazil": [-15, "BRL", 0.50, 1.05],
    "Bulgaria": [42, "BGN", 0.15, 0.35], "Cambodia": [12, "KHR", 400, 800], "Canada": [45, "CAD", 0.06, 0.18],
    "Chile": [-33, "CLP", 60.0, 150.0], "China": [35, "CNY", 0.42, 0.65], "Colombia": [4, "COP", 350, 700],
    "Croatia": [45, "EUR", 0.10, 0.25], "Cyprus": [35, "EUR", 0.18, 0.40], "Czech Republic": [50, "CZK", 2.5, 6.5],
    "Denmark": [55, "DKK", 0.65, 2.8], "Egypt": [27, "EGP", 1.0, 2.0], "Estonia": [58, "EUR", 0.08, 0.30],
    "Ethiopia": [9, "ETB", 0.6, 1.4], "Finland": [60, "EUR", 0.09, 0.35], "France": [42, "EUR", 0.12, 0.28],
    "Georgia": [42, "GEL", 0.10, 0.25], "Germany": [48, "EUR", 0.10, 0.44], "Ghana": [5, "GHS", 0.7, 1.5],
    "Greece": [38, "EUR", 0.15, 0.35], "Hong Kong": [22, "HKD", 3.0, 5.0], "Hungary": [47, "HUF", 30, 80],
    "Iceland": [64, "ISK", 6.0, 18.0], "India": [22, "INR", 5.5, 10.5], "Indonesia": [-6, "IDR", 1500, 3200],
    "Iran": [32, "IRR", 5000, 15000], "Iraq": [33, "IQD", 70, 150], "Ireland": [53, "EUR", 0.20, 0.50],
    "Israel": [31, "ILS", 0.45, 0.65], "Italy": [38, "EUR", 0.15, 0.40], "Jamaica": [18, "JMD", 15, 35],
    "Japan": [36, "JPY", 18.0, 35.0], "Jordan": [31, "JOD", 0.08, 0.18], "Kazakhstan": [48, "KZT", 15, 30],
    "Kenya": [1, "KES", 12, 28], "Kuwait": [29, "KWD", 0.02, 0.08], "Latvia": [56, "EUR", 0.10, 0.35],
    "Lebanon": [33, "LBP", 2000, 5000], "Libya": [25, "LYD", 0.05, 0.15], "Lithuania": [55, "EUR", 0.09, 0.38],
    "Luxembourg": [49, "EUR", 0.15, 0.35], "Malaysia": [3, "MYR", 0.35, 0.60], "Maldives": [4, "MVR", 2.0, 4.5],
    "Mexico": [23, "MXN", 1.8, 3.8], "Mongolia": [47, "MNT", 150, 300], "Morocco": [32, "MAD", 1.0, 2.0],
    "Myanmar": [21, "MMK", 50, 150], "Nepal": [28, "NPR", 8.0, 18.0], "Netherlands": [52, "EUR", 0.12, 0.45],
    "New Zealand": [-41, "NZD", 0.10, 0.38], "Nigeria": [10, "NGN", 70, 150], "Norway": [60, "NOK", 0.7, 2.0],
    "Oman": [23, "OMR", 0.02, 0.08], "Pakistan": [30, "PKR", 42.0, 72.0], "Palestine": [31, "ILS", 0.5, 0.8],
    "Panama": [9, "PAB", 0.12, 0.22], "Peru": [-12, "PEN", 0.30, 0.65], "Philippines": [14, "PHP", 6.0, 13.0],
    "Poland": [52, "PLN", 0.40, 0.90], "Portugal": [37, "EUR", 0.12, 0.30], "Qatar": [25, "QAR", 0.12, 0.30],
    "Romania": [45, "RON", 0.5, 1.0], "Russia": [55, "RUB", 3.0, 6.0], "Saudi Arabia": [25, "SAR", 0.12, 0.25],
    "Serbia": [44, "RSD", 10, 25], "Singapore": [1, "SGD", 0.25, 0.38], "Slovakia": [48, "EUR", 0.12, 0.30],
    "Slovenia": [46, "EUR", 0.10, 0.28], "South Africa": [-28, "ZAR", 1.5, 3.2], "South Korea": [36, "KRW", 180, 320],
    "Spain": [37, "EUR", 0.18, 0.35], "Sri Lanka": [7, "LKR", 25, 55], "Sweden": [59, "SEK", 0.8, 2.2],
    "Switzerland": [47, "CHF", 0.18, 0.40], "Taiwan": [24, "TWD", 4.5, 7.0], "Tanzania": [-6, "TZS", 150, 400],
    "Thailand": [15, "THB", 2.5, 5.2], "Tunisia": [34, "TND", 0.2, 0.5], "Turkey": [38, "TRY", 3.0, 5.5],
    "UAE": [24, "AED", 0.18, 0.40], "Uganda": [0, "UGX", 300, 700], "Ukraine": [49, "UAH", 5.0, 8.5],
    "UK": [51, "GBP", 0.18, 0.52], "USA": [35, "USD", 0.12, 0.24], "Uruguay": [-33, "UYU", 4.0, 9.0],
    "Uzbekistan": [41, "UZS", 500, 1000], "Venezuela": [10, "VED", 5, 15], "Vietnam": [16, "VND", 2000, 3500],
    "Zambia": [-15, "ZMW", 0.5, 1.2], "Zimbabwe": [-18, "ZWL", 10, 25]
}

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.title("⚙️ Engine Parameters")
    selected_country = st.selectbox("Market Selection (100+ Nations)", sorted(db.keys()))
    c_data = db[selected_country]
    
    with st.expander("🛠️ Technical Configuration"):
        p_watt = st.number_input("Panel Power (W)", value=580)
        p_num = st.number_input("Panel Count", value=18)
        p_type = st.selectbox("Cell Type", ["N-Type TOPCon", "Mono-PERC", "Bifacial Pro"])
    
    with st.expander("💰 Tariff & Rate Controls"):
        buy_rate = st.number_input(f"Grid Buy Price ({c_data[1]})", value=float(c_data[3]))
        sell_rate = st.number_input(f"Grid Sale Price ({c_data[1]})", value=float(c_data[2]))
        
    with st.expander("🔋 Advanced Hardware"):
        inv_eff = st.slider("Inverter Efficiency (%)", 90.0, 99.0, 97.5)
        has_batt = st.checkbox("Storage System")
        batt_cap = st.number_input("Battery Size (kWh)", value=15.0) if has_batt else 0
        
    with st.expander("⚡ Daily Dynamics"):
        daily_load = st.number_input("Energy Demand (kWh)", value=35.0)
        sun_h = st.slider("Peak Sun Hours", 1.0, 12.0, 7.0)

# --- ENGINE CALCULATION ---
sys_size = (p_watt * p_num) / 1000
net_yield_daily = sys_size * sun_h * (inv_eff / 100) * 0.94 # System Loss Factor

hours = np.arange(24)
gen_h = [net_yield_daily * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
gen_h = [max(0, g) for g in gen_h]
load_h = [(daily_load/24) * (2.0 if (h > 18 or h < 7) else 0.8) for h in hours]

export_u = [max(0, g - l) for g, l in zip(gen_h, load_h)]
import_u = [max(0, l - g) for g, l in zip(gen_h, load_h)]
self_cons = [min(g, l) for g, l in zip(gen_h, load_h)]

# --- DASHBOARD UI ---
st.markdown(f"<div class='section-header'>SolarX Project Architecture: {selected_country}</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("DC Peak Power", f"{sys_size:.2f} kWp")
m2.metric("Daily Production", f"{sum(gen_h):.1f} kWh")
m3.metric("Annual Carbon Offset", f"{sum(gen_h)*365*0.7/1000:.1f} Tons")
m4.metric("Market Currency", c_data[1])

st.divider()

# --- CONTENT TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📉 Live Analytics", "📜 Specifications", "💸 Economic ROI", "🌿 Ecology"])

with tab1:
    st.subheader("24-Hour Predictive Power Flow")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=gen_h, name="Solar Output", fill='tozeroy', line=dict(color='#ffc107', width=4)))
    fig.add_trace(go.Scatter(x=hours, y=load_h, name="Demand Curve", line=dict(color='#0d6efd', width=3, dash='dot')))
    fig.add_trace(go.Scatter(x=hours, y=export_u, name="Export to Grid", line=dict(color='#198754')))
    fig.add_trace(go.Scatter(x=hours, y=import_u, name="Grid Import", line=dict(color='#dc3545')))
    fig.update_layout(template="plotly_white", height=500, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Technical Design Parameters")
    st.markdown(f"""
    <div class='spec-box'>
    <b>I. Photovoltaic Array:</b><br>
    - Technology: {p_type} Modules<br>
    - Capacity: {p_num} Panels @ {p_watt}W each<br>
    - Optimal Installation Tilt: {abs(c_data[0])}° Facing {'North' if c_data[0] < 0 else 'South'}<br><br>
    
    <b>II. Energy Tariffs:</b><br>
    - Utility Buy Rate: {buy_rate} {c_data[1]}/Unit<br>
    - Feed-in (Sale) Rate: {sell_rate} {c_data[1]}/Unit<br><br>
    
    <b>III. System Architecture:</b><br>
    - Inverter Efficiency: {inv_eff}%<br>
    - Storage: {'Hybrid Enabled (' + str(batt_cap) + ' kWh)' if has_batt else 'Grid-Tied Standard'}
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.subheader("Financial Performance Evaluation")
    rev_export = sum(export_u) * sell_rate
    sav_usage = sum(self_cons) * buy_rate
    daily_benefit = rev_export + sav_usage
    
    f1, f2, f3 = st.columns(3)
    f1.metric("Est. Monthly Benefit", f"{daily_benefit*30:,.0f} {c_data[1]}")
    f2.metric("Est. Annual Revenue", f"{daily_benefit*365:,.0f} {c_data[1]}")
    f3.metric("Net Monthly Bill", f"{(sum(import_u)*30*buy_rate - rev_export*30):,.0f} {c_data[1]}")
    
    st.info("The system automatically prioritizes self-consumption to maximize savings based on current tariffs.")

with tab4:
    st.subheader("Global Sustainability Footprint")
    co2_total = sum(gen_h) * 365 * 0.72 / 1000
    st.success(f"Annual Carbon Displacement: **{co2_total:.2f} Metric Tons** of CO2.")
    st.info(f"Ecological Equivalent: **{int(co2_total * 15)} mature trees** planted per year.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"SolarX Sovereign Edition v6.0 | Database Scale: 100+ Nations | High-Performance Engine Active")
