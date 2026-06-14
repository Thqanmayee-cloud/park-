import streamlit as st
import random
import hashlib
import time
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(
    page_title="Smart Campus Parking AI",
    layout="wide",
    page_icon="🚗"
)

# ================= UI STYLE =================
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

.block {
    background-color: #0f172a;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #1f2937;
}

.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

h1, h2, h3 { color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "logs" not in st.session_state:
    st.session_state.logs = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ================= ZONE SYSTEM =================
def generate_zones():
    return {
        "Zone A (Faculty Priority)": random.randint(60, 95),
        "Zone B (Students)": random.randint(40, 90),
        "Zone C (Visitors)": random.randint(20, 80)
    }

zones = generate_zones()

# ================= AI ENGINE =================
def stress_score(load, is_faculty):
    base = load
    return base - (20 if is_faculty else -5) + random.randint(-5, 5)

def auto_assign(role):
    scores = {}
    for z, load in zones.items():
        scores[z] = stress_score(load, role == "Faculty")
    return min(scores, key=scores.get), scores

# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ================= ALERT SYSTEM =================
def notify(msg):
    st.session_state.alerts.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")

# ================= HEADER =================
st.title("🚗 Smart Campus Parking AI System")
st.caption("Next-Gen AI Parking Optimization Platform")

role = st.sidebar.selectbox("User Role", ["Student", "Faculty", "Admin"])

st.sidebar.markdown("### 🔔 Alerts")
for a in st.session_state.alerts[-6:]:
    st.sidebar.info(a)

# ================= ADMIN PANEL =================
if role == "Admin":

    st.header("🛠 Admin Control Dashboard")

    total = sum(zones.values())

    st.metric("System Load Index", total)

    for z, v in zones.items():
        progress = int((v / 100) * 100)
        st.write(z)
        st.progress(progress)

    st.warning("AI optimizing parking distribution in real-time")

# ================= USER PANEL =================
else:

    st.header("🧠 AI Smart Parking Allocation")

    vehicle = st.text_input("Vehicle Number")

    zone, scores = auto_assign(role)

    st.success(f"🤖 AI Assigned Zone → {zone}")

    st.caption("Stress Score Engine (lower is better)")
    st.json(scores)

    if st.button("🚀 Generate Smart Parking Pass"):

        if not vehicle:
            st.error("Enter vehicle number")
        else:

            with st.spinner("AI analyzing parking space..."):
                time.sleep(1.5)

            raw = vehicle + str(datetime.now())
            pid = "AI-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

            qr_data = f"""
SMART CAMPUS AI PARK PASS
ID: {pid}
ROLE: {role}
ZONE: {zone}
TIME: {datetime.now()}
"""

            img = make_qr(qr_data)

            st.session_state.pass_id = pid

            notify(f"{role} allocated to {zone}")

            st.success("Allocation Complete")
            st.image(img, caption="QR Parking Pass")
            st.code(pid)

            st.balloons()

# ================= LIVE ZONES =================
st.markdown("## 📡 Live Parking Heatmap")

for z, v in zones.items():

    col1, col2 = st.columns([3,1])

    with col1:
        st.write(z)
        st.progress(v)

    with col2:
        if v > 80:
            st.error("CRITICAL")
        elif v > 50:
            st.warning("BUSY")
        else:
            st.success("FREE")

# ================= AI INSIGHTS =================
st.markdown("## 📊 AI Insights Engine")

peak = max(zones, key=zones.get)

st.info(f"""
🔥 Peak Zone: {peak}
🧠 Recommendation: Avoid peak zone during next 30 mins
🚗 Best Strategy: Early arrival improves availability by 35%
""")

# ================= ACTIVE PASS =================
st.markdown("## 🎫 Active Pass")

if st.session_state.pass_id:
    st.success(st.session_state.pass_id)
else:
    st.info("No active parking pass generated yet")

# ================= FOOTER =================
st.markdown("---")
st.caption("Smart Campus AI Parking System • Production Simulation Model")