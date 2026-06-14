import streamlit as st
import pandas as pd
import qrcode
import plotly.express as px
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Mahindra University Smart Parking",
    layout="wide"
)

st.title("🏫 Mahindra University Smart Parking System")

# ---------------- SESSION STATE ----------------
if "reservations" not in st.session_state:
    st.session_state.reservations = []

# ---------------- NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["🗺️ Map View", "🅿️ Reservation System", "📊 Analytics Dashboard"]
)

# ---------------- ZONES DATA ----------------
zones = [
    {"name": "Faculty Zone", "color": "green", "occupancy": 80},
    {"name": "Student Zone", "color": "blue", "occupancy": 60},
    {"name": "Visitor Zone", "color": "orange", "occupancy": 40},
]

# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.subheader("Campus Parking Zone Overview")

    st.markdown("""
    ### 🧭 Zone Legend
    🟢 Faculty Zone → Priority Parking  
    🔵 Student Zone → Regular Parking  
    🟠 Visitor Zone → Temporary Parking  
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"{zones[0]['name']}\n{zones[0]['occupancy']}% Occupied")

    with col2:
        st.info(f"{zones[1]['name']}\n{zones[1]['occupancy']}% Occupied")

    with col3:
        st.warning(f"{zones[2]['name']}\n{zones[2]['occupancy']}% Occupied")

    st.divider()

    st.subheader("📍 Campus Map (Simulation View)")

    map_data = pd.DataFrame({
        "lat": [17.543, 17.544, 17.542, 17.5435],
        "lon": [78.572, 78.573, 78.571, 78.5725]
    })

    st.map(map_data)

    st.info("Click zones (future upgrade: interactive polygon map with Leaflet)")

# ======================================================
# 🅿️ RESERVATION SYSTEM
# ======================================================
elif page == "🅿️ Reservation System":

    st.subheader("Reserve Your Parking Slot")

    st.markdown("Fill in details below to reserve a parking slot")

    vehicle = st.text_input("🚗 Vehicle Number (e.g., AP09AB1234)")

    zone = st.selectbox(
        "📍 Select Parking Zone",
        [z["name"] for z in zones]
    )

    time_slot = st.time_input("⏰ Select Time Slot")

    faculty_priority = st.checkbox("Faculty Priority Access")

    if st.button("🚀 Reserve Parking Slot"):

        if vehicle.strip() == "":
            st.error("Vehicle number is required")
        else:
            reservation = {
                "vehicle": vehicle,
                "zone": zone,
                "time": str(time_slot),
                "priority": "Faculty" if faculty_priority else "Normal"
            }

            st.session_state.reservations.append(reservation)

            # ---------------- QR GENERATION (SAFE) ----------------
            qr_data = str(reservation)
            qr_img = qrcode.make(qr_data)

            st.success("✅ Parking Reserved Successfully!")

            st.markdown("### 🎟️ Your Entry QR Code")
            st.image(qr_img, caption="Scan at Entry Gate")

            st.json(reservation)

    st.divider()

    st.subheader("📋 Recent Reservations")

    if st.session_state.reservations:
        st.dataframe(pd.DataFrame(st.session_state.reservations))
    else:
        st.info("No reservations yet")

# ======================================================
# 📊 ANALYTICS DASHBOARD
# ======================================================
elif page == "📊 Analytics Dashboard":

    st.subheader("Parking Usage Analytics")

    if len(st.session_state.reservations) == 0:
        st.warning("No data available yet")
    else:

        df = pd.DataFrame(st.session_state.reservations)

        st.dataframe(df)

        st.divider()

        # ---------------- ZONE ANALYSIS ----------------
        zone_count = df["zone"].value_counts().reset_index()
        zone_count.columns = ["Zone", "Count"]

        fig1 = px.bar(
            zone_count,
            x="Zone",
            y="Count",
            title="Zone-wise Reservations"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---------------- PRIORITY ANALYSIS ----------------
        priority_count = df["priority"].value_counts().reset_index()
        priority_count.columns = ["Priority", "Count"]

        fig2 = px.pie(
            priority_count,
            names="Priority",
            values="Count",
            title="Faculty vs Normal Usage"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---------------- METRICS ----------------
        st.metric("Total Reservations", len(df))
        st.metric("Most Used Zone", df["zone"].mode()[0])