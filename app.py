import streamlit as st
import random
import time
from datetime import datetime
import hashlib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

# ---------------- PREMIUM UI THEME ----------------
st.markdown("""
<style>

.main {
    background-color: #0b1220;
    color: #e5e7eb;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #1f2937;
}

.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #1d4ed8;
}

h1, h2, h3 {
    color: #60a5fa;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "passes" not in st.session_state:
    st.session_state.passes = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "active_pass" not in st.session_state:
    st.session_state.active_pass = None

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False


# ---------------- BASE SYSTEM DATA ----------------
TOTAL = 500

base_occupied = random.randint(280, 420)
event_factor = 1.4 if st.session_state.event_mode else 1.0

occupied = min(int(base_occupied * event_factor), TOTAL)
available = TOTAL - occupied

zones = {
    "Zone A (Faculty)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Hostel)": random.randint(30, 85),
    "Zone D (Visitors)": random.randint(20, 70),
}

# ---------------- SIDEBAR NAV ----------------
st.sidebar.title("🅿️ Smart Parking AI")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "AI Engine", "Live Zones", "Smart Park", "My Pass"]
)

st.sidebar.divider()
st.sidebar.caption("Mahindra University • Smart Infrastructure System")


# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🏢 Campus Control Center")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Slots", TOTAL)
    col2.metric("Occupied", occupied)
    col3.metric("Available", available)
    col4.metric("Occupancy %", f"{round((occupied/TOTAL)*100,2)}%")

    st.divider()

    st.subheader("🎯 Event Mode")

    toggle = st.toggle("Enable Event Mode")

    st.session_state.event_mode = toggle

    if toggle:
        st.warning("Event Mode Active → Demand Surge Simulation ON")
    else:
        st.info("Normal Operations")


# ---------------- AI ENGINE ----------------
elif page == "AI Engine":

    st.title("🧠 Predictive AI Engine")

    hour = st.slider("Select Time", 8, 20, 10)

    trend = (hour - 8) * 30
    noise = random.randint(-10, 10)

    prediction = 180 + trend + noise

    if st.session_state.event_mode:
        prediction *= 1.35

    st.metric("Predicted Occupancy", int(prediction))

    risk = min(100, int(prediction / 5))

    if risk > 75:
        st.error("High Congestion Expected")
    elif risk > 45:
        st.warning("Moderate Congestion Expected")
    else:
        st.success("Low Congestion")

    best_zone = min(zones, key=zones.get)
    st.info(f"Smart Recommendation → {best_zone}")

    best_time = f"{random.randint(8,10)}:{random.choice(['00','30'])} AM"
    st.success(f"Best Arrival Time → {best_time}")


# ---------------- LIVE ZONES ----------------
elif page == "Live Zones":

    st.title("📡 Live Parking Zones")

    for z, v in zones.items():

        col1, col2 = st.columns([3,1])

        with col1:
            st.write(z)

        with col2:
            if v > 80:
                st.error(f"{v}% FULL")
            elif v > 50:
                st.warning(f"{v}% BUSY")
            else:
                st.success(f"{v}% FREE")


# ---------------- SMART RESERVATION (FIXED UX) ----------------
elif page == "Smart Park":

    st.title("🚗 Smart Parking (1-Click System)")

    st.caption("AI automatically allocates best available parking slot")

    vehicle = st.text_input("Enter Vehicle Number")

    user_type = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    st.divider()

    # AI auto-zone selection
    recommended_zone = min(zones, key=zones.get)

    st.info(f"🤖 Recommended Zone: {recommended_zone}")

    slot_available = random.choice([True, True, False])  # bias toward success

    if st.button("🚗 Generate Smart Parking Pass"):

        if not vehicle:
            st.error("Enter vehicle number first")

        else:
            with st.spinner("Finding best slot using AI..."):
                time.sleep(1.5)

            if slot_available:

                raw = f"{vehicle}-{datetime.now()}"
                pass_id = "PASS-" + hashlib.md5(raw.encode()).hexdigest()[:8].upper()

                qr_payload = f"""
                SMART PARK PASS
                ID: {pass_id}
                VEHICLE: {vehicle}
                USER: {user_type}
                ZONE: {recommended_zone}
                TIME: {datetime.now().strftime("%H:%M:%S")}
                """

                st.success("✅ Parking Allocated Successfully")
                st.code(pass_id)

                st.text_area("🎫 QR PASS (Scan Data)", qr_payload, height=160)

                st.session_state.active_pass = pass_id

                st.session_state.passes.append({
                    "id": pass_id,
                    "vehicle": vehicle,
                    "zone": recommended_zone,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

                st.balloons()

            else:
                wait_id = "WL-" + str(random.randint(1000,9999))
                st.warning("All slots full → Added to Waitlist")
                st.code(wait_id)

                st.session_state.waitlist.append(wait_id)


# ---------------- ACTIVE PASS ----------------
elif page == "My Pass":

    st.title("🎫 My Active Parking Pass")

    if st.session_state.active_pass:

        st.success("Active Parking Pass Found")

        st.code(st.session_state.active_pass)

        st.info("Show this QR at campus entry gate")

        if st.button("Invalidate Pass"):
            st.session_state.active_pass = None
            st.warning("Pass Cancelled")

    else:
        st.info("No active pass found")


# ---------------- FOOTER ----------------
st.sidebar.divider()
st.sidebar.caption("v2.0 • AI Parking Infrastructure System")
