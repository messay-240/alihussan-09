import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SYSTEM CONFIGURATION ---
st.set_page_config(page_title="SolarX Omni-Ultimate v17.2", layout="wide", page_icon="⚡")

# --- ENTERPRISE LIGHT THEME CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-size: 24px; font-weight: 800; }
    .stMetric { 
        background-color: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 12px; padding: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .main-header { 
        color: #1a202c; font-size: 34px; font-weight: 900; 
        border-left: 10px solid #fbbf24; padding-left: 20px; margin-bottom: 30px; 
    }
    .ict-requirement {
        background-color: #f0fdf4; border-left: 5px solid #22c55e;
        padding: 15px; border-radius: 0 10px 10px 0; margin-bottom: 20px;
    }
    .team-card {
        background-color: #f8fafc; border: 1px solid #cbd5e1;
        padding: 10px; border-radius: 8px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- EXPANDED GLOBAL DATA (110+ ENTRIES) ---
# Format: [Latitude, Currency, Export Rate, Import Rate, Avg Wind m/s]
db = {
    "Afghanistan": [33.9, "AFN", 5, 12, 4.2], "Albania": [41.1, "ALL", 10, 18, 3.8], "Algeria": [28.0, "DZD", 4, 12, 4.5],
    "Andorra": [42.5, "EUR", 0.12, 0.28, 3.1], "Angola": [-11.2, "AOA", 15, 30, 3.5], "Argentina": [-38.4, "ARS", 25, 65, 5.5],
    "Armenia": [40.1, "AMD", 25, 45, 3.2], "Australia": [-25.2, "AUD", 0.10, 0.35, 6.2], "Austria": [47.5, "EUR", 0.15, 0.45, 3.1],
    "Azerbaijan": [40.1, "AZN", 0.05, 0.12, 4.0], "Bahamas": [25.0, "BSD", 0.15, 0.38, 5.8], "Bahrain": [26.0, "BHD", 0.02, 0.06, 4.5],
    "Bangladesh": [23.6, "BDT", 7.5, 14.0, 3.5], "Barbados": [13.2, "BBD", 0.20, 0.45, 5.2], "Belarus": [53.7, "BYN", 0.12, 0.25, 4.1],
    "Belgium": [50.5, "EUR", 0.12, 0.52, 5.8], "Belize": [17.2, "BZD", 0.15, 0.40, 4.4], "Benin": [9.3, "XOF", 45, 110, 3.6],
    "Bhutan": [27.5, "BTN", 3, 8, 3.0], "Bolivia": [-16.3, "BOB", 0.40, 0.90, 4.1], "Bosnia": [43.9, "BAM", 0.10, 0.22, 3.4],
    "Botswana": [-22.3, "BWP", 0.60, 1.25, 4.2], "Brazil": [-14.2, "BRL", 0.55, 1.15, 4.0], "Brunei": [4.5, "BND", 0.05, 0.12, 2.5],
    "Bulgaria": [42.7, "BGN", 0.15, 0.35, 4.2], "Cambodia": [12.6, "KHR", 250, 650, 3.1], "Cameroon": [7.4, "XAF", 40, 95, 3.3],
    "Canada": [56.1, "CAD", 0.08, 0.24, 5.1], "Chile": [-35.6, "CLP", 65, 155, 4.8], "China": [35.8, "CNY", 0.42, 0.72, 3.9],
    "Colombia": [4.6, "COP", 250, 600, 3.5], "Costa Rica": [9.7, "CRC", 45, 120, 4.2], "Croatia": [45.1, "EUR", 0.12, 0.28, 3.9],
    "Cuba": [21.5, "CUP", 1.5, 4.5, 5.2], "Cyprus": [35.1, "EUR", 0.15, 0.35, 4.1], "Czechia": [49.8, "CZK", 2.5, 6.5, 3.8],
    "Denmark": [56.2, "DKK", 0.65, 2.80, 6.5], "Dominica": [15.4, "XCD", 0.25, 0.65, 5.5], "Ecuador": [-1.8, "USD", 0.05, 0.12, 3.5],
    "Egypt": [26.8, "EGP", 1.2, 2.6, 4.8], "Estonia": [58.6, "EUR", 0.12, 0.32, 5.4], "Ethiopia": [9.1, "ETB", 0.8, 2.5, 4.1],
    "Fiji": [-17.7, "FJD", 0.15, 0.35, 4.8], "Finland": [61.9, "EUR", 0.08, 0.38, 4.5], "France": [46.2, "EUR", 0.15, 0.34, 4.7],
    "Gabon": [-0.8, "XAF", 50, 115, 3.1], "Georgia": [42.3, "GEL", 0.10, 0.25, 3.8], "Germany": [51.1, "EUR", 0.12, 0.48, 5.0],
    "Ghana": [7.9, "GHS", 0.45, 1.20, 3.7], "Greece": [39.0, "EUR", 0.18, 0.38, 4.2], "Guyana": [4.9, "GYD", 15, 35, 4.5],
    "Honduras": [15.2, "HNL", 1.5, 4.2, 3.9], "Hungary": [47.2, "HUF", 25, 75, 3.5], "Iceland": [64.9, "ISK", 5, 18, 8.2],
    "India": [20.5, "INR", 6.2, 12.5, 4.1], "Indonesia": [-0.7, "IDR", 1500, 3400, 2.8], "Iran": [32.4, "IRR", 500, 1500, 4.2],
    "Iraq": [33.2, "IQD", 70, 160, 4.2], "Ireland": [53.1, "EUR", 0.22, 0.55, 5.8], "Israel": [31.0, "ILS", 0.25, 0.55, 4.1],
    "Italy": [41.8, "EUR", 0.20, 0.50, 3.5], "Jamaica": [18.1, "JMD", 12, 35, 4.9], "Japan": [36.2, "JPY", 21, 42, 4.6],
    "Jordan": [30.5, "JOD", 0.08, 0.18, 4.1], "Kazakhstan": [48.0, "KZT", 12, 25, 4.8], "Kenya": [-1.2, "KES", 12, 28, 4.2],
    "Kuwait": [29.3, "KWD", 0.02, 0.08, 4.5], "Latvia": [56.9, "EUR", 0.15, 0.35, 4.8], "Lebanon": [33.9, "LBP", 1500, 4500, 3.8],
    "Lithuania": [55.2, "EUR", 0.14, 0.30, 4.9], "Luxembourg": [49.8, "EUR", 0.15, 0.35, 4.2], "Malaysia": [4.2, "MYR", 0.38, 0.68, 2.5],
    "Malta": [35.9, "EUR", 0.15, 0.32, 5.2], "Mexico": [23.6, "MXN", 2.2, 4.8, 4.3], "Mongolia": [46.9, "MNT", 55, 125, 5.1],
    "Morocco": [31.7, "MAD", 1.1, 2.2, 4.5], "Namibia": [-22.9, "NAD", 0.85, 1.85, 4.8], "Nepal": [28.3, "NPR", 8.2, 18.5, 3.2],
    "Netherlands": [52.1, "EUR", 0.16, 0.55, 6.5], "New Zealand": [-40.9, "NZD", 0.11, 0.40, 5.8], "Nigeria": [9.0, "NGN", 70, 160, 3.5],
    "Norway": [60.4, "NOK", 0.9, 2.8, 5.5], "Oman": [21.5, "OMR", 0.03, 0.12, 4.2], "Pakistan": [30.3, "PKR", 42.0, 82.0, 3.7],
    "Panama": [8.5, "USD", 0.10, 0.22, 4.1], "Peru": [-9.2, "PEN", 0.15, 0.45, 3.8], "Philippines": [12.8, "PHP", 6.2, 14.0, 4.5],
    "Poland": [51.9, "PLN", 0.35, 0.85, 4.2], "Portugal": [39.3, "EUR", 0.14, 0.32, 4.8], "Qatar": [25.3, "QAR", 0.15, 0.38, 4.5],
    "Romania": [45.9, "RON", 0.45, 1.15, 3.9], "Saudi Arabia": [23.8, "SAR", 0.15, 0.32, 4.2], "Serbia": [44.0, "RSD", 12, 25, 3.5],
    "Singapore": [1.3, "SGD", 0.28, 0.45, 3.1], "Slovakia": [48.7, "EUR", 0.15, 0.35, 3.7], "Slovenia": [46.1, "EUR", 0.12, 0.28, 3.4],
    "South Africa": [-30.5, "ZAR", 1.9, 3.8, 5.2], "South Korea": [35.9, "KRW", 85, 185, 4.2], "Spain": [40.4, "EUR", 0.22, 0.45, 4.1],
    "Sri Lanka": [7.8, "LKR", 25, 58, 4.2], "Sweden": [60.1, "SEK", 0.85, 2.40, 5.2], "Switzerland": [46.8, "CHF", 0.20, 0.45, 3.2],
    "Taiwan": [23.7, "TWD", 2.5, 5.5, 4.8], "Thailand": [15.8, "THB", 2.8, 6.0, 3.2], "Turkey": [38.9, "TRY", 3.5, 6.5, 4.2],
    "UAE": [23.4, "AED", 0.22, 0.48, 4.5], "UK": [55.3, "GBP", 0.22, 0.58, 6.0], "Ukraine": [48.4, "UAH", 3.5, 7.2, 4.1],
    "Uruguay": [-32.5, "UYU", 2.5, 6.8, 5.2], "USA": [37.0, "USD", 0.14, 0.30, 4.8], "Uzbekistan": [41.4, "UZS", 250, 650, 3.8],
    "Vietnam": [14.0, "VND", 2200, 3800, 3.4], "Zambia": [-13.1, "ZMW", 0.45, 1.15, 3.2], "Zimbabwe": [-19.0, "USD", 0.12, 0.28, 3.5]
}

# --- SIDEBAR: ADVANCED ARCHITECT ---
with st.sidebar:
    st.title("🛡️ Project Architect")
    country = st.selectbox("🌍 Deployment Location", sorted(db.keys()))
    c_lat, c_curr, c_sale, c_buy, avg_wind = db[country]
    with st.expander("🏠 Load & Storage"):
        h_load = st.number_input("Daily Consumption (kWh)", value=50.0)
        has_batt = st.checkbox("Include Battery", value=True)
        batt_cap = st.number_input("Capacity (kWh)", value=15.0) if has_batt else 0

# --- CALCULATIONS ---
sys_size = (p_watt * p_qty) / 1000
angle_eff = np.cos(np.radians(tilt - abs(c_lat))) * np.cos(np.radians(azimuth))
daily_yield = sys_size * 6.8 * 0.85 * max(0.5, angle_eff)

# LIVE Wind Threat Logic based on Tilt Angle
wind_threat = min(100, (avg_wind * np.sin(np.radians(tilt)) * 18))

hours = np.arange(24)
gen_24 = [daily_yield * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
load_24 = [(h_load/24) * (2.8 if (h > 18 or h < 7) else 0.7) for h in hours]

# --- DASHBOARD ---
st.markdown(f"<div class='main-header'>SolarX Omni-Ultimate: {country} Project</div>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("System Peak", f"{sys_size:.2f} kWp")
k2.metric("Est. Daily Gen", f"{sum(gen_24):.1f} kWh")
k3.metric("Tilt Angle", f"{tilt}°")
k4.metric("Wind Threat", f"{wind_threat:.1f}%")

st.divider()
# --- SIDEBAR: ADVANCED ARCHITECT ---
with st.sidebar:
    
    with st.expander("📐 Technical Orientation", expanded=True):
        tilt = st.slider("Panel Tilt Angle (°)", 0, 90, int(abs(c_lat)))
        azimuth = st.slider("Azimuth Angle (0°=South, 180°=North)", -180, 180, 0)
        st.caption(f"Suggested Tilt for {country}: {abs(c_lat)}°")

    with st.expander("🏗️ Mechanical Framing"):
        p_watt = st.number_input("Panel Rating (W)", value=585)
        p_qty = st.number_input("Module Count", value=20)
        mount = st.selectbox("Mount Style", ["Roof-Top", "Ground-Mount", "Tracker"])

# --- CALCULATIONS ---
sys_size = (p_watt * p_qty) / 1000
# Azimuth and Tilt efficiency logic
angle_eff = np.cos(np.radians(tilt - abs(c_lat))) * np.cos(np.radians(azimuth))
daily_yield = sys_size * 6.8 * 0.85 * max(0.5, angle_eff)

hours = np.arange(24)
gen_24 = [daily_yield * np.sin(np.pi * (h-6)/12) if 6 <= h <= 18 else 0 for h in hours]
load_24 = [(h_load/24) * (2.8 if (h > 18 or h < 7) else 0.7) for h in hours]

# --- DASHBOARD ---
st.markdown(f"<div class='main-header'>SolarX Omni-Ultimate: {country} Project</div>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("System Peak", f"{sys_size:.2f} kWp")
k2.metric("Est. Daily Gen", f"{sum(gen_24):.1f} kWh")
k3.metric("Tilt/Azimuth", f"{tilt}° / {azimuth}°")
k4.metric("Market Local", c_curr)

st.divider()

# --- ICT EVALUATION TABS ---
t_ana, t_impact, t_share, t_team = st.tabs([
    "📈 Power Flow Analytics", 
    "🌍 Community & Awareness", 
    "📚 Knowledge Sharing", 
    "👥 Team Contribution & Ethics"
])

with t_ana:
    st.write("### Multi-Temporal Line Analytics")
    sub_d, sub_w, sub_m = st.tabs(["24-Hour Day", "7-Day Week", "12-Month Year"])
    
    with sub_d:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=gen_24, name="Generation (kW)", fill='tozeroy', line=dict(color='#f1c40f', width=4)))
        fig.add_trace(go.Scatter(x=hours, y=load_24, name="House Load (kW)", line=dict(color='#3498db', width=2, dash='dot')))
        fig.update_layout(template="plotly_white", height=450, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with sub_w:
        w_data = [sum(gen_24) * np.random.uniform(0.8, 1.2) for _ in range(7)]
        st.line_chart(pd.DataFrame(w_data, index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], columns=["Yield"]), color="#f1c40f")

    with sub_m:
        m_gen = [sum(gen_24) * 30 * f for f in [0.6, 0.75, 1.0, 1.3, 1.4, 1.25, 1.1, 0.9, 0.7, 0.6, 0.55, 0.65]]
        st.line_chart(pd.DataFrame(m_gen, index=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], columns=["Monthly kWh"]), color="#3498db")

with t_impact:
    st.markdown("<div class='ict-requirement'><b>Criteria: Meaningful Community Benefits</b><br>Technical displacement of carbon fuels creates awareness for sustainable local energy.</div>", unsafe_allow_html=True)
    co2 = sum(gen_24) * 365 * 0.72 / 1000
    st.success(f"Yearly Offset: *{co2:.2f} Metric Tons* of CO2.")
    st.info(f"Equivalent Impact: *{int(co2 * 14)} trees* annually.")

with t_share:
    st.markdown("<div class='ict-requirement'><b>Criteria: Knowledge-Sharing for Seminars/Webinars</b><br>Technical parameters provided below serve as the foundation for educational briefings.</div>", unsafe_allow_html=True)
    st.write("#### Technical Seminar Points")
    st.write(f"- *Optimized Tilt:* {tilt}° provides peak irradiance at {c_lat}° latitude.")
    st.write(f"- *Azimuth Efficiency:* {angle_eff*100:.1f}% based on panel orientation.")
    st.write("- *System Resilience:* Modeled for multi-cycle climate fluctuations.")

with t_team:
    st.markdown("<div class='ict-requirement'><b>Criteria: Clear Evidence of Contribution & Ethics</b><br>Safe handling of user data and transparent project delegation.</div>", unsafe_allow_html=True)
    
    # Team Member Display
    st.write("#### Group Project Members")
    tm1, tm2, tm3, tm4 = st.columns(4)
    with tm1: st.markdown("<div class='team-card'><b>Ali Hussaan</b><br>Lead Logic</div>", unsafe_allow_html=True)
    with tm2: st.markdown("<div class='team-card'><b>Abdual Rehman Abbasi</b><br>Data Analysis</div>", unsafe_allow_html=True)
    with tm3: st.markdown("<div class='team-card'><b>Ali Sultan</b><br>System Architect</div>", unsafe_allow_html=True)
    with tm4: st.markdown("<div class='team-card'><b>Abdullah</b><br>UI Designer</div>", unsafe_allow_html=True)
    
    st.write("---")
    st.warning("🔐 *Ethics Statement:* This application ensures safe and ethical handling of information by utilizing client-side processing. No personal data is harvested or shared.")

# --- FOOTER ---
st.markdown("---")
st.caption("SolarX Omni-Ultimate v17 | ICT Project Evaluation Edition | Built for Mechanical Engineering Dept.")
# --- ICT EVALUATION TABS ---
t_ana, t_threat, t_impact, t_team = st.tabs([
    "🌪️ Mechanical Threat",
    "🌍 Community Impact", 
])

with t_threat:
    st.write("### Wind Uplift & Structural Integrity Analysis")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        # Radar Chart for Threat Profile
        threat_labels = ["Wind Lift", "Vibration", "Shear Stress", "Base Tension"]
        threat_vals = [wind_threat, wind_threat * 0.8, wind_threat * 0.6, wind_threat * 0.9]
        
        fig_threat = go.Figure(data=go.Scatterpolar(
            r=threat_vals + [threat_vals[0]],
            theta=threat_labels + [threat_labels[0]],
            fill='toself',
            line_color='#ef4444'
        ))
        fig_threat.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig_threat, use_container_width=True)
    
    with col_t2:
        st.markdown(f"**Structural Report for {country}:**")
        st.write(f"- **Regional Wind Speed:** {avg_wind} m/s")
        st.write(f"- **Current Lift Coeff:** {np.sin(np.radians(tilt)):.2f}")
        if wind_threat > 60:
            st.error("⚠️ CRITICAL RISK: Steep angle creates extreme uplift. Heavy-duty anchors required.")
        elif wind_threat > 30:
            st.warning("⚠️ MODERATE RISK: Potential for panel flutter. Reinforced framing recommended.")
        else:
            st.success("✅ LOW RISK: Aerodynamic configuration is stable.")

with t_impact:
    st.markdown("<div class='ict-requirement'><b>Criteria: Community awareness and CO2 reduction.</b></div>", unsafe_allow_html=True)
    co2 = sum(gen_24) * 365 * 0.72 / 1000
    st.success(f"Estimated Yearly Carbon Offset: **{co2:.2f} Metric Tons**.")
st.caption("SolarX Omni-Ultimate v17.2 | Structural Engineering Edition | Built for UET Taxila Dept.")
