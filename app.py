import streamlit as st
import random
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO

# ================= SETUP =================
st.set_page_config(page_title="Smart Campus AI Parking", layout="wide")

# ================= STATE =================
if "pass_id" not in st.session_state:
    st.session_state.pass_id = None

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ================= ZONES =================
zones = {
    "Zone A": random.randint(60, 95),
    "Zone B": random.randint(40, 90),
    "Zone C": random.randint(20, 80)
}

# ================= UNIQUE AI CORE =================

def stress_score(occupancy, is_faculty):
    base = occupancy
    priority_bonus = -15 if is_faculty else 10
    randomness = random.randint(-5, 5)
    return max(0, base + priority_bonus + randomness)

def auto_allocate(user_type):
    scores = {}

    for z, occ in zones.items():
        score = stress_score(occ, user_type == "Faculty")
        scores[z] = score

    best_zone = min(scores, key=scores.get)
    return best_zone, scores

def qr(data):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf

def notify(msg):
    st.session_state.alerts.append(msg)

# ================= HEADER =================
st.title("🚗 Smart Campus AI Parking System (Next-Gen)")

role = st.sidebar.selectbox("Role", ["Student", "Faculty", "Admin"])

st.sidebar.markdown("### 🔔 AI Notifications")
for a in st.session_state.alerts[-5:]:
    st.sidebar.info(a)

# ================= ADMIN =================
if role == "Admin":

    st.header("🛠 AI CONTROL CENTER")

    total = sum(zones.values())

    st.metric("Total Load Index", total)

    for z, v in zones.items():
        st.write(f"{z} → Load {v}")

    st.warning("AI is continuously optimizing parking allocation")

# ================= USER =================
else:

    st.header("🧠 AI Smart Allocation System")

    vehicle = st.text_input("Vehicle Number")

    best_zone, scores = auto_allocate(role)

    st.success(f"🤖 AI Assigned Zone → {best_zone}")

    st.caption("Stress Scores (lower = better)")

    st.json(scores)

    if st.button("Generate Smart Pass"):

        if vehicle:

            raw = vehicle + str(datetime.now())
            pid = "AI-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

            qr_data = f"""
SMART AI PARK PASS
ID: {pid}
ROLE: {role}
ZONE: {best_zone}
TIME: {datetime.now()}
"""

            img = qr(qr_data)

            st.session_state.pass_id = pid

            notify(f"{role} assigned to {best_zone}")

            st.success("AI Allocation Complete")
            st.image(img, caption="Smart QR Pass")
            st.code(pid)

            st.balloons()

        else:
            st.error("Enter vehicle number")

# ================= LIVE AI ZONES =================
st.markdown("## 🔥 AI Zone Heatmap")

for z, v in zones.items():

    if v > 80:
        st.error(f"{z} → 🔴 CRITICAL LOAD ({v})")
    elif v > 50:
        st.warning(f"{z} → 🟡 MODERATE LOAD ({v})")
    else:
        st.success(f"{z} → 🟢 LOW LOAD ({v})")

# ================= UNIQUE INSIGHT =================
st.markdown("## 📊 AI INSIGHT ENGINE")

peak = max(zones, key=zones.get)

st.info(f"""
🚨 Peak Stress Zone: {peak}  
🧠 Recommendation: Avoid peak zone  
📉 AI Suggestion: Shift 10–15 mins earlier arrival
""")

# ================= PASS =================
st.markdown("## 🎫 Active AI Pass")

if st.session_state.pass_id:
    st.code(st.session_state.pass_id)
else:
    st.info("No active pass")