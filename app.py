import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

# ================= CONFIG =================
st.set_page_config(page_title="Smart Parking", layout="wide")

# ================= SESSION STATE =================
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "notifications" not in st.session_state:
    st.session_state.notifications = []

if "zone_state" not in st.session_state:
    st.session_state.zone_state = {
        "Zone A (Faculty)": [120, random.randint(60, 110)],
        "Zone B (Students)": [200, random.randint(80, 180)],
        "Zone C (Visitors)": [180, random.randint(50, 160)]
    }

# ================= HELPERS =================
def available(zone):
    cap, used = st.session_state.zone_state[zone]
    return cap - used

def ai_zone(role):
    if role == "Faculty":
        return "Zone A (Faculty)"
    elif role == "Student":
        return "Zone B (Students)"
    else:
        return "Zone C (Visitors)"

def make_qr(data):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf

def notify(msg):
    st.session_state.notifications.append(msg)

# ================= UI =================
st.title("🚗 Smart Campus Parking System")

role = st.sidebar.selectbox("Role", ["Student", "Faculty", "Admin"])

st.sidebar.markdown("### 🔔 Notifications")
for n in st.session_state.notifications[-5:]:
    st.sidebar.info(n)

# ================= ADMIN =================
if role == "Admin":
    st.header("🛠 Admin Dashboard")

    total_cap = sum(v[0] for v in st.session_state.zone_state.values())
    total_used = sum(v[1] for v in st.session_state.zone_state.values())

    st.metric("Total Capacity", total_cap)
    st.metric("Occupied", total_used)
    st.metric("Occupancy %", f"{round(total_used/total_cap*100,2)}%")

    st.markdown("### Zone Status")
    for z, v in st.session_state.zone_state.items():
        st.write(f"{z}: {v[1]}/{v[0]}")

# ================= USER =================
else:

    st.header("🎟 Smart Reservation")

    vehicle = st.text_input("Vehicle Number")
    user = role

    recommended = ai_zone(user)

    st.success(f"AI Recommended → {recommended}")

    if st.button("Generate Pass"):

        if not vehicle:
            st.error("Enter vehicle number")
        else:

            cap, used = st.session_state.zone_state[recommended]

            if used < cap:

                # SAFE UPDATE (no corruption)
                st.session_state.zone_state[recommended][1] += 1

                raw = vehicle + str(datetime.now())
                pass_id = "PASS-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

                qr_data = f"""
PASS ID: {pass_id}
USER: {user}
ZONE: {recommended}
TIME: {datetime.now()}
"""

                qr = make_qr(qr_data)

                st.session_state.pass_id = pass_id

                notify(f"{user} booked in {recommended}")

                st.success("Booking Confirmed")
                st.image(qr, caption="QR Pass")
                st.code(pass_id)

            else:
                notify("Zone full → waitlisted")
                st.warning("Zone Full")

# ================= ZONES =================
st.markdown("## 📡 Live Zones")

for z, v in st.session_state.zone_state.items():
    free = v[0] - v[1]

    if free < 20:
        st.error(f"{z} → CRITICAL ({free})")
    elif free < 50:
        st.warning(f"{z} → BUSY ({free})")
    else:
        st.success(f"{z} → FREE ({free})")

# ================= PASS =================
st.markdown("## 🎫 Active Pass")

if st.session_state.pass_id:
    st.code(st.session_state.pass_id)
else:
    st.info("No active pass")
st.caption("Smart Campus Parking System • Mahindra University Project")