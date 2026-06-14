import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO
import pandas as pd

# ================= CONFIG =================
st.set_page_config(
    page_title="Park+ Production System",
    layout="wide",
    page_icon="🚗"
)

# ================= DATABASE =================
conn = sqlite3.connect("parkplus.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS bookings(
    id TEXT PRIMARY KEY,
    username TEXT,
    vehicle TEXT,
    role TEXT,
    zone TEXT,
    time TEXT,
    status TEXT
)
""")

conn.commit()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= ZONE ENGINE (REAL LOGIC) =================
def get_zones():
    c.execute("SELECT zone, COUNT(*) FROM bookings WHERE status='ACTIVE' GROUP BY zone")
    data = dict(c.fetchall())

    return {
        "Zone A (Faculty)": 50 - data.get("Zone A (Faculty)", 0),
        "Zone B (Students)": 200 - data.get("Zone B (Students)", 0),
        "Zone C (Visitors)": 100 - data.get("Zone C (Visitors)", 0),
    }

# ================= QR =================
def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# ================= LOGIN =================
if st.session_state.user is None:

    st.title("🚗 Park+ Login")

    username = st.text_input("Username")
    role = st.selectbox("Role", ["Student", "Faculty", "Admin"])

    if st.button("Login"):

        c.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (username, role))
        conn.commit()

        st.session_state.user = {"username": username, "role": role}
        st.rerun()

# ================= MAIN APP =================
else:

    user = st.session_state.user

    st.sidebar.success(f"Logged in as {user['username']} ({user['role']})")

    page = st.sidebar.radio("Navigation", ["Dashboard", "Reserve", "Verify QR", "Analytics"])

    zones = get_zones()

    # ================= DASHBOARD =================
    if page == "Dashboard":

        st.title("🚗 Park+ Smart Parking System")

        col1, col2, col3 = st.columns(3)

        col1.metric("Zone A (Faculty)", zones["Zone A (Faculty)"])
        col2.metric("Zone B (Students)", zones["Zone B (Students)"])
        col3.metric("Zone C (Visitors)", zones["Zone C (Visitors)"])

        st.bar_chart(zones)

    # ================= RESERVATION =================
    elif page == "Reserve":

        st.subheader("🅿️ Reserve Parking Slot")

        vehicle = st.text_input("Vehicle Number")

        zone = st.selectbox(
            "Select Zone",
            list(zones.keys())
        )

        if st.button("Reserve Slot"):

            if zones[zone] <= 0:
                st.error("No slots available in this zone")
            else:

                booking_id = hashlib.md5(
                    (vehicle + str(datetime.now())).encode()
                ).hexdigest()[:10].upper()

                qr_payload = f"{booking_id}|{vehicle}|{zone}|ACTIVE"

                c.execute("""
                    INSERT INTO bookings VALUES (?,?,?,?,?,?,?)
                """, (
                    booking_id,
                    user["username"],
                    vehicle,
                    user["role"],
                    zone,
                    str(datetime.now()),
                    "ACTIVE"
                ))

                conn.commit()

                st.success("Booking Confirmed")

                st.image(make_qr(qr_payload), caption="Scan at Entry")

                st.code(booking_id)

    # ================= QR VERIFY =================
    elif page == "Verify QR":

        st.subheader("📲 QR Verification (Gate System)")

        qr_input = st.text_input("Enter Booking ID")

        if st.button("Verify"):

            c.execute("SELECT * FROM bookings WHERE id=?", (qr_input,))
            result = c.fetchone()

            if result:
                st.success("VALID PASS ✅")
                st.json(result)
            else:
                st.error("INVALID PASS ❌")

    # ================= ANALYTICS =================
    elif page == "Analytics":

        st.subheader("📊 System Analytics")

        df = pd.read_sql_query("SELECT * FROM bookings", conn)

        if df.empty:
            st.warning("No bookings yet")
        else:
            st.dataframe(df)

            st.bar_chart(df["zone"].value_counts())

            st.metric("Total Bookings", len(df))