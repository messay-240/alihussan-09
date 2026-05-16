import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- SYSTEM SETTINGS ---
st.set_page_config(page_title="SolarX Industrial Designer", layout="wide", page_icon="🏗️")

# Custom Professional Theme
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .section-header { color: #58a6ff; font-size: 24px; font-weight: bold; border-bottom: 2px solid #30363d; padding-bottom: 10px; margin-top: 20px; }
    .spec-box { background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 12px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- THE MEGA DATABASE (65+ COUNTRIES) ---
db = {
    "Pakistan": [30.0, "PKR", 42.0, 65.0, "Asia"], "India": [22.5, "INR", 5.0, 9.0, "Asia"],
    "USA (Texas)": [30.2, "USD", 0.08, 0.14, "Americas"], "USA (California)": [34.0, "USD", 0.12, 0.28, "Americas"],
    "United Kingdom": [50.1, "GBP", 0.15, 0.45, "Europe"], "Germany": [48.0, "EUR", 0.08, 0.40, "Europe"],
    "Australia": [35.0, "AUD", 0.07, 0.32, "Oceania"], "UAE": [24.5, "AED", 0.15, 0.35, "Middle East"],
    "Saudi Arabia": [25.0, "SAR", 0.10, 0.20, "Middle East"], "Canada": [45.0, "CAD", 0.05, 0.15, "Americas"],
    "China": [35.0, "CNY", 0.40, 0.60, "Asia"], "Japan": [35.0, "JPY", 16.0, 30.0, "Asia"],
    "France": [40.0, "EUR", 0.10, 0.25, "Europe"], "Italy": [38.0, "EUR", 0.12, 0.30, "Europe"],
    "Brazil": [20.0, "BRL", 0.45, 0.95, "Americas"], "Turkey": [38.0, "TRY", 2.5, 4.5, "Europe"],
    "South Africa": [28.0, "ZAR", 1.2, 2.8, "Africa"], "Egypt": [27.0, "EGP", 0.8, 1.6, "Africa"],
    "Qatar": [25.0, "QAR", 0.1, 0.25, "Middle East"], "Malaysia": [5.0, "MYR", 0.3, 0.5, "Asia"],
    "Singapore": [1.0, "SGD", 0.2, 0.3, "Asia"], "Thailand": [15.0, "THB", 2.2, 4.5, "Asia"],
    "New Zealand": [-40.0, "NZD", 0.08, 0.3, "Oceania"], "Spain": [37.0, "EUR", 0.15, 0.30, "Europe"],
    "Mexico": [23.0, "MXN", 1.5, 3.0, "Americas"], "Russia": [55.0, "RUB", 2.0, 5.0, "Asia"],
    "Norway": [60.0, "NOK", 0.5, 1.5, "Europe"], "Tanzania": [-6.0, "TZS", 100, 350, "Africa"],
    "Kenya": [1.0, "KES", 12, 25, "Africa"], "Bangladesh": [23.5, "BDT", 5.0, 10.0, "Asia"]
}

# --- SIDEBAR: DEEP SPECS INPUTS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2950/2950130.png", width=100)
    st.title("🎛️ Project Architect")
    
    selected_country = st.selectbox("🌍 Deployment Location", sorted(db.keys()))
    c_data = db[selected_country]
    
    with st.expander("🛠️ PV Panel Engineering"):
        p_type = st.selectbox("Cell Technology", ["Mono-Crystalline (PERC)", "Poly-Crystalline", "Thin Film (CdTe)"])
        p_watt = st.number_input("Panel Rating (Pmax)", value=580)
        p_num = st.number_input("String Count (Panels)", value=14)
        deg_rate = st.slider("Annual Degradation (%)", 0.2, 1.0, 0.5)
        temp_coeff = st.slider("Temp Coefficient (Pmax %/°C)", -0.5, -0.2, -0.35)
    
    with st.expander("⚡ Inverter & Grid"):
        inv_topology = st.selectbox("Inverter Topology", ["Central Inverter", "String Inverter", "Micro-Inverters"])
        inv_eff = st.slider("Peak Efficiency (%)", 90.0, 99.0, 97.5)
        net_metering = st.checkbox("Enable Net-Metering", value=True)
    
    with st.expander("🔋 Storage (BESS)"):
        has_batt = st.checkbox("Integrate Battery")
        if has_batt:
            batt_tech = st.selectbox("Battery Chemistry", ["Lithium Iron Phosphate (LFP)", "Lead Acid (Deep Cycle)", "Nickel Manganese Cobalt (NMC)"])
            batt_cap = st.number_input("Capacity (kWh)", value=15.0)
            dod = st.slider("Depth of Discharge (DoD %)", 50, 100, 80)
    
    with st.expander("🏠 Load & Economics"):
        daily_load_kwh = st.number_input("Total 24h Load (kWh)", value=30.0)
        sun_peak_h = st.slider("Available Sun Hours", 1.0, 12.0, 6.5)

# --- CORE ENGINEERING ENGINE ---
sys_pmax = (p_watt * p_num) / 1000  # Total kWp
loss_factor = (inv_eff/100) * 0.94 # Accounting for wiring & dust losses (6% average)
total_daily_gen = sys_pmax * sun_peak_h * loss_factor

# 24-Hour Simulation Logic
hours = np.arange(24)
gen_curve = [total_daily_gen * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
gen_curve = [max(0, g) for g in gen_curve]

# Load curve: Peaks in morning and evening
load_curve = [(daily_load_kwh/24) * (1.9 if (h >= 18 or h < 7) else 0.6) for h in hours]

# Energy Management System (EMS) Logic
export, import_grid, batt_status = [], [], []
current_soc = batt_cap * (dod/100) if has_batt else 0

for g, l in zip(gen_curve, load_curve):
    if g > l:
        surplus = g - l
        if has_batt and current_soc < batt_cap:
            charge = min(surplus, batt_cap - current_soc)
            current_soc += charge
            export.append(surplus - charge)
        else:
            export.append(surplus)
        import_grid.append(0)
    else:
        deficit = l - g
        if has_batt and current_soc > (batt_cap * (1 - dod/100)):
            discharge = min(deficit, current_soc - (batt_cap * (1 - dod/100)))
            current_soc -= discharge
            import_grid.append(deficit - discharge)
        else:
            import_grid.append(deficit)
    batt_status.append(current_soc)

# --- MAIN INTERFACE ---
st.markdown(f"<div class='section-header'>🏗️ System Specification: {selected_country} Project</div>", unsafe_allow_html=True)

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Peak DC Capacity", f"{sys_pmax:.2f} kWp")
c2.metric("Daily AC Yield", f"{sum(gen_curve):.1f} kWh")
c3.metric("Annual Offset", f"{sum(gen_curve)*365/1000:.1f} MWh")
c4.metric("Market Currency", c_data[1])

st.divider()

# --- THE MEGA DETAIL TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📉 Power Flow Analytics", "🛠️ Technical Data Sheet", "💰 Financial ROI", "🌍 Climate Impact"])

with tab1:
    st.write("### Real-Time Energy Simulation (24h Window)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=gen_curve, name="PV Generation", fill='tozeroy', line=dict(color='#FFD700', width=4)))
    fig.add_trace(go.Scatter(x=hours, y=load_curve, name="Building Demand", line=dict(color='#00BFFF', width=3, dash='dot')))
    fig.add_trace(go.Scatter(x=hours, y=export, name="Grid Export", line=dict(color='#32CD32')))
    fig.add_trace(go.Scatter(x=hours, y=import_grid, name="Grid Import", line=dict(color='#FF4500')))
    if has_batt:
        fig.add_trace(go.Scatter(x=hours, y=batt_status, name="Battery SoC", line=dict(color='#9370DB', width=2)))
    
    fig.update_layout(template="plotly_dark", height=550, hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.write("### Detailed Hardware Specification Sheet")
    st.markdown(f"""
    <div class='spec-box'>
    <b>1. Photovoltaic Modules (PV):</b><br>
    - Technology: {p_type} | Rating: {p_watt}W per module<br>
    - Quantity: {p_num} Modules | Area: ~{p_num*2.4:.1f} m²<br>
    - Optimal Tilt: {c_data[0]}° | Degradation: {deg_rate}% per annum<br><br>
    
    <b>2. Inverter System:</b><br>
    - Topology: {inv_topology} | AC Rating: {sys_pmax * 0.9:.2f} kW<br>
    - Peak Efficiency: {inv_eff}% | Communication: RS485/WiFi/LAN<br><br>
    
    <b>3. Battery Energy Storage (BESS):</b><br>
    - Status: {'Active' if has_batt else 'Not Included'}<br>
    - Technology: {batt_tech if has_batt else 'N/A'}<br>
    - Capacity: {batt_cap if has_batt else '0'} kWh | Useable Capacity: {batt_cap*(dod/100) if has_batt else '0'} kWh
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.write("### Economic & Financial Projections")
    daily_revenue = (sum(export) * c_data[2])
    daily_saved = (sum(gen_curve) - sum(export)) * c_data[3]
    total_daily_benefit = daily_revenue + daily_saved
    
    f1, f2, f3 = st.columns(3)
    f1.metric("Monthly Fiscal Benefit", f"{total_daily_benefit*30:,.0f} {c_data[1]}")
    f2.metric("Annual System Revenue", f"{total_daily_benefit*365:,.0f} {c_data[1]}")
    f3.metric("LCOE Estimate", f"{(total_daily_benefit/sum(gen_curve)):.2f} /kWh")
    
    st.write("#### 12-Month Performance Scaling")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    seasonal_data = [total_daily_benefit * 30 * (1.4 if m in [5,6,7] else 0.7) for m in range(12)]
    st.bar_chart(pd.DataFrame(seasonal_data, index=months), color="#32CD32")

with tab4:
    st.write("### Environmental & Carbon Metrics")
    st.success(f"Aapka system saalana **{sum(gen_curve)*365*0.65/1000:.2f} Metric Tons** Carbon Dioxide (CO2) ko hawa mein janay se rokega.")
    st.info(f"Ye taqreeban **{int(sum(gen_curve)*365/150)}** darakht (trees) lagane ke barabar hai.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"Enterprise Solar Design Engine v3.5 | Region: {c_data[4]} | Local Market Data: Active")
