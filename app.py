import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

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
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-weight: 600;
}

h1, h2, h3 { color: #60a5fa; }

.block {
    padding: 15px;
    background-color: #0f172a;
    border-radius: 12px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "role" not in st.session_state:
    st.session_state.role = "Student"

if "notifications" not in st.session_state:
    st.session_state.notifications = []

# ================= ZONE SYSTEM =================
zones = {
    "Zone A (Faculty Priority)": {"cap": 120, "used": random.randint(60, 110)},
    "Zone B (Students)": {"cap": 200, "used": random.randint(80, 180)},
    "Zone C (Visitors)": {"cap": 180, "used": random.randint(50, 160)},
}

# ================= FUNCTIONS =================

def available(zone):
    return zones[zone]["cap"] - zones[zone]["used"]

def ai_recommend(user_type):
    if user_type == "Faculty":
        return "Zone A (Faculty Priority)"
    elif user_type == "Student":
        return "Zone B (Students)"
    else:
        return "Zone C (Visitors)"

def generate_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

def notify(msg):
    st.session_state.notifications.append(msg)

# ================= HEADER =================
st.title("🚗 Smart Campus Parking System")
st.caption("Industry-Level Smart Parking + Admin Control System")

# ================= ROLE SELECTION =================
st.sidebar.title("Access Panel")

role = st.sidebar.selectbox("Select Role", ["Student", "Faculty", "Admin"])
st.session_state.role = role

st.sidebar.markdown("---")
st.sidebar.write("🔔 Notifications")

for n in st.session_state.notifications[-5:]:
    st.sidebar.info(n)

# ================= ADMIN DASHBOARD =================
if role == "Admin":

    st.header("🛠 Admin Dashboard")

    total_used = sum(z["used"] for z in zones.values())
    total_cap = sum(z["cap"] for z in zones.values())

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Capacity", total_cap)
    col2.metric("Occupied", total_used)
    col3.metric("Occupancy %", f"{round((total_used/total_cap)*100,2)}%")

    st.markdown("### 📊 Zone Status")

    for z, data in zones.items():
        st.write(f"{z}: {data['used']}/{data['cap']}")

    st.warning("Admin can monitor real-time campus parking load.")

# ================= USER DASHBOARD =================
else:

    st.header("🎟 Smart Parking Reservation")

    user_type = role

    vehicle = st.text_input("Enter Vehicle Number")

    st.info(f"Logged in as: {user_type}")

    recommended = ai_recommend(user_type)

    st.success(f"🤖 AI Recommended Zone → {recommended}")

    if st.button("🚀 Generate Parking Pass"):

        if not vehicle:
            st.error("Enter vehicle number")
        else:

            if available(recommended) > 0:

                zones[recommended]["used"] += 1

                raw = vehicle + str(datetime.now())
                pass_id = "PASS-" + hashlib.sha256(raw.encode()).hexdigest()[:10].upper()

                qr_data = f"""
SMART CAMPUS PARK PASS
ID: {pass_id}
USER: {user_type}
ZONE: {recommended}
TIME: {datetime.now()}
"""

                qr_img = generate_qr(qr_data)

                st.session_state.pass_id = pass_id

                notify(f"{user_type} booked slot in {recommended}")

                st.success("✅ Parking Confirmed")

                st.image(qr_img, caption="Scan QR at Entry")

                st.code(pass_id)

            else:
                notify("Slot full → Added to waitlist")
                st.warning("⚠ Zone Full → Added to Waitlist")

# ================= LIVE ZONES =================
st.markdown("## 📡 Live Parking Availability")

for z, data in zones.items():
    avail = available(z)

    if avail < 20:
        st.error(f"{z} → CRITICAL ({avail} slots left)")
    elif avail < 50:
        st.warning(f"{z} → BUSY ({avail} slots left)")
    else:
        st.success(f"{z} → AVAILABLE ({avail} slots left)")

# ================= ACTIVE PASS =================
st.markdown("## 🎫 Active Pass")

if st.session_state.pass_id:
    st.code(st.session_state.pass_id)
else:
    st.info("No active pass")

# ================= FOOTER =================
st.markdown("---")
st.caption("Smart Campus Parking System • Mahindra University Project")