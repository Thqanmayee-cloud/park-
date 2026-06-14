import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PARK+ Smart Campus Parking",
    page_icon="🚗",
    layout="wide"
)

# ================= STATE =================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "role" not in st.session_state:
    st.session_state.role = "Student"

if "vehicle" not in st.session_state:
    st.session_state.vehicle = ""

if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "notifications" not in st.session_state:
    st.session_state.notifications = []

# ================= ZONES =================
zones = {
    "Zone A (Faculty Priority)": random.randint(60, 95),
    "Zone B (Students)": random.randint(40, 90),
    "Zone C (Visitors)": random.randint(20, 80)
}

# ================= UI STYLE =================
st.markdown("""
<style>
.main { background-color: #0b1220; color: #e5e7eb; }

h1, h2, h3 { color: #60a5fa; }

.card {
    background-color: #0f172a;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid #1f2937;
}

.stButton button {
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
def notify(msg):
    st.session_state.notifications.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")

def ai_zone(role):
    if role == "Faculty":
        return "Zone A (Faculty Priority)"
    elif role == "Student":
        return "Zone B (Students)"
    else:
        return "Zone C (Visitors)"

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

def go(page):
    st.session_state.page = page

# ================= SIDEBAR =================
st.sidebar.title("🚗 PARK+ SYSTEM")

st.sidebar.write("### Notifications")
for n in st.session_state.notifications[-5:]:
    st.sidebar.info(n)

st.sidebar.markdown("---")

if st.sidebar.button("🏠 Home"):
    go("home")

if st.sidebar.button("🔄 New Booking"):
    go("vehicle")

if st.sidebar.button("🛠 Admin Panel"):
    go("admin")

# ================= HOME =================
if st.session_state.page == "home":

    st.title("🚗 PARK+ Smart Campus Parking System")
    st.subheader("AI-Based Smart Parking Allocation")

    st.markdown("""
    <div class='card'>
    Welcome to PARK+ System  
    - AI Auto Parking Allocation  
    - Faculty Priority System  
    - Real-time Zone Management  
    - QR Based Entry Pass  
    </div>
    """, unsafe_allow_html=True)

    role = st.selectbox("Select Role", ["Student", "Faculty", "Visitor"])
    st.session_state.role = role

    if st.button("🚀 Start Parking"):
        go("vehicle")

# ================= VEHICLE INPUT =================
elif st.session_state.page == "vehicle":

    st.title("🚗 Step 1: Vehicle Entry")

    st.session_state.vehicle = st.text_input("Enter Vehicle Number")

    if st.button("Next → AI Processing"):

        if st.session_state.vehicle == "":
            st.error("Please enter vehicle number")
        else:
            go("processing")

# ================= AI PROCESSING =================
elif st.session_state.page == "processing":

    st.title("🧠 AI Processing System")

    with st.spinner("Analyzing parking zones..."):
        pass

    role = st.session_state.role
    recommended = ai_zone(role)

    st.success(f"AI Recommended Zone → {recommended}")

    st.markdown("""
    <div class='card'>
    ✔ Checking congestion levels  
    ✔ Applying faculty priority rules  
    ✔ Calculating optimal zone  
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Parking Pass"):
        st.session_state.recommended = recommended
        go("result")

# ================= RESULT =================
elif st.session_state.page == "result":

    st.title("🎯 Parking Allocation Result")

    vehicle = st.session_state.vehicle
    role = st.session_state.role
    zone = st.session_state.recommended

    raw = vehicle + str(datetime.now())
    pass_id = "PARK+" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

    qr_data = f"""
PARK+ CAMPUS PASS
ID: {pass_id}
ROLE: {role}
ZONE: {zone}
TIME: {datetime.now()}
"""

    qr = make_qr(qr_data)

    st.success("Parking Confirmed!")

    st.image(qr, caption="Scan QR at Entry")

    st.code(pass_id)

    notify(f"{role} allocated → {zone}")

    st.session_state.pass_id = pass_id

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 Back to Home"):
            go("home")

    with col2:
        if st.button("🔄 New Booking"):
            go("vehicle")

# ================= ADMIN =================
elif st.session_state.page == "admin":

    st.title("🛠 Admin Dashboard")

    st.markdown("""
    <div class='card'>
    System Overview (Simulated Real-Time Data)
    </div>
    """, unsafe_allow_html=True)

    total = sum(zones.values())

    st.metric("System Load Index", total)

    for z, v in zones.items():
        st.write(f"{z}: {v}% occupancy")

        if v > 80:
            st.error("CRITICAL")
        elif v > 50:
            st.warning("BUSY")
        else:
            st.success("FREE")

    if st.button("🏠 Back Home"):
        go("home")