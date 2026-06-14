import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(
    page_title="Park+ Smart Campus Parking",
    page_icon="🚗",
    layout="wide"
)

# ---------------------------------
# SIDEBAR
# ---------------------------------
st.sidebar.title("🚗 Park+")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Reservation",
        "Live Parking",
        "AI Prediction",
        "Notifications",
        "Admin Dashboard"
    ]
)

# ---------------------------------
# SAMPLE DATA
# ---------------------------------
TOTAL_SLOTS = 500
OCCUPIED = random.randint(250, 420)
AVAILABLE = TOTAL_SLOTS - OCCUPIED
FACULTY_RESERVED = 50

# ---------------------------------
# DASHBOARD
# ---------------------------------
if page == "Dashboard":

    st.title("🚗 Smart Campus Parking System")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Available Slots", AVAILABLE)
    col2.metric("Occupied Slots", OCCUPIED)
    col3.metric("Faculty Reserved", FACULTY_RESERVED)
    col4.metric("EV Slots", 20)

    st.divider()

    st.subheader("📈 Occupancy Analytics")

    chart_data = pd.DataFrame({
        "Hour":[8,9,10,11,12,1,2,3,4,5],
        "Occupancy":[45,60,75,85,90,88,80,72,60,50]
    })

    st.line_chart(
        chart_data.set_index("Hour")
    )

    st.subheader("💡 Smart Suggestions")

    st.success(
        "Zone D currently has the highest availability."
    )

# ---------------------------------
# RESERVATION
# ---------------------------------
elif page == "Reservation":

    st.title("🎟️ Parking Reservation")

    vehicle = st.text_input("Vehicle Number")

    zone = st.selectbox(
        "Select Zone",
        ["Zone A","Zone B","Zone C","Zone D","Zone E"]
    )

    slot_time = st.selectbox(
        "Time Slot",
        [
            "8-10 AM",
            "10-12 PM",
            "12-2 PM",
            "2-4 PM"
        ]
    )

    if st.button("Reserve Slot"):
        st.success(
            f"Parking reserved in {zone}"
        )

        st.info(
            f"QR Pass Generated for {vehicle}"
        )

# ---------------------------------
# LIVE PARKING
# ---------------------------------
elif page == "Live Parking":

    st.title("🅿️ Live Parking Availability")

    zones = {
        "Zone A Faculty": "🟢 Available",
        "Zone B Students": "🟡 Moderate",
        "Zone C Hostel": "🔴 Full",
        "Zone D Visitors": "🟢 Available",
        "Zone E EV": "🟢 Available"
    }

    for z,v in zones.items():
        st.write(f"**{z}** : {v}")

# ---------------------------------
# AI PREDICTION
# ---------------------------------
elif page == "AI Prediction":

    st.title("🤖 AI Parking Prediction")

    hour = st.slider(
        "Arrival Hour",
        8,
        18,
        10
    )

    prediction = min(
        100,
        40 + (hour*4)
    )

    st.metric(
        "Predicted Occupancy",
        f"{prediction}%"
    )

    if prediction > 85:
        st.error(
            "High Congestion Expected"
        )
    elif prediction > 65:
        st.warning(
            "Moderate Demand"
        )
    else:
        st.success(
            "Parking Available"
        )

# ---------------------------------
# NOTIFICATIONS
# ---------------------------------
elif page == "Notifications":

    st.title("🔔 Notifications")

    st.warning(
        "Zone C is currently full."
    )

    st.info(
        "Placement Drive on Friday."
    )

    st.success(
        "Reserved slot confirmed."
    )

# ---------------------------------
# ADMIN
# ---------------------------------
elif page == "Admin Dashboard":

    st.title("🛠️ Admin Dashboard")

    st.metric(
        "Total Vehicles Today",
        742
    )

    st.metric(
        "Peak Occupancy",
        "92%"
    )

    event_mode = st.toggle(
        "Event Parking Mode"
    )

    if event_mode:
        st.error(
            "Event Mode Activated"
        )

    st.subheader("Parking Zone Status")

    df = pd.DataFrame({
        "Zone":["A","B","C","D","E"],
        "Status":[
            "Available",
            "Moderate",
            "Full",
            "Available",
            "Available"
        ]
    })

    st.dataframe(df)
