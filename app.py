st.markdown("""
<style>

/* Background */
.main {
    background-color: #0f1117;
    color: white;
}

/* Cards */
div[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #4CAF50, #00C6FF);
    color: white;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #00C6FF;
}

/* Section headers */
h1, h2, h3 {
    color: #00C6FF;
}

</style>
""", unsafe_allow_html=True)
st.subheader("🎟 Smart Reservation Flow")

step = st.radio("Step", ["1. Vehicle", "2. Zone", "3. Time", "4. Confirm"])

if step == "1. Vehicle":
    vehicle = st.text_input("Enter Vehicle Number")

elif step == "2. Zone":
    zone = st.selectbox("Choose Zone", ["A", "B", "C", "D"])

elif step == "3. Time":
    time_slot = st.selectbox("Time Slot", ["8-10", "10-12", "12-2", "2-4"])

elif step == "4. Confirm":
    if st.button("Generate Smart Pass"):
        with st.spinner("Generating QR Pass..."):
            time.sleep(2)
        st.success("PASS GENERATED: MU-" + str(random.randint(1000,9999)))
        st.balloons()
        st.subheader("📡 Live Campus Zones")

zones = {
    "Zone A (Faculty)": random.randint(60,95),
    "Zone B (Students)": random.randint(40,90),
    "Zone C (Hostel)": random.randint(30,85),
    "Zone D (Visitors)": random.randint(20,70),
}

for z, val in zones.items():
    if val > 80:
        st.error(f"{z} → {val}% FULL 🔴")
    elif val > 50:
        st.warning(f"{z} → {val}% BUSY 🟡")
    else:
        st.success(f"{z} → {val}% FREE 🟢")
