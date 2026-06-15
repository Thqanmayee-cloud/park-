import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime

# 1. SETUP PRESENTATION PROPORTIONS & STYLE INJECTIONS
st.set_page_config(
    page_title="ParkSmart Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to force your Figma color-coding themes onto Streamlit containers
st.markdown("""
<style>
    .zone-box { padding: 20px; border-radius: 12px; margin-bottom: 15px; color: white; text-align: center; }
    .zone-a { background-color: #4CAF50; } /* Faculty Green */
    .zone-b { background-color: #2196F3; } /* Student Blue */
    .zone-c { background-color: #FFC107; color: black; } /* Visitor Yellow */
    .metric-val { font-size: 28px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. DATABASE ARCHITECTURE
# ==========================================================
def init_db():
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT,
            role TEXT,
            zone TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_bookings():
    conn = sqlite3.connect('parking.db')
    df = pd.read_sql_query("SELECT vehicle_number, role, zone, timestamp FROM bookings", conn)
    conn.close()
    return df

def save_booking(vehicle_num, user_role, assigned_zone, current_time):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO bookings (vehicle_number, role, zone, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (vehicle_num, user_role, assigned_zone, current_time))
    conn.commit()
    conn.close()


# ==========================================================
# 3. GLOBAL SESSION & AUTHENTICATION MANAGEMENT
# ==========================================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# --- RE-ENGINEERED LOGIN GATEWAY VIEW ---
if not st.session_state['logged_in']:
    st.title("🔒 ParkSmart | Secure Terminal Gateway")
    st.subheader("Mahindra University Authentication Portal")
    
    with st.container(border=True):
        selected_role = st.selectbox("Select Your User Access Profile Tier:", ["Faculty", "Student"])
        pass_code = st.text_input("Enter Gateway Pin / Password:", type="password", value="1234")
        
        if st.button("Authenticate and Open Session", type="primary"):
            if pass_code == "1234":  # Standard mock credentials validation
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = selected_role
                st.success(f"Access granted! Profile context: {selected_role}")
                st.rerun()
            else:
                st.error("Invalid structural access credentials. Please try again.")
    st.stop() # Stops execution here so unauthenticated users see nothing else


# ==========================================================
# 4. FUNCTIONAL SIDEBAR CONTROLS & ROUTING
# ==========================================================
st.sidebar.title("ParkSmart App Menu")
st.sidebar.write(f"🟢 **Profile Profile:** {st.session_state['user_role']}")

# THIS ROUTING MATRIX NOW ACTIVELY SWITCHES PAGES FLUIDLY
nav_selection = st.sidebar.radio(
    "Application Screens:", 
    ["Reservation System", "Campus Parking Map", "System Dashboard"]
)

st.sidebar.write("---")
if st.sidebar.button("🚪 Terminate Session (Logout)"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state.pop('active_ticket', None)
    st.rerun()


# ==========================================================
# PAGE 1: DYNAMIC RESERVATION SYSTEM SCREEN
# ==========================================================
if nav_selection == "Reservation System":
    st.title("🎫 Smart Reservation Gate")
    st.caption("Generate verifiable smart access passes in real-time.")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Parking Grid Assignment Form")
        vehicle_input = st.text_input("Vehicle Number Plate ID", value="TS06US678").strip().upper()
        
        # Enforce role boundaries matching your presentation metrics
        if st.session_state['user_role'] == "Faculty":
            allocated_zone = "Zone A (Faculty)"
            st.info("⚡ Priority Access Cleared: System routes your context directly to Zone A.")
        else:
            allocated_zone = "Zone B (Students)"
            st.info("ℹ️ General Access Status: Routed to Student Zone B grid slots.")

        if st.button("Generate Secure Pass Token", type="primary"):
            if not vehicle_input:
                st.error("Please insert a valid license plate code.")
            else:
                time_now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                save_booking(vehicle_input, st.session_state['user_role'], allocated_zone, time_now)
                
                st.session_state['active_ticket'] = {
                    'veh': vehicle_input,
                    'role': st.session_state['user_role'],
                    'zone': allocated_zone,
                    'time': time_now
                }
                st.success("Transaction committed to permanent system storage logs!")

    with col_right:
        st.subheader("Active Pass Token View")
        if 'active_ticket' in st.session_state:
            ticket = st.session_state['active_ticket']
            with st.container(border=True):
                st.markdown(f"**Status:** `CONFIRMED PASS` 🟢")
                st.write(f"**Vehicle:** `{ticket['veh']}`")
                st.write(f"**Target:** {ticket['zone']}")
                
                raw_payload = f"ID:{ticket['veh']}|Role:{ticket['role']}|Zone:{ticket['zone']}"
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(raw_payload)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                stream = BytesIO()
                qr_img.save(stream)
                st.image(stream.getvalue(), width=160)
                st.caption(f"Validated at: {ticket['time']}")
        else:
            st.info("No terminal pass generated in current session cache.")


# ==========================================================
# PAGE 2: STRUCTURAL COLOR-CODED PARKING MAP SCREEN
# ==========================================================
elif nav_selection == "Campus Parking Map":
    st.title("🗺️ Interactive Campus Space Matrix")
    st.caption("Live terminal zone allocations tracking layout parameters.")
    
    records_df = load_bookings()
    live_reservations = len(records_df)

    # HTML/CSS structural card rows that match your exact layout goals
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="zone-box zone-a">
            <h3>🟢 ZONE A</h3>
            <p>FACULTY ACCESS OVERRIDE</p>
            <div class="metric-val">78</div>
            <small>Available Slots</small>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        student_slots = max(0, 117 - live_reservations)
        st.markdown(f"""
        <div class="zone-box zone-b">
            <h3>🔵 ZONE B</h3>
            <p>ACTIVE STUDENT LOGINS</p>
            <div class="metric-val">{student_slots}</div>
            <small>Available Slots (-{live_reservations} filled)</small>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="zone-box zone-c">
            <h3>🟡 ZONE C</h3>
            <p>GUEST VISITORS</p>
            <div class="metric-val">100</div>
            <small>Available Slots</small>
        </div>
        """, unsafe_allow_html=True)


# ==========================================================
# PAGE 3: CENTRAL REPOSITORIES & DATA MONITORING AUDITS
# ==========================================================
elif nav_selection == "System Dashboard":
    st.title("📊 System Audit Dashboard & Analytics")
    st.caption("Permanent operational insights database tracking layout matrices.")
    
    history_data = load_bookings()
    live_reservations = len(history_data)
    utilization = (live_reservations / 300) * 100 if live_reservations > 0 else 0.0

    an1, an2 = st.columns(2)
    with an1:
        st.metric(label="Total Database Storage Records", value=f"{live_reservations} Transactions")
    with an2:
        st.metric(label="Overall Terminal Load Factor", value=f"{utilization:.1f}%")

    if utilization > 85.0:
        st.error("⚠️ Critical Alert: Operations crossing safety capacity ceilings.")
    else:
        st.success("✅ Operational Parameter Check: Infrastructure execution framework entirely stable.")

    st.write("---")
    st.subheader("📋 Historic Audit Records Log (Persistent Database)")
    
    if not history_data.empty:
        st.dataframe(
            history_data.iloc[::-1],
            column_config={
                "vehicle_number": "Vehicle License ID",
                "role": "Profile Clear Tier",
                "zone": "Allocated Grid Zone",
                "timestamp": "System Timestamp Log"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("System storage is completely fresh. No active entries logged in SQL cache file databases.")