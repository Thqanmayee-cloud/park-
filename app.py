import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import numpy as np
import folium
from streamlit_folium import st_folium
import cv2

# ================= CONFIG =================
st.set_page_config(
    page_title="ParkSmart | Mahindra University",
    layout="wide"
)

# ================= LOGO =================
col1, col2 = st.columns([1, 6])

with col1:
    st.image("assets/mu_logo.png", width=80)

with col2:
    st.title("🏫 Mahindra University")
    st.subheader("ParkSmart – SaaS Smart Parking System")

st.markdown("---")

# ================= SESSION =================
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "events" not in st.session_state:
    st.session_state.events = [
        {"name": "Tech Fest", "slots": 50, "booked": 10},
        {"name": "Convocation", "slots": 80, "booked": 20},
    ]

# ================= ROLES =================
role = st.sidebar.selectbox("Role", ["Student", "Faculty", "Admin"])

page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Live Map", "🅿️ Parking", "🎉 Events", "📷 QR Scanner", "📊 AI Dashboard"]
)

# ================= AI ZONE =================
def predict_zone_load():
    return np.random.randint(50, 95, 3)

# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ======================================================
# 🗺️ REAL MAP (FOLIUM)
# ======================================================
if page == "🗺️ Live Map":

    st.title("🗺️ Campus Live Parking Map")

    m = folium.Map(location=[17.54, 78.57], zoom_start=16)

    folium.Marker([17.540, 78.570], popup="Zone A Faculty").add_to(m)
    folium.Marker([17.542, 78.572], popup="Zone B Students").add_to(m)
    folium.Marker([17.544, 78.574], popup="Zone C Visitors").add_to(m)

    st_folium(m, width=900, height=500)

# ======================================================
# 🅿️ PARKING
# ======================================================
elif page == "🅿️ Parking":

    st.title("🅿️ Smart Parking")

    vehicle = st.text_input("Vehicle Number")

    zone = st.selectbox("Zone", ["A", "B", "C"])

    if st.button("Reserve Slot"):

        pid = "PSMART+" + hashlib.md5(
            (vehicle + str(datetime.now())).encode()
        ).hexdigest()[:10].upper()

        st.session_state.bookings.append({
            "Vehicle": vehicle,
            "Zone": zone,
            "Time": datetime.now().strftime("%H:%M:%S")
        })

        qr = make_qr(pid)

        st.success("Booked Successfully")
        st.image(qr)
        st.code(pid)

# ======================================================
# 🎉 EVENTS
# ======================================================
elif page == "🎉 Events":

    st.title("🎉 Event Parking System")

    event = st.selectbox("Select Event", [e["name"] for e in st.session_state.events])
    vehicle = st.text_input("Vehicle")

    selected = next(e for e in st.session_state.events if e["name"] == event)

    st.info(f"Slots left: {selected['slots'] - selected['booked']}")

    if st.button("Book Event Parking"):

        if selected["booked"] < selected["slots"]:
            selected["booked"] += 1

            st.session_state.bookings.append({
                "Vehicle": vehicle,
                "Zone": f"Event-{event}",
                "Time": str(datetime.now())
            })

            st.success("Event Booked")

# ======================================================
# 📷 QR SCANNER (SIMULATED)
# ======================================================
elif page == "📷 QR Scanner":

    st.title("📷 QR Scanner (Simulation)")

    code = st.text_input("Enter QR ID")

    if st.button("Scan"):

        if "PSMART" in code or "EVENT" in code:
            st.success("Access Granted")
        else:
            st.error("Invalid QR")

# ======================================================
# 📊 AI DASHBOARD
# ======================================================
elif page == "📊 AI Dashboard":

    st.title("📊 Smart Analytics Dashboard")

    loads = predict_zone_load()

    st.write("Zone Load Prediction (%)")

    st.bar_chart(pd.DataFrame({
        "Zone A": [loads[0]],
        "Zone B": [loads[1]],
        "Zone C": [loads[2]]
    }))

    st.subheader("Recent Bookings")

    if st.session_state.bookings:
        st.dataframe(pd.DataFrame(st.session_state.bookings))