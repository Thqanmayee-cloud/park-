import streamlit as st
import random
import hashlib
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import os

# ================= SIMPLE LOGIN =================
if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.role is None:
    st.title("ParkSmart Login")

    role = st.radio("Select Role", ["Student", "Faculty"])
    name = st.text_input("Enter Your Name")

    if st.button("Login"):
        if name.strip() == "":
            st.error("Please enter your name")
        else:
            st.session_state.role = role
            st.session_state.user = name
            st.rerun()
    st.stop()


# ================= CONFIG =================
st.set_page_config(
    page_title="ParkSmart | Mahindra University",
    layout="wide",
    page_icon="🚗"
)

st.title("ParkSmart | Mahindra University Smart Parking System")
st.markdown("---")


# ================= FILE SETUP & STRUCTURAL SANITIZATION =================
# Standardizing 6 columns to cleanly track Active vs Cancelled passes
CORE_COLUMNS = ["User", "Vehicle", "Role", "Zone", "Time", "Status"]

if not os.path.exists("bookings.csv"):
    pd.DataFrame(columns=CORE_COLUMNS).to_csv("bookings.csv", index=False)
else:
    try:
        df_fix = pd.read_csv("bookings.csv")
        # Ensure 'Status' column exists if upgrading an older CSV file
        if "Status" not in df_fix.columns:
            df_fix["Status"] = "Active"
            df_fix.to_csv("bookings.csv", index=False)
    except Exception:
        pd.DataFrame(columns=CORE_COLUMNS).to_csv("bookings.csv", index=False)

if not os.path.exists("event_bookings.csv"):
    pd.DataFrame(columns=["User", "Event", "Vehicle", "Time"]).to_csv("event_bookings.csv", index=False)


# ================= SESSION ALERTS =================
if "alerts" not in st.session_state:
    st.session_state.alerts = []


# ================= BASE ZONES =================
BASE_ZONES = {
    "Zone A (Faculty)": 80,
    "Zone B (Students)": 120,
    "Zone C (Visitors)": 100
}


# ================= EVENTS =================
EVENTS = [
    {"name": "Tech Fest 2026", "slots": 60, "booked": 0},
    {"name": "Convocation Day", "slots": 80, "booked": 0},
    {"name": "Hackathon Night", "slots": 40, "booked": 0}
]

if os.path.exists("event_bookings.csv"):
    try:
        df_ev = pd.read_csv("event_bookings.csv")
        for e in EVENTS:
            e["booked"] = len(df_ev[df_ev["Event"] == e["name"]])
    except Exception:
        pass


# ================= COMPUTE ZONES =================
def compute_zones():
    used = {z: 0 for z in BASE_ZONES}

    if os.path.exists("bookings.csv"):
        try:
            df = pd.read_csv("bookings.csv")
            # Only count spots for passes that are currently Active
            active_df = df[df["Status"].str.strip().str.capitalize() == "Active"]
            for _, row in active_df.iterrows():
                if str(row.get("Zone")) in used:
                    used[str(row["Zone"])] += 1
        except Exception:
            pass

    available = {z: max(BASE_ZONES[z] - used[z], 0) for z in BASE_ZONES}
    return used, available

occupied, available = compute_zones()

TOTAL = sum(BASE_ZONES.values())
total_used = sum(occupied.values())
occupancy = round((total_used / TOTAL) * 100, 2)


# ================= HELPERS =================
def ai_zone(role):
    if role == "Faculty":
        return "Zone A (Faculty)"
    elif role == "Student":
        return "Zone B (Students)"
    return "Zone C (Visitors)"

def make_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

def notify(msg):
    st.session_state.alerts.append(
        f"{datetime.now().strftime('%H:%M:%S')} - {msg}"
    )


# ================= STYLE =================
st.markdown("""
<style>
.zoneA {background:#16a34a;padding:12px;border-radius:10px;color:white;text-align:center;}
.zoneB {background:#2563eb;padding:12px;border-radius:10px;color:white;text-align:center;}
.zoneC {background:#f59e0b;padding:12px;border-radius:10px;color:white;text-align:center;}

.stButton button {
    width:100%;
    border-radius:10px;
    font-weight:bold;
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
}
</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR & NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard","🗺️ Map View", "🅿️ Reservation System", "🎉 Event Parking", ]
)

st.sidebar.markdown("---")
st.sidebar.success(f"Logged in as {st.session_state.role}")
st.sidebar.write(f"User: {st.session_state.user}")

if st.sidebar.button("🧹 Clear All App Data"):
    pd.DataFrame(columns=CORE_COLUMNS).to_csv("bookings.csv", index=False)
    pd.DataFrame(columns=["User", "Event", "Vehicle", "Time"]).to_csv("event_bookings.csv", index=False)
    st.sidebar.info("CSV records reset successfully!")
    st.rerun()

if st.sidebar.button("Logout"):
    st.session_state.role = None
    st.session_state.user = None
    st.rerun()


# ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":
    st.title("🗺️ Campus Parking Map")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='zoneA'>ZONE A<br>FACULTY</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])

    with col2:
        st.markdown("<div class='zoneB'>ZONE B<br>STUDENTS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])

    with col3:
        st.markdown("<div class='zoneC'>ZONE C<br>VISITORS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])


# ======================================================
# 🅿️ RESERVATION SYSTEM (WITH SIDEBAR CANCELLATION PANEL)
# ======================================================
elif page == "🅿️ Reservation System":
    st.title("🅿️ Parking Reservation")

    # Layout splits to separate generating passes from revoking passes
    left_layout, right_layout = st.columns([2, 1])

    with left_layout:
        st.subheader("Request Parking Pass")
        role = st.session_state.role
        vehicle = st.text_input("Vehicle Number").strip().upper()

        zone = ai_zone(role)
        st.info(f"AI Suggested Zone → {zone}")

        if st.button("Generate Parking Pass"):
            if vehicle == "":
                st.error("Enter vehicle number")
            elif available[zone] <= 0:
                st.error("No slots available")
            else:
                df = pd.read_csv("bookings.csv")

                time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = {
                    "User": st.session_state.user,
                    "Vehicle": vehicle,
                    "Role": role,
                    "Zone": zone,
                    "Time": time_string,
                    "Status": "Active"
                }

                # Block booking duplicates if an active pass already exists for this vehicle
                is_duplicate = (
                    (df["User"] == new_row["User"]) &
                    (df["Vehicle"] == new_row["Vehicle"]) &
                    (df["Status"] == "Active")
                ).any()

                if not is_duplicate:
                    df = df[CORE_COLUMNS]
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv("bookings.csv", index=False)
                    
                    notify(f"{st.session_state.user} generated an active pass for {vehicle}")
                    st.success("Booking Confirmed 🚗")
                else:
                    st.warning(f"An active booking pass already exists for vehicle {vehicle}!")

        # Always pull records to re-render the current QR code on page reloads
        if os.path.exists("bookings.csv") and vehicle != "":
            df_check = pd.read_csv("bookings.csv")
            latest_active = df_check[(df_check["User"] == st.session_state.user) & 
                                     (df_check["Vehicle"] == vehicle) & 
                                     (df_check["Status"] == "Active")]
            if not latest_active.empty:
                row_data = latest_active.iloc[-1]
                pid = "PSMART+" + hashlib.md5((str(row_data["Vehicle"]) + str(row_data["Time"])).encode()).hexdigest()[:10].upper()
                qr = make_qr(pid)
                
                st.markdown("### 🎫 Active Ticket Pass")
                st.image(qr, width=250)
                st.code(f"Pass ID: {pid}")

    with right_layout:
        st.subheader("Cancel Pass")
        if os.path.exists("bookings.csv"):
            df_cancel = pd.read_csv("bookings.csv")
            
            # Isolate active passes belonging to the logged-in profile
            user_active = df_cancel[(df_cancel["User"] == st.session_state.user) & (df_cancel["Status"] == "Active")]
            
            if not user_active.empty:
                vehicle_to_cancel = st.selectbox("Select Vehicle to Cancel", user_active["Vehicle"].unique())
                
                if st.button("❌ Revoke Reservation"):
                    idx = df_cancel[(df_cancel["User"] == st.session_state.user) & 
                                    (df_cancel["Vehicle"] == vehicle_to_cancel) & 
                                    (df_cancel["Status"] == "Active")].index
                    
                    if len(idx) > 0:
                        df_cancel.at[idx[0], "Status"] = "Cancelled"
                        df_cancel.to_csv("bookings.csv", index=False)
                        notify(f"Cancelled booking for vehicle {vehicle_to_cancel}")
                        st.success(f"Pass for {vehicle_to_cancel} revoked successfully.")
                        st.rerun()
            else:
                st.info("No active reservations found under your profile.")

    st.write("---")
    for a in st.session_state.alerts[-5:]:
        st.warning(a)


# ======================================================
# 🎉 EVENT PARKING
# ======================================================
elif page == "🎉 Event Parking":
    st.title("🎉 Event Parking System")

    event_name = st.selectbox("Select Event", [e["name"] for e in EVENTS])
    vehicle = st.text_input("Vehicle Number (Event)").strip().upper()

    event_obj = next(e for e in EVENTS if e["name"] == event_name)
    st.info(f"Slots Available: {event_obj['slots'] - event_obj['booked']} / {event_obj['slots']}")

    if st.button("Book Event Parking"):
        if vehicle == "":
            st.error("Enter vehicle number")
        elif event_obj["booked"] >= event_obj["slots"]:
            st.error("Event Parking Full")
        else:
            df_event = pd.read_csv("event_bookings.csv")
            
            new_event_row = {
                "User": st.session_state.user,
                "Event": event_name,
                "Vehicle": vehicle,
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            df_event = pd.concat([df_event, pd.DataFrame([new_event_row])], ignore_index=True)
            df_event.to_csv("event_bookings.csv", index=False)

            st.success("Event Parking Confirmed 🎉")
            st.rerun()

    st.divider()
    st.subheader("📊 Event Overview")
    st.dataframe(pd.DataFrame(EVENTS), use_container_width=True, hide_index=True)


# ======================================================
# 📊 DASHBOARD
# ======================================================
elif page == "📊 Dashboard":
    st.title("📊 ParkSmart Dashboard")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Occupancy %", f"{occupancy}%")
    with col_m2:
        st.metric("Total Active Vehicles", total_used)

    st.subheader("Zone Status")
    st.bar_chart(pd.DataFrame(occupied, index=["Count"]).T)

    st.subheader("Recent Bookings")
    if os.path.exists("bookings.csv"):
        df_display = pd.read_csv("bookings.csv")
        if not df_display.empty:
            # Filter layout to strictly maintain standard headers
            existing_cores = [col for col in CORE_COLUMNS if col in df_display.columns]
            df_display = df_display[existing_cores]
            
            # Drop duplicates keeping the latest status modification
            df_display = df_display.drop_duplicates(subset=["User", "Vehicle", "Zone"], keep="last")
            df_display = df_display.reindex(columns=CORE_COLUMNS[:-1]) # Keep just the first 5 columns for UI
            
            st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("No bookings recorded in history logs yet.")

    st.subheader("Event Bookings")
    if os.path.exists("event_bookings.csv"):
        df2_display = pd.read_csv("event_bookings.csv")
        if not df2_display.empty:
            df2_display = df2_display.drop_duplicates(subset=["User", "Event", "Vehicle"], keep="last")
            st.dataframe(df2_display.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("No event spaces booked yet.")
          # ======================================================
# 🗺️ MAP VIEW
# ======================================================
if page == "🗺️ Map View":

    st.title("🗺️ Campus Parking Map")

    # 1. Map Layout (Safely resolved path)
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "parking_map.png")

    if os.path.exists(image_path):
        st.image(
            image_path,
            caption="ParkSmart Custom Zone Layout (Top View)",
            use_container_width=True
        )
    else:
        st.warning("⚠️ 'parking_map.png' not detected in your workspace directory.")

    # Extra spacing element
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Live Parking Availability Metrics (Placed strictly BELOW the map)
    st.markdown("### Live Parking Availability")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='zoneA'>ZONE A<br>FACULTY</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone A (Faculty)"])
        st.metric("Occupied", occupied["Zone A (Faculty)"])

    with col2:
        st.markdown("<div class='zoneB'>ZONE B<br>STUDENTS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone B (Students)"])
        st.metric("Occupied", occupied["Zone B (Students)"])

    with col3:
        st.markdown("<div class='zoneC'>ZONE C<br>VISITORS</div>", unsafe_allow_html=True)
        st.metric("Available", available["Zone C (Visitors)"])
        st.metric("Occupied", occupied["Zone C (Visitors)"])