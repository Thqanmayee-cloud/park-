import streamlit as st
import random
import hashlib
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(
    page_title="Smart Campus Parking System",
    page_icon="🚗",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

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

h1, h2, h3 { color: #60a5fa; }

.block {
    padding: 20px;
    border-radius: 12px;
    background-color: #0f172a;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "history" not in st.session_state:
    st.session_state.history = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_mode" not in st.session_state:
    st.session_state.event_mode = False

# ================= CORE ENGINE =================
TOTAL = 500

def ai(hour):
    base = 180
    trend = (hour - 8) * 30
    noise = random.randint(-6, 6)
    mult = 1.4 if st.session_state.event_mode else 1.0
    return int((base + trend + noise) * mult)

zones = {
    "Zone A (Faculty)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Hostel)": random.randint(30, 85),
    "Zone D (Visitors)": random.randint(20, 75),
}

recommended_zone = min(zones, key=zones.get)

# ================= HEADER =================
st.title("🚗 Smart Campus Parking System")
st.caption("Single Page Smart Control Dashboard")

st.toggle("🎯 Event Mode", key="event_mode")

# ================= FAST RESERVATION (TOP UX) =================
st.markdown("## 🎟 Quick Smart Reservation")

with st.container():
    vehicle = st.text_input("Vehicle Number")
    user = st.selectbox("User Type", ["Student", "Faculty", "Visitor"])

    st.info(f"🤖 AI Recommended Zone → {recommended_zone}")

    if st.button("🚀 Generate Parking Pass"):

        if not vehicle:
            st.error("Enter vehicle number")
        else:
            slot = random.choice([True, True, False])

            if slot:
                raw = vehicle + str(datetime.now())
                pass_id = "PASS-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

                st.session_state.pass_id = pass_id
                st.session_state.history.append(pass_id)

                st.success("✅ Parking Confirmed")
                st.code(pass_id)
                st.balloons()

            else:
                wl = "WL-" + str(random.randint(1000,9999))
                st.warning("⚠ No slot available")
                st.session_state.waitlist.append(wl)

# ================= DASHBOARD =================
st.markdown("## 🏢 Live Dashboard")

hour = datetime.now().hour
predicted = ai(hour)

occupied = min(predicted, TOTAL)
available = TOTAL - occupied
rate = round((occupied / TOTAL) * 100, 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Slots", TOTAL)
col2.metric("Occupied", occupied)
col3.metric("Available", available)
col4.metric("Occupancy %", f"{rate}%")

# ================= AI ENGINE =================
st.markdown("## 🧠 AI Prediction Engine")

risk = min(100, predicted // 5)

st.metric("Predicted Occupancy", predicted)

if risk > 75:
    st.error("🔴 High Congestion")
elif risk > 45:
    st.warning("🟡 Medium Congestion")
else:
    st.success("🟢 Low Congestion")

st.info(f"📍 Smart Zone Recommendation → {recommended_zone}")

# ================= LIVE ZONES =================
st.markdown("## 📡 Live Zone Status")

for z, v in zones.items():
    if v > 80:
        st.error(f"{z} → {v}% FULL")
    elif v > 50:
        st.warning(f"{z} → {v}% BUSY")
    else:
        st.success(f"{z} → {v}% FREE")

# ================= ACTIVE PASS =================
st.markdown("## 🎫 Active Pass")

if st.session_state.pass_id:
    st.success(st.session_state.pass_id)

    if st.button("Cancel Pass"):
        st.session_state.pass_id = None
        st.warning("Pass Cancelled")
else:
    st.info("No active pass")

# ================= HISTORY =================
st.markdown("## 📊 System Logs")

col1, col2 = st.columns(2)

with col1:
    st.write("### Bookings")
    st.write(st.session_state.history if st.session_state.history else "No bookings")

with col2:
    st.write("### Waitlist")
    st.write(st.session_state.waitlist if st.session_state.waitlist else "No waitlist")