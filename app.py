# ============================================================
# SOLAR POWER ESTIMATOR PRO ULTIMATE 2026
# PART 1 OF 6
# CORE SYSTEM
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import plotly.express as px
import math
import json
import time

from io import BytesIO
from datetime import datetime
from datetime import timedelta

# ============================================================
# OPTIONAL LIBRARIES
# ============================================================

try:
    from geopy.geocoders import Nominatim
    GEO_ENABLED = True
except:
    GEO_ENABLED = False

try:
    from fpdf import FPDF
    PDF_ENABLED = True
except:
    PDF_ENABLED = False

try:
    import openpyxl
    XLSX_ENABLED = True
except:
    XLSX_ENABLED = False

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Solar Power Estimator Pro Ultimate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION VARIABLES
# ============================================================

defaults = {

    "agreed":False,
    "weather_enabled":False,
    "forecast_loaded":False,
    "report_generated":False,
    "country":"Pakistan",
    "theme":"Dark"

}

for key,val in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = val

# ============================================================
# PREMIUM THEME
# ============================================================

st.markdown("""

<style>

html,
body,
[data-testid="stAppViewContainer"]{

background:#0f172a;
color:white;

}

.main-title{

font-size:48px;
font-weight:900;
text-align:center;
padding:15px;
margin-bottom:20px;

background:linear-gradient(
90deg,
#4f46e5,
#06b6d4
);

border-radius:20px;

}

.info-card{

background:#1e293b;

padding:20px;

border-radius:15px;

margin-bottom:10px;

border:1px solid #334155;

}

.metric-card{

background:#111827;

padding:15px;

border-radius:15px;

border-left:5px solid #3b82f6;

}

.footer{

text-align:center;

font-size:12px;

color:gray;

}

</style>

""",unsafe_allow_html=True)

# ============================================================
# TERMS AGREEMENT
# ============================================================

def agreement_dialog():

    @st.dialog(
        "Terms & Conditions"
    )

    def popup():

        st.markdown("""

### Solar Power Estimator Pro Ultimate

Before using this software:

✔ Engineering estimates only

✔ Weather APIs may contain delays

✔ Financial calculations are approximate

✔ Use certified engineers before installation

✔ No warranty implied

✔ Data may vary by country

""")

        c1,c2 = st.columns(2)

        with c1:

            if st.button(
                "Decline"
            ):

                st.stop()

        with c2:

            if st.button(
                "I Agree"
            ):

                st.session_state.agreed = True

                st.rerun()

    if not st.session_state.agreed:

        popup()

        st.stop()

agreement_dialog()

# ============================================================
# HEADER
# ============================================================

st.markdown("""

<div class='main-title'>

⚡ SOLAR POWER ESTIMATOR PRO ULTIMATE

</div>

""",unsafe_allow_html=True)

# ============================================================
# WEATHER ENGINE
# ============================================================

@st.cache_data(ttl=1800)

def get_live_weather(
    latitude,
    longitude
):

    try:

        url = (

            "https://api.open-meteo.com/v1/forecast"

            f"?latitude={latitude}"

            f"&longitude={longitude}"

            "&current="

            "temperature_2m,"

            "wind_speed_10m,"

            "cloud_cover"

            "&timezone=auto"

        )

        response = requests.get(
            url,
            timeout=20
        )

        data = response.json()

        current = data["current"]

        return {

            "temperature":
            current["temperature_2m"],

            "wind":
            current["wind_speed_10m"] * 3.6,

            "cloud":
            current["cloud_cover"]

        }

    except:

        return None

# ============================================================
# WEEKLY FORECAST
# ============================================================

@st.cache_data(ttl=1800)

def get_week_forecast(
    latitude,
    longitude
):

    try:

        url = (

            "https://api.open-meteo.com/v1/forecast"

            f"?latitude={latitude}"

            f"&longitude={longitude}"

            "&daily="

            "temperature_2m_max,"

            "temperature_2m_min,"

            "wind_speed_10m_max,"

            "cloud_cover_mean"

            "&timezone=auto"

        )

        response = requests.get(
            url,
            timeout=20
        )

        data = response.json()

        daily = data["daily"]

        results = []

        for i in range(7):

            results.append({

                "Date":
                daily["time"][i],

                "Temp Max":
                daily["temperature_2m_max"][i],

                "Temp Min":
                daily["temperature_2m_min"][i],

                "Wind":
                daily["wind_speed_10m_max"][i],

                "Cloud":
                daily["cloud_cover_mean"][i]

            })

        return results

    except:

        return []

# ============================================================
# GEOLOCATION ENGINE
# ============================================================

@st.cache_data(ttl=86400)

def get_country_location(
    country,
    fallback_lat
):

    if not GEO_ENABLED:

        return (
            fallback_lat,
            70,
            country
        )

    try:

        geo = Nominatim(
            user_agent=
            "solar_estimator"
        )

        location = geo.geocode(
            country
        )

        if location:

            return (

                location.latitude,

                location.longitude,

                location.address.split(",")[0]

            )

    except:

        pass

    return (
        fallback_lat,
        70,
        country
    )

# ============================================================
# PDF ENGINE
# ============================================================

def generate_pdf_report(
    report_data
):

    if not PDF_ENABLED:
        return None

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=10
    )

    pdf.cell(
        0,
        10,
        "Solar Report",
        ln=1
    )

    for k,v in report_data.items():

        text = f"{k}: {v}"

        text = (
            text
            .encode(
                "latin-1",
                "ignore"
            )
            .decode(
                "latin-1"
            )
        )

        pdf.cell(
            0,
            8,
            text,
            ln=1
        )

    result = pdf.output(
        dest="S"
    )

    if isinstance(
        result,
        str
    ):

        result = result.encode(
            "latin-1"
        )

    return result

# ============================================================
# EXCEL ENGINE
# ============================================================

def generate_excel(
    dataframe
):

    excel_file = BytesIO()

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False
        )

    return excel_file.getvalue()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe_round(x):

    try:
        return round(x,2)
    except:
        return 0

def percentage(
    value,
    total
):

    if total == 0:
        return 0

    return (
        value /
        total
    ) * 100

def clamp(
    value,
    min_val,
    max_val
):

    return max(
        min_val,
        min(
            value,
            max_val
        )
    )

# ============================================================
# END PART 1
# ============================================================
# ============================================================
# PART 2A
# COUNTRIES DATABASE (1-40)
# ============================================================

countries_db = {

"Pakistan":{
"Latitude":30.3,"Currency":"PKR","BuyRate":82,"SellRate":42,
"GHI":5.3,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"Extreme"
},

"India":{
"Latitude":20.5,"Currency":"INR","BuyRate":12.5,"SellRate":6.2,
"GHI":5.4,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"China":{
"Latitude":35.8,"Currency":"CNY","BuyRate":0.72,"SellRate":0.42,
"GHI":4.3,"Voltage":220,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"United States":{
"Latitude":37.0,"Currency":"USD","BuyRate":0.30,"SellRate":0.14,
"GHI":4.8,"Voltage":120,"Frequency":60,"WindSpeed":90,
"WindZone":"Extreme"
},

"Canada":{
"Latitude":56.1,"Currency":"CAD","BuyRate":0.24,"SellRate":0.08,
"GHI":3.7,"Voltage":120,"Frequency":60,"WindSpeed":80,
"WindZone":"Extreme"
},

"United Kingdom":{
"Latitude":55.3,"Currency":"GBP","BuyRate":0.58,"SellRate":0.22,
"GHI":2.8,"Voltage":230,"Frequency":50,"WindSpeed":80,
"WindZone":"Extreme"
},

"Germany":{
"Latitude":51.1,"Currency":"EUR","BuyRate":0.48,"SellRate":0.12,
"GHI":3.0,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"Extreme"
},

"France":{
"Latitude":46.2,"Currency":"EUR","BuyRate":0.34,"SellRate":0.15,
"GHI":3.5,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"High"
},

"Italy":{
"Latitude":41.8,"Currency":"EUR","BuyRate":0.50,"SellRate":0.20,
"GHI":4.2,"Voltage":230,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"Spain":{
"Latitude":40.4,"Currency":"EUR","BuyRate":0.45,"SellRate":0.22,
"GHI":4.6,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"Portugal":{
"Latitude":39.3,"Currency":"EUR","BuyRate":0.32,"SellRate":0.14,
"GHI":4.3,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"Extreme"
},

"Netherlands":{
"Latitude":52.1,"Currency":"EUR","BuyRate":0.55,"SellRate":0.16,
"GHI":2.8,"Voltage":230,"Frequency":50,"WindSpeed":85,
"WindZone":"Extreme"
},

"Belgium":{
"Latitude":50.5,"Currency":"EUR","BuyRate":0.52,"SellRate":0.12,
"GHI":2.9,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"High"
},

"Switzerland":{
"Latitude":46.8,"Currency":"CHF","BuyRate":0.45,"SellRate":0.20,
"GHI":3.4,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"High"
},

"Austria":{
"Latitude":47.5,"Currency":"EUR","BuyRate":0.45,"SellRate":0.15,
"GHI":3.4,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Norway":{
"Latitude":60.4,"Currency":"NOK","BuyRate":2.8,"SellRate":0.9,
"GHI":2.3,"Voltage":230,"Frequency":50,"WindSpeed":80,
"WindZone":"Extreme"
},

"Sweden":{
"Latitude":60.1,"Currency":"SEK","BuyRate":2.4,"SellRate":0.85,
"GHI":2.6,"Voltage":230,"Frequency":50,"WindSpeed":75,
"WindZone":"Extreme"
},

"Finland":{
"Latitude":61.9,"Currency":"EUR","BuyRate":0.38,"SellRate":0.08,
"GHI":2.5,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"Denmark":{
"Latitude":56.2,"Currency":"DKK","BuyRate":2.8,"SellRate":0.65,
"GHI":2.7,"Voltage":230,"Frequency":50,"WindSpeed":90,
"WindZone":"Extreme"
},

"Ireland":{
"Latitude":53.1,"Currency":"EUR","BuyRate":0.55,"SellRate":0.22,
"GHI":2.7,"Voltage":230,"Frequency":50,"WindSpeed":95,
"WindZone":"Extreme"
},

"Turkey":{
"Latitude":38.9,"Currency":"TRY","BuyRate":6.5,"SellRate":3.5,
"GHI":4.9,"Voltage":230,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"Iran":{
"Latitude":32.4,"Currency":"IRR","BuyRate":2000,"SellRate":800,
"GHI":5.6,"Voltage":220,"Frequency":50,"WindSpeed":70,
"WindZone":"Extreme"
},

"Iraq":{
"Latitude":33.2,"Currency":"IQD","BuyRate":160,"SellRate":70,
"GHI":5.8,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"Extreme"
},

"Saudi Arabia":{
"Latitude":23.8,"Currency":"SAR","BuyRate":0.32,"SellRate":0.15,
"GHI":6.1,"Voltage":220,"Frequency":60,"WindSpeed":65,
"WindZone":"Extreme"
},

"United Arab Emirates":{
"Latitude":23.4,"Currency":"AED","BuyRate":0.48,"SellRate":0.22,
"GHI":5.9,"Voltage":220,"Frequency":50,"WindSpeed":65,
"WindZone":"Extreme"
},

"Qatar":{
"Latitude":25.3,"Currency":"QAR","BuyRate":0.38,"SellRate":0.15,
"GHI":5.9,"Voltage":240,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"Kuwait":{
"Latitude":29.3,"Currency":"KWD","BuyRate":0.08,"SellRate":0.02,
"GHI":5.9,"Voltage":240,"Frequency":50,"WindSpeed":70,
"WindZone":"Extreme"
},

"Oman":{
"Latitude":21.5,"Currency":"OMR","BuyRate":0.12,"SellRate":0.03,
"GHI":6.0,"Voltage":240,"Frequency":50,"WindSpeed":65,
"WindZone":"Extreme"
},

"Jordan":{
"Latitude":30.5,"Currency":"JOD","BuyRate":0.18,"SellRate":0.08,
"GHI":5.8,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"Egypt":{
"Latitude":26.8,"Currency":"EGP","BuyRate":2.6,"SellRate":1.2,
"GHI":6.1,"Voltage":220,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"South Africa":{
"Latitude":-30.5,"Currency":"ZAR","BuyRate":3.8,"SellRate":1.9,
"GHI":5.7,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"Extreme"
},

"Nigeria":{
"Latitude":9.1,"Currency":"NGN","BuyRate":180,"SellRate":70,
"GHI":5.8,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Kenya":{
"Latitude":0.1,"Currency":"KES","BuyRate":35,"SellRate":15,
"GHI":5.9,"Voltage":240,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Ethiopia":{
"Latitude":9.1,"Currency":"ETB","BuyRate":4.2,"SellRate":1.5,
"GHI":5.7,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Morocco":{
"Latitude":31.8,"Currency":"MAD","BuyRate":1.8,"SellRate":0.7,
"GHI":5.5,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Algeria":{
"Latitude":28.0,"Currency":"DZD","BuyRate":5.5,"SellRate":2.0,
"GHI":6.0,"Voltage":230,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"Tunisia":{
"Latitude":34.0,"Currency":"TND","BuyRate":0.35,"SellRate":0.12,
"GHI":5.6,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"High"
},

"Libya":{
"Latitude":27.0,"Currency":"LYD","BuyRate":0.12,"SellRate":0.04,
"GHI":6.2,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Sudan":{
"Latitude":15.6,"Currency":"SDG","BuyRate":90,"SellRate":30,
"GHI":6.0,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
}

}
# ============================================================
# PART 2B
# COUNTRIES DATABASE (41-80)
# ============================================================

countries_db.update({

"Japan":{
"Latitude":36.2,"Currency":"JPY","BuyRate":31,"SellRate":12,
"GHI":3.8,"Voltage":100,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"South Korea":{
"Latitude":36.5,"Currency":"KRW","BuyRate":180,"SellRate":75,
"GHI":4.0,"Voltage":220,"Frequency":60,"WindSpeed":60,
"WindZone":"High"
},

"North Korea":{
"Latitude":40.3,"Currency":"KPW","BuyRate":120,"SellRate":45,
"GHI":4.1,"Voltage":220,"Frequency":50,"WindSpeed":50,
"WindZone":"Moderate"
},

"Australia":{
"Latitude":-25.0,"Currency":"AUD","BuyRate":0.38,"SellRate":0.12,
"GHI":5.8,"Voltage":230,"Frequency":50,"WindSpeed":75,
"WindZone":"Extreme"
},

"New Zealand":{
"Latitude":-41.0,"Currency":"NZD","BuyRate":0.34,"SellRate":0.10,
"GHI":4.2,"Voltage":230,"Frequency":50,"WindSpeed":85,
"WindZone":"Extreme"
},

"Russia":{
"Latitude":61.5,"Currency":"RUB","BuyRate":7.0,"SellRate":3.0,
"GHI":2.8,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Ukraine":{
"Latitude":49.0,"Currency":"UAH","BuyRate":7.5,"SellRate":3.2,
"GHI":3.4,"Voltage":230,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"Poland":{
"Latitude":52.0,"Currency":"PLN","BuyRate":1.3,"SellRate":0.5,
"GHI":3.2,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Czech Republic":{
"Latitude":49.8,"Currency":"CZK","BuyRate":6.2,"SellRate":2.4,
"GHI":3.1,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Slovakia":{
"Latitude":48.7,"Currency":"EUR","BuyRate":0.24,"SellRate":0.08,
"GHI":3.2,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Hungary":{
"Latitude":47.2,"Currency":"HUF","BuyRate":92,"SellRate":35,
"GHI":3.5,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Romania":{
"Latitude":45.9,"Currency":"RON","BuyRate":1.5,"SellRate":0.6,
"GHI":3.8,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Bulgaria":{
"Latitude":42.7,"Currency":"BGN","BuyRate":0.40,"SellRate":0.15,
"GHI":4.0,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Greece":{
"Latitude":39.1,"Currency":"EUR","BuyRate":0.32,"SellRate":0.14,
"GHI":4.8,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Croatia":{
"Latitude":45.1,"Currency":"EUR","BuyRate":0.28,"SellRate":0.10,
"GHI":4.1,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Serbia":{
"Latitude":44.0,"Currency":"RSD","BuyRate":18,"SellRate":7,
"GHI":4.0,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Bosnia and Herzegovina":{
"Latitude":44.2,"Currency":"BAM","BuyRate":0.36,"SellRate":0.14,
"GHI":3.9,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Slovenia":{
"Latitude":46.1,"Currency":"EUR","BuyRate":0.26,"SellRate":0.10,
"GHI":3.7,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Albania":{
"Latitude":41.1,"Currency":"ALL","BuyRate":11,"SellRate":4,
"GHI":4.7,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Brazil":{
"Latitude":-14.2,"Currency":"BRL","BuyRate":0.95,"SellRate":0.40,
"GHI":5.2,"Voltage":127,"Frequency":60,"WindSpeed":50,
"WindZone":"High"
},

"Argentina":{
"Latitude":-34.6,"Currency":"ARS","BuyRate":120,"SellRate":55,
"GHI":5.0,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Chile":{
"Latitude":-35.7,"Currency":"CLP","BuyRate":180,"SellRate":80,
"GHI":5.8,"Voltage":220,"Frequency":50,"WindSpeed":60,
"WindZone":"High"
},

"Peru":{
"Latitude":-9.2,"Currency":"PEN","BuyRate":0.85,"SellRate":0.35,
"GHI":5.4,"Voltage":220,"Frequency":60,"WindSpeed":40,
"WindZone":"Moderate"
},

"Colombia":{
"Latitude":4.5,"Currency":"COP","BuyRate":950,"SellRate":420,
"GHI":4.9,"Voltage":110,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Venezuela":{
"Latitude":7.0,"Currency":"VES","BuyRate":18,"SellRate":7,
"GHI":5.5,"Voltage":120,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Mexico":{
"Latitude":23.6,"Currency":"MXN","BuyRate":3.5,"SellRate":1.5,
"GHI":5.5,"Voltage":127,"Frequency":60,"WindSpeed":50,
"WindZone":"High"
},

"Guatemala":{
"Latitude":15.7,"Currency":"GTQ","BuyRate":1.7,"SellRate":0.7,
"GHI":5.2,"Voltage":120,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Costa Rica":{
"Latitude":9.9,"Currency":"CRC","BuyRate":120,"SellRate":45,
"GHI":4.8,"Voltage":120,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Panama":{
"Latitude":8.5,"Currency":"PAB","BuyRate":0.25,"SellRate":0.10,
"GHI":5.0,"Voltage":120,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Cuba":{
"Latitude":21.5,"Currency":"CUP","BuyRate":6.5,"SellRate":2.5,
"GHI":5.1,"Voltage":110,"Frequency":60,"WindSpeed":45,
"WindZone":"High"
},

"Dominican Republic":{
"Latitude":18.7,"Currency":"DOP","BuyRate":11,"SellRate":4,
"GHI":5.3,"Voltage":120,"Frequency":60,"WindSpeed":50,
"WindZone":"High"
},

"Jamaica":{
"Latitude":18.1,"Currency":"JMD","BuyRate":38,"SellRate":15,
"GHI":5.4,"Voltage":110,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Bahamas":{
"Latitude":25.0,"Currency":"BSD","BuyRate":0.32,"SellRate":0.12,
"GHI":5.5,"Voltage":120,"Frequency":60,"WindSpeed":70,
"WindZone":"Extreme"
},

"Indonesia":{
"Latitude":-2.5,"Currency":"IDR","BuyRate":2400,"SellRate":1000,
"GHI":4.8,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Malaysia":{
"Latitude":4.2,"Currency":"MYR","BuyRate":0.55,"SellRate":0.22,
"GHI":4.9,"Voltage":240,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Singapore":{
"Latitude":1.3,"Currency":"SGD","BuyRate":0.38,"SellRate":0.16,
"GHI":4.6,"Voltage":230,"Frequency":50,"WindSpeed":25,
"WindZone":"Low"
},

"Thailand":{
"Latitude":15.8,"Currency":"THB","BuyRate":4.8,"SellRate":2.0,
"GHI":5.1,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Vietnam":{
"Latitude":14.1,"Currency":"VND","BuyRate":3200,"SellRate":1300,
"GHI":4.8,"Voltage":220,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Philippines":{
"Latitude":12.8,"Currency":"PHP","BuyRate":12,"SellRate":5,
"GHI":5.0,"Voltage":220,"Frequency":60,"WindSpeed":65,
"WindZone":"Extreme"
}

})
# ============================================================
# PART 2C
# COUNTRIES DATABASE (81-120+)
# ============================================================

countries_db.update({

"Bangladesh":{
"Latitude":23.7,"Currency":"BDT","BuyRate":11.5,"SellRate":5.0,
"GHI":4.9,"Voltage":220,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Sri Lanka":{
"Latitude":7.8,"Currency":"LKR","BuyRate":55,"SellRate":25,
"GHI":5.2,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Nepal":{
"Latitude":28.4,"Currency":"NPR","BuyRate":13,"SellRate":6,
"GHI":5.1,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Afghanistan":{
"Latitude":33.9,"Currency":"AFN","BuyRate":8.5,"SellRate":3.5,
"GHI":5.7,"Voltage":220,"Frequency":50,"WindSpeed":45,
"WindZone":"High"
},

"Kazakhstan":{
"Latitude":48.0,"Currency":"KZT","BuyRate":22,"SellRate":10,
"GHI":4.2,"Voltage":220,"Frequency":50,"WindSpeed":70,
"WindZone":"Extreme"
},

"Uzbekistan":{
"Latitude":41.3,"Currency":"UZS","BuyRate":900,"SellRate":400,
"GHI":5.5,"Voltage":220,"Frequency":50,"WindSpeed":50,
"WindZone":"High"
},

"Turkmenistan":{
"Latitude":38.9,"Currency":"TMT","BuyRate":0.7,"SellRate":0.3,
"GHI":5.8,"Voltage":220,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Kyrgyzstan":{
"Latitude":41.2,"Currency":"KGS","BuyRate":3.5,"SellRate":1.5,
"GHI":5.0,"Voltage":220,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Tajikistan":{
"Latitude":38.8,"Currency":"TJS","BuyRate":0.9,"SellRate":0.4,
"GHI":5.3,"Voltage":220,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Azerbaijan":{
"Latitude":40.1,"Currency":"AZN","BuyRate":0.11,"SellRate":0.05,
"GHI":4.8,"Voltage":220,"Frequency":50,"WindSpeed":60,
"WindZone":"High"
},

"Armenia":{
"Latitude":40.2,"Currency":"AMD","BuyRate":45,"SellRate":18,
"GHI":4.9,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Georgia":{
"Latitude":42.0,"Currency":"GEL","BuyRate":0.28,"SellRate":0.12,
"GHI":4.5,"Voltage":220,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Mongolia":{
"Latitude":46.8,"Currency":"MNT","BuyRate":260,"SellRate":100,
"GHI":5.4,"Voltage":220,"Frequency":50,"WindSpeed":75,
"WindZone":"Extreme"
},

"Cambodia":{
"Latitude":12.5,"Currency":"KHR","BuyRate":1000,"SellRate":450,
"GHI":5.0,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Laos":{
"Latitude":19.8,"Currency":"LAK","BuyRate":1500,"SellRate":650,
"GHI":4.9,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Myanmar":{
"Latitude":21.9,"Currency":"MMK","BuyRate":210,"SellRate":90,
"GHI":5.1,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Brunei":{
"Latitude":4.5,"Currency":"BND","BuyRate":0.30,"SellRate":0.12,
"GHI":4.7,"Voltage":240,"Frequency":50,"WindSpeed":25,
"WindZone":"Low"
},

"Maldives":{
"Latitude":3.2,"Currency":"MVR","BuyRate":2.8,"SellRate":1.1,
"GHI":5.6,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"High"
},

"Iceland":{
"Latitude":64.9,"Currency":"ISK","BuyRate":24,"SellRate":9,
"GHI":2.0,"Voltage":230,"Frequency":50,"WindSpeed":95,
"WindZone":"Extreme"
},

"Luxembourg":{
"Latitude":49.8,"Currency":"EUR","BuyRate":0.30,"SellRate":0.12,
"GHI":3.0,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Estonia":{
"Latitude":58.6,"Currency":"EUR","BuyRate":0.25,"SellRate":0.10,
"GHI":2.7,"Voltage":230,"Frequency":50,"WindSpeed":60,
"WindZone":"High"
},

"Latvia":{
"Latitude":56.9,"Currency":"EUR","BuyRate":0.24,"SellRate":0.10,
"GHI":2.8,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Lithuania":{
"Latitude":55.2,"Currency":"EUR","BuyRate":0.24,"SellRate":0.10,
"GHI":2.9,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Belarus":{
"Latitude":53.7,"Currency":"BYN","BuyRate":0.22,"SellRate":0.09,
"GHI":3.0,"Voltage":230,"Frequency":50,"WindSpeed":45,
"WindZone":"Moderate"
},

"Moldova":{
"Latitude":47.4,"Currency":"MDL","BuyRate":3.0,"SellRate":1.2,
"GHI":3.8,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Uruguay":{
"Latitude":-32.5,"Currency":"UYU","BuyRate":8.5,"SellRate":3.5,
"GHI":4.8,"Voltage":230,"Frequency":50,"WindSpeed":55,
"WindZone":"High"
},

"Paraguay":{
"Latitude":-23.4,"Currency":"PYG","BuyRate":650,"SellRate":250,
"GHI":5.3,"Voltage":220,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Bolivia":{
"Latitude":-16.3,"Currency":"BOB","BuyRate":1.2,"SellRate":0.5,
"GHI":5.6,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Ecuador":{
"Latitude":-1.8,"Currency":"USD","BuyRate":0.18,"SellRate":0.08,
"GHI":4.9,"Voltage":120,"Frequency":60,"WindSpeed":30,
"WindZone":"Moderate"
},

"Guyana":{
"Latitude":5.0,"Currency":"GYD","BuyRate":42,"SellRate":18,
"GHI":5.2,"Voltage":240,"Frequency":60,"WindSpeed":35,
"WindZone":"Moderate"
},

"Suriname":{
"Latitude":4.1,"Currency":"SRD","BuyRate":6.0,"SellRate":2.4,
"GHI":5.1,"Voltage":127,"Frequency":60,"WindSpeed":30,
"WindZone":"Moderate"
},

"Namibia":{
"Latitude":-22.5,"Currency":"NAD","BuyRate":3.2,"SellRate":1.4,
"GHI":6.2,"Voltage":220,"Frequency":50,"WindSpeed":45,
"WindZone":"High"
},

"Botswana":{
"Latitude":-22.3,"Currency":"BWP","BuyRate":2.1,"SellRate":0.9,
"GHI":6.1,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
},

"Zimbabwe":{
"Latitude":-19.0,"Currency":"USD","BuyRate":0.16,"SellRate":0.06,
"GHI":5.8,"Voltage":220,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Zambia":{
"Latitude":-13.1,"Currency":"ZMW","BuyRate":3.5,"SellRate":1.5,
"GHI":5.7,"Voltage":230,"Frequency":50,"WindSpeed":35,
"WindZone":"Moderate"
},

"Uganda":{
"Latitude":1.3,"Currency":"UGX","BuyRate":850,"SellRate":350,
"GHI":5.4,"Voltage":240,"Frequency":50,"WindSpeed":25,
"WindZone":"Low"
},

"Tanzania":{
"Latitude":-6.3,"Currency":"TZS","BuyRate":320,"SellRate":120,
"GHI":5.6,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Ghana":{
"Latitude":7.9,"Currency":"GHS","BuyRate":2.1,"SellRate":0.9,
"GHI":5.5,"Voltage":230,"Frequency":50,"WindSpeed":30,
"WindZone":"Moderate"
},

"Cameroon":{
"Latitude":5.7,"Currency":"XAF","BuyRate":95,"SellRate":40,
"GHI":5.2,"Voltage":220,"Frequency":50,"WindSpeed":25,
"WindZone":"Low"
},

"Senegal":{
"Latitude":14.5,"Currency":"XOF","BuyRate":120,"SellRate":50,
"GHI":5.8,"Voltage":230,"Frequency":50,"WindSpeed":40,
"WindZone":"Moderate"
}

})
# ============================================================
# PART 3 OF 6
# COMPONENT DATABASES + SIDEBAR
# ============================================================

# ------------------------------------------------------------
# SOLAR PANELS DATABASE
# ------------------------------------------------------------

panel_db = {

    "Mono PERC 450W":[
        21.0,
        140,
        49.5,
        -0.35,
        45,
        11.2,
        "High efficiency"
    ],

    "Mono PERC 550W":[
        22.5,
        180,
        50.8,
        -0.34,
        55,
        13.2,
        "Utility scale"
    ],

    "TOPCon 600W":[
        23.2,
        240,
        52.4,
        -0.30,
        60,
        14.0,
        "Latest generation"
    ],

    "HJT 700W":[
        24.0,
        330,
        53.5,
        -0.26,
        70,
        15.1,
        "Premium performance"
    ]

}

# ------------------------------------------------------------
# BATTERY DATABASE
# ------------------------------------------------------------

battery_db = {

    "No Battery":[
        0,0,0,0,0,""
    ],

    "Lead Acid":[
        85,
        1200,
        120,
        4,
        48,
        "Budget option"
    ],

    "Lithium Iron Phosphate":[
        96,
        6500,
        350,
        1,
        48,
        "Recommended"
    ],

    "Lithium NMC":[
        94,
        5000,
        420,
        1.2,
        48,
        "High energy density"
    ]

}

# ------------------------------------------------------------
# INVERTER DATABASE
# ------------------------------------------------------------

inverter_db = {

    "String Inverter":[
        97,
        1.00,
        120,
        "Residential"
    ],

    "Hybrid Inverter":[
        98,
        1.05,
        180,
        "Battery compatible"
    ],

    "Micro Inverter":[
        96,
        1.08,
        250,
        "Best shading performance"
    ]

}

# ------------------------------------------------------------
# STRUCTURE DATABASE
# ------------------------------------------------------------

structure_db = {

    "Low":{
        "tilt_max":35,
        "type":"Light Duty"
    },

    "Moderate":{
        "tilt_max":40,
        "type":"Medium Duty"
    },

    "High":{
        "tilt_max":45,
        "type":"Heavy Duty"
    },

    "Extreme":{
        "tilt_max":50,
        "type":"Cyclone Rated"
    }

}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙ Solar Inputs")

    country = st.selectbox(
        "Country",
        sorted(countries_db.keys())
    )

    country_data = countries_db[country]

    st.divider()

    weather_enabled = st.toggle(
        "Use Live Weather",
        value=False
    )

    if weather_enabled:

        st.info(
            "Location permission required"
        )

    st.divider()

    panel_type = st.selectbox(
        "Solar Panel",
        list(panel_db.keys())
    )

    panel_qty = st.number_input(
        "Panel Quantity",
        min_value=1,
        max_value=5000,
        value=20
    )

    st.divider()

    inverter_type = st.selectbox(
        "Inverter",
        list(inverter_db.keys())
    )

    st.divider()

    battery_type = st.selectbox(
        "Battery",
        list(battery_db.keys())
    )

    if battery_type != "No Battery":

        battery_capacity = st.number_input(
            "Battery Capacity (kWh)",
            value=20.0
        )

        battery_dod = st.slider(
            "Battery DoD %",
            50,
            95,
            85
        )

    else:

        battery_capacity = 0
        battery_dod = 0

    st.divider()

    daily_load = st.number_input(
        "Daily Load (kWh)",
        value=50.0
    )

    st.divider()

    tilt = st.slider(
        "Tilt Angle",
        0,
        60,
        25
    )

    azimuth = st.slider(
        "Azimuth",
        -180,
        180,
        0
    )

    st.divider()

    tax_rate = st.slider(
        "Tax %",
        0,
        30,
        17
    )

# ============================================================
# COUNTRY VALUES
# ============================================================

lat = country_data["Latitude"]
currency = country_data["Currency"]
buy_rate = country_data["BuyRate"]
sell_rate = country_data["SellRate"]
ghi = country_data["GHI"]
grid_voltage = country_data["Voltage"]
grid_frequency = country_data["Frequency"]
wind_speed = country_data["WindSpeed"]
wind_zone = country_data["WindZone"]

# ============================================================
# LOCATION
# ============================================================

latitude, longitude, location_name = (
    get_country_location(
        country,
        lat
    )
)

# ============================================================
# WEATHER
# ============================================================

cloud = 20
temperature = 25

weekly_forecast = []

if weather_enabled:

    weather = get_live_weather(
        latitude,
        longitude
    )

    if weather:

        temperature = weather["temperature"]
        cloud = weather["cloud"]
        wind_speed = weather["wind"]

        weekly_forecast = get_week_forecast(
            latitude,
            longitude
        )

# ============================================================
# END PART 3
# ============================================================
# ============================================================
# PART 4 OF 6
# SOLAR CALCULATION ENGINE
# ============================================================

# ------------------------------------------------------------
# PANEL DATA
# ------------------------------------------------------------

panel_efficiency = panel_db[panel_type][0]
panel_cost = panel_db[panel_type][1]
panel_voc = panel_db[panel_type][2]
panel_temp_coeff = panel_db[panel_type][3]
panel_power = panel_db[panel_type][4]
panel_isc = panel_db[panel_type][5]

# ------------------------------------------------------------
# BATTERY DATA
# ------------------------------------------------------------

battery_eff = battery_db[battery_type][0]
battery_cycles = battery_db[battery_type][1]
battery_cost_per_kwh = battery_db[battery_type][2]

# ------------------------------------------------------------
# INVERTER DATA
# ------------------------------------------------------------

inv_eff = inverter_db[inverter_type][0]
inv_factor = inverter_db[inverter_type][1]
inv_cost_per_kw = inverter_db[inverter_type][2]

# ============================================================
# WEATHER CORRECTIONS
# ============================================================

cloud_factor = max(
    0.35,
    1 - (cloud / 100) * 0.55
)

temp_factor = max(
    0.70,
    1 - (
        (temperature - 25)
        *
        abs(panel_temp_coeff)
        / 100
    )
)

weather_factor = (
    cloud_factor
    *
    temp_factor
)

# ============================================================
# SOLAR ARRAY SIZE
# ============================================================

system_size_kw = (
    panel_qty
    *
    panel_power
) / 1000

# ============================================================
# DAILY GENERATION
# ============================================================

daily_generation = (

    system_size_kw

    *

    ghi

    *

    weather_factor

    *

    (inv_eff / 100)

)

# ============================================================
# ANNUAL GENERATION
# ============================================================

annual_generation = (
    daily_generation
    *
    365
)

# ============================================================
# WEEKLY OUTPUT FORECAST
# ============================================================

weekly_output = []

if weather_enabled and weekly_forecast:

    for day in weekly_forecast:

        c = day["Cloud"]

        cloud_adj = max(
            0.35,
            1 - (c / 100) * 0.55
        )

        gen = (
            system_size_kw
            *
            ghi
            *
            cloud_adj
            *
            (inv_eff / 100)
        )

        weekly_output.append({

            "Date":
            day["Date"],

            "Generation":
            round(gen,2)

        })

# ============================================================
# ENERGY BALANCE
# ============================================================

net_energy = (
    daily_generation
    -
    daily_load
)

coverage_percent = (

    daily_generation

    /

    max(
        daily_load,
        1
    )

) * 100

# ============================================================
# BATTERY ENGINE
# ============================================================

has_battery = (
    battery_type
    !=
    "No Battery"
)

usable_battery = 0

backup_hours = 0

if has_battery:

    usable_battery = (

        battery_capacity

        *

        (battery_dod / 100)

        *

        (battery_eff / 100)

    )

    backup_hours = (

        usable_battery

        /

        max(
            daily_load / 24,
            0.1
        )

    )

# ============================================================
# INVERTER SIZING
# ============================================================

recommended_inverter = (

    system_size_kw

    *

    inv_factor

)

# ============================================================
# STRING DESIGN
# ============================================================

panels_per_string = max(

    1,

    int(
        1000
        /
        panel_voc
    )

)

strings = max(

    1,

    math.ceil(
        panel_qty
        /
        panels_per_string
    )

)

voc_string = (
    panel_voc
    *
    panels_per_string
)

isc_string = (
    panel_isc
    *
    strings
)

mppt_voltage = (
    voc_string
    *
    0.82
)

# ============================================================
# WIND ANALYSIS
# ============================================================

wind_pressure = (

    0.613

    *

    (
        wind_speed
        /
        3.6
    ) ** 2

)

panel_area = (
    panel_qty
    *
    2.3
)

wind_force = (
    wind_pressure
    *
    panel_area
)

# ============================================================
# STRUCTURE TYPE
# ============================================================

if wind_zone in structure_db:

    structure_type = (
        structure_db
        [wind_zone]
        ["type"]
    )

else:

    structure_type = (
        "Standard"
    )

# ============================================================
# CARBON SAVINGS
# ============================================================

co2_factor = 0.45

annual_co2_saved = (

    annual_generation

    *

    co2_factor

) / 1000

trees_equivalent = (
    annual_co2_saved
    *
    45
)

# ============================================================
# NET METERING
# ============================================================

surplus_daily = max(
    0,
    daily_generation - daily_load
)

surplus_annual = (
    surplus_daily
    *
    365
)

annual_export_income = (

    surplus_annual

    *

    sell_rate

)

# ============================================================
# FINANCIAL ENGINE
# ============================================================

panel_cost_total = (
    panel_qty
    *
    panel_cost
)

battery_cost_total = (

    battery_capacity

    *

    battery_cost_per_kwh

)

inverter_cost_total = (

    recommended_inverter

    *

    inv_cost_per_kw

)

subtotal = (

    panel_cost_total

    +

    battery_cost_total

    +

    inverter_cost_total

)

tax_amount = (
    subtotal
    *
    tax_rate
    / 100
)

total_cost = (
    subtotal
    +
    tax_amount
)

annual_savings = (

    min(
        daily_generation,
        daily_load
    )

    *

    365

    *

    buy_rate

)

annual_profit = (

    annual_savings

    +

    annual_export_income

)

if annual_profit > 0:

    payback_years = (
        total_cost
        /
        annual_profit
    )

else:

    payback_years = 999

# ============================================================
# AI SYSTEM SCORE
# ============================================================

score = 100

if coverage_percent < 100:
    score -= 20

if cloud > 70:
    score -= 10

if payback_years > 8:
    score -= 15

if wind_speed > 80:
    score -= 5

system_score = max(
    0,
    min(
        100,
        round(score)
    )
)

# ============================================================
# RECOMMENDATIONS
# ============================================================

recommendations = []

if coverage_percent < 100:

    recommendations.append(
        "Increase solar panel quantity."
    )

if payback_years > 8:

    recommendations.append(
        "Reduce system cost or improve self-consumption."
    )

if wind_speed > 80:

    recommendations.append(
        "Use cyclone-rated mounting structure."
    )

if battery_type == "No Battery":

    recommendations.append(
        "Battery backup recommended."
    )

if not recommendations:

    recommendations.append(
        "System configuration looks good."
    )

# ============================================================
# END PART 4
# ============================================================
# ============================================================
# ============================================================
# PART 5 OF 6
# ADVANCED FINANCIAL ENGINE
# ============================================================

# ------------------------------------------------------------
# PROJECT LIFE
# ------------------------------------------------------------

project_life = 25

panel_degradation = 0.55

discount_rate = 8.0

inflation_rate = 5.0

electricity_growth = 4.0

# ============================================================
# YEARLY FORECAST
# ============================================================

yearly_forecast = []

current_generation = annual_generation

for year in range(1, project_life + 1):

    degradation_factor = (

        1
        -
        (
            panel_degradation
            / 100
            * year
        )

    )

    degradation_factor = max(
        0.75,
        degradation_factor
    )

    yearly_energy = (
        annual_generation
        *
        degradation_factor
    )

    future_buy_rate = (

        buy_rate

        *

        (
            1
            +
            electricity_growth
            / 100
        ) ** year

    )

    yearly_saving = (
        yearly_energy
        *
        future_buy_rate
    )

    yearly_forecast.append({

        "Year":year,
        "Energy":round(yearly_energy,2),
        "Tariff":round(future_buy_rate,4),
        "Saving":round(yearly_saving,2)

    })

# ============================================================
# NPV
# ============================================================

npv = -total_cost

for row in yearly_forecast:

    cashflow = row["Saving"]

    npv += (

        cashflow

        /

        (
            (
                1
                +
                discount_rate
                / 100
            )
            **
            row["Year"]
        )

    )

# ============================================================
# ROI
# ============================================================

total_lifetime_profit = 0

for row in yearly_forecast:

    total_lifetime_profit += row["Saving"]

roi = (

    (
        total_lifetime_profit
        -
        total_cost
    )

    /

    max(
        total_cost,
        1
    )

) * 100

# ============================================================
# SIMPLE IRR ESTIMATION
# ============================================================

irr = 0

if total_cost > 0:

    irr = (

        annual_profit

        /

        total_cost

    ) * 100

# ============================================================
# MONTHLY GENERATION MODEL
# ============================================================

monthly_factors = {

    "Jan":0.75,
    "Feb":0.82,
    "Mar":0.93,
    "Apr":1.02,
    "May":1.10,
    "Jun":1.15,
    "Jul":1.08,
    "Aug":1.04,
    "Sep":0.97,
    "Oct":0.90,
    "Nov":0.80,
    "Dec":0.72

}

monthly_generation = []

for month,factor in monthly_factors.items():

    monthly_generation.append({

        "Month":month,

        "Generation":

        round(
            annual_generation
            / 12
            *
            factor,
            2
        )

    })

# ============================================================
# WEATHER RISK SCORE
# ============================================================

weather_risk = 0

if cloud > 70:
    weather_risk += 25

elif cloud > 50:
    weather_risk += 15

if wind_speed > 80:
    weather_risk += 25

elif wind_speed > 60:
    weather_risk += 15

if temperature > 45:
    weather_risk += 15

weather_risk = min(
    weather_risk,
    100
)

# ============================================================
# PERFORMANCE RATIO
# ============================================================

performance_ratio = (

    daily_generation

    /

    max(
        system_size_kw
        *
        ghi,
        1
    )

) * 100

performance_ratio = round(
    performance_ratio,
    2
)

# ============================================================
# MAINTENANCE PLAN
# ============================================================

maintenance_schedule = [

    {
        "Task":"Panel Cleaning",
        "Frequency":"Monthly"
    },

    {
        "Task":"Cable Inspection",
        "Frequency":"Quarterly"
    },

    {
        "Task":"Inverter Check",
        "Frequency":"6 Months"
    },

    {
        "Task":"Structure Inspection",
        "Frequency":"Yearly"
    },

    {
        "Task":"Performance Audit",
        "Frequency":"Yearly"
    }

]

# ============================================================
# AI RECOMMENDATION ENGINE PRO
# ============================================================

ai_advice = []

if performance_ratio < 75:

    ai_advice.append(
        "Low performance ratio detected."
    )

if weather_risk > 50:

    ai_advice.append(
        "High weather risk environment."
    )

if payback_years > 7:

    ai_advice.append(
        "Improve self-consumption for faster payback."
    )

if annual_co2_saved > 5:

    ai_advice.append(
        "Excellent environmental impact."
    )

if backup_hours < 6 and has_battery:

    ai_advice.append(
        "Battery capacity may be insufficient."
    )

if system_score > 90:

    ai_advice.append(
        "System health is excellent."
    )

if len(ai_advice) == 0:

    ai_advice.append(
        "Configuration appears balanced."
    )

# ============================================================
# ENERGY SECURITY SCORE
# ============================================================

energy_security_score = 50

if coverage_percent >= 100:
    energy_security_score += 25

if has_battery:
    energy_security_score += 15

if backup_hours > 12:
    energy_security_score += 10

energy_security_score = min(
    energy_security_score,
    100
)

# ============================================================
# ESG SCORE
# ============================================================

esg_score = round(

    (
        system_score
        +
        energy_security_score
        +
        min(
            annual_co2_saved * 5,
            100
        )
    )

    / 3,

    1

)

if esg_score >= 85:
    esg_rating = "AAA"

elif esg_score >= 70:
    esg_rating = "AA"

elif esg_score >= 55:
    esg_rating = "A"

else:
    esg_rating = "BBB"

# ============================================================
# LIFETIME ENERGY
# ============================================================

lifetime_energy = 0

for row in yearly_forecast:

    lifetime_energy += row["Energy"]

# ============================================================
# SYSTEM HEALTH INDEX
# ============================================================

health_index = round(

    (
        performance_ratio
        +
        system_score
    ) / 2,

    1

)

# ============================================================
# SMART ALERTS
# ============================================================

alerts = []

if weather_risk > 50:

    alerts.append(
        "⚠ Severe weather conditions detected."
    )

if coverage_percent < 100:

    alerts.append(
        "⚠ Solar generation below load demand."
    )

if payback_years > 10:

    alerts.append(
        "⚠ Long payback period."
    )

if health_index < 70:

    alerts.append(
        "⚠ System health requires attention."
    )

# ============================================================
# PART 5 END
# ============================================================
# ============================================================
# PART 6 OF 6
# EXECUTIVE DASHBOARD
# ============================================================

st.markdown("---")

# ============================================================
# HEADER CARD
# ============================================================

st.markdown(
f"""
<div class='info-card'>
<h2>Solar Power Estimator Pro Ultimate</h2>
<b>Country:</b> {country}<br>
<b>Currency:</b> {currency}<br>
<b>Grid:</b> {grid_voltage}V / {grid_frequency}Hz<br>
<b>ESG Rating:</b> {esg_rating}
</div>
""",
unsafe_allow_html=True
)

# ============================================================
# KPI SECTION
# ============================================================

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.metric(
        "Daily Generation",
        f"{daily_generation:.2f} kWh"
    )

with k2:
    st.metric(
        "Annual Generation",
        f"{annual_generation:,.0f} kWh"
    )

with k3:
    st.metric(
        "Annual Profit",
        f"{annual_profit:,.0f} {currency}"
    )

with k4:
    st.metric(
        "Payback",
        f"{payback_years:.1f} Years"
    )

# ============================================================
# TABS
# ============================================================

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([

    "Summary",
    "Weather",
    "Technical",
    "Financial",
    "AI Insights",
    "Export"

])

# ============================================================
# SUMMARY TAB
# ============================================================

with tab1:

    st.subheader("System Summary")

    c1,c2 = st.columns(2)

    with c1:

        st.info(
            f"System Size: {system_size_kw:.2f} kW"
        )

        st.info(
            f"Panel Quantity: {panel_qty}"
        )

        st.info(
            f"Panel Type: {panel_type}"
        )

        st.info(
            f"Inverter: {inverter_type}"
        )

    with c2:

        st.info(
            f"Battery: {battery_type}"
        )

        st.info(
            f"Coverage: {coverage_percent:.1f}%"
        )

        st.info(
            f"System Score: {system_score}"
        )

        st.info(
            f"Health Index: {health_index}"
        )

    # Energy Chart

    energy_fig = go.Figure()

    energy_fig.add_bar(
        name="Generation",
        x=["Daily"],
        y=[daily_generation]
    )

    energy_fig.add_bar(
        name="Load",
        x=["Daily"],
        y=[daily_load]
    )

    st.plotly_chart(
        energy_fig,
        use_container_width=True
    )

# ============================================================
# WEATHER TAB
# ============================================================

with tab2:

    st.subheader("Weather Overview")

    w1,w2,w3 = st.columns(3)

    with w1:
        st.metric(
            "Temperature",
            f"{temperature:.1f} °C"
        )

    with w2:
        st.metric(
            "Cloud",
            f"{cloud:.0f}%"
        )

    with w3:
        st.metric(
            "Wind",
            f"{wind_speed:.1f} km/h"
        )

    if weekly_forecast:

        st.subheader(
            "7 Day Forecast"
        )

        forecast_df = pd.DataFrame(
            weekly_forecast
        )

        st.dataframe(
            forecast_df,
            use_container_width=True
        )

# ============================================================
# TECHNICAL TAB
# ============================================================

with tab3:

    technical_df = pd.DataFrame({

        "Parameter":[
            "System Size",
            "Strings",
            "Panels/String",
            "String Voc",
            "String Isc",
            "MPPT Voltage",
            "Wind Force",
            "Structure"
        ],

        "Value":[
            f"{system_size_kw:.2f} kW",
            strings,
            panels_per_string,
            f"{voc_string:.1f} V",
            f"{isc_string:.1f} A",
            f"{mppt_voltage:.1f} V",
            f"{wind_force:.1f} N",
            structure_type
        ]

    })

    st.dataframe(
        technical_df,
        use_container_width=True
    )

    if has_battery:

        st.success(
            f"Usable Battery: {usable_battery:.2f} kWh"
        )

        st.success(
            f"Backup Hours: {backup_hours:.1f}"
        )

# ============================================================
# FINANCIAL TAB
# ============================================================

with tab4:

    st.subheader(
        "Financial Analysis"
    )

    finance_df = pd.DataFrame({

        "Metric":[
            "Total Cost",
            "Annual Profit",
            "ROI",
            "NPV",
            "IRR",
            "Payback"
        ],

        "Value":[
            round(total_cost,2),
            round(annual_profit,2),
            round(roi,2),
            round(npv,2),
            round(irr,2),
            round(payback_years,2)
        ]

    })

    st.dataframe(
        finance_df,
        use_container_width=True
    )

    pie = go.Figure()

    pie.add_pie(

        labels=[
            "Panels",
            "Battery",
            "Inverter"
        ],

        values=[
            panel_cost_total,
            battery_cost_total,
            inverter_cost_total
        ]

    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )

# ============================================================
# AI TAB
# ============================================================

with tab5:

    st.subheader(
        "AI Recommendations"
    )

    for item in ai_advice:

        st.success(item)

    st.subheader(
        "Smart Alerts"
    )

    if alerts:

        for alert in alerts:

            st.warning(alert)

    else:

        st.success(
            "No alerts detected."
        )

    st.subheader(
        "Maintenance Schedule"
    )

    maintenance_df = pd.DataFrame(
        maintenance_schedule
    )

    st.dataframe(
        maintenance_df,
        use_container_width=True
    )

# ============================================================
# EXPORT TAB
# ============================================================

with tab6:

    st.subheader(
        "Export Reports"
    )

    report_data = {

        "Country":country,
        "System Size":system_size_kw,
        "Daily Generation":daily_generation,
        "Annual Generation":annual_generation,
        "Annual Profit":annual_profit,
        "ROI":roi,
        "NPV":npv,
        "IRR":irr,
        "Payback":payback_years,
        "ESG":esg_rating

    }

    pdf_file = generate_pdf_report(
        report_data
    )

    if pdf_file:

        st.download_button(

            "Download PDF",

            pdf_file,

            file_name=
            "solar_report.pdf",

            mime=
            "application/pdf"

        )

    export_df = pd.DataFrame(
        [report_data]
    )

    excel_file = generate_excel(
        export_df
    )

    st.download_button(

        "Download Excel",

        excel_file,

        file_name=
        "solar_report.xlsx",

        mime=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

# ============================================================
# MONTHLY CHART
# ============================================================

st.subheader(
    "Monthly Generation Forecast"
)

monthly_df = pd.DataFrame(
    monthly_generation
)

monthly_chart = px.bar(

    monthly_df,

    x="Month",

    y="Generation"

)

st.plotly_chart(
    monthly_chart,
    use_container_width=True
)

# ============================================================
# LIFETIME CHART
# ============================================================

st.subheader(
    "25 Year Energy Forecast"
)

forecast_df = pd.DataFrame(
    yearly_forecast
)

life_chart = px.line(

    forecast_df,

    x="Year",

    y="Energy"

)

st.plotly_chart(
    life_chart,
    use_container_width=True
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
f"""
<div class='footer'>

Solar Power Estimator Pro Ultimate 2026

Country: {country}

ESG Rating: {esg_rating}

Lifetime Energy:
{lifetime_energy:,.0f} kWh

CO₂ Saved:
{annual_co2_saved:.2f} Tons / Year

</div>
""",
unsafe_allow_html=True
)

# ============================================================
# END OF PROJECT
# ============================================================
