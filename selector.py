import streamlit as st
import pandas as pd

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# --- Load CSV ---
try:
    pumps = pd.read_csv("Pump Selection Data.csv")
except Exception as e:
    st.error(f"❌ Failed to load CSV file: {e}")
    st.stop()

# --- Default values ---
default_values = {
    "floors": 0, "faucets": 0,
    "length": 0.0, "width": 0.0, "height": 0.0,
    "drain_time_hr": 0.01,
    "underground_depth": 0.0,
    "particle_size": 0.0,
    "flow_value": 0.0, "head_value": 0.0
}

# --- Initialize session_state ---
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Header ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("https://www.hungpump.com/images/340357", width=160)
with col_title:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 100%; padding-left: 15px;'>
            <h1 style='color: #0057B8; margin: 0;'>Hung Pump</h1>
        </div>
    """, unsafe_allow_html=True)

st.title("Pump Selection Tool")

# --- Step 1: Initial Selection ---
st.markdown("### 🔧 Step 1: Select Basic Criteria")

category_options = ["All Categories"] + sorted(pumps["Category"].dropna().unique())
category = st.selectbox("* Category:", category_options)
frequency = st.selectbox("* Frequency (Hz):", ["Select..."] + sorted(pumps["Frequency (Hz)"].dropna().unique()))
phase = st.selectbox("* Phase:", ["Select...", 1, 3])

if frequency == "Select..." or phase == "Select...":
    st.warning("Please select Frequency and Phase to proceed.")
    st.stop()

# --- 🏢 Application Section ---
st.markdown("### 🏢 Application Input")
st.caption("💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM")

num_floors = st.number_input("Number of Floors", min_value=0, step=1, key="floors")
num_faucets = st.number_input("Number of Faucets", min_value=0, step=1, key="faucets")

# --- 🌊 Pond Drainage ---
st.markdown("### 🌊 Pond Drainage")

length = st.number_input("Pond Length (m)", min_value=0.0, step=0.1, key="length")
width = st.number_input("Pond Width (m)", min_value=0.0, step=0.1, key="width")
height = st.number_input("Pond Height (m)", min_value=0.0, step=0.1, key="height")
drain_time_hr = st.number_input("Drain Time (hours)", min_value=0.01, step=0.1, key="drain_time_hr")

pond_volume = length * width * height * 1000
drain_time_min = drain_time_hr * 60
pond_lpm = pond_volume / drain_time_min if drain_time_min > 0 else 0

if pond_volume > 0:
    st.caption(f"📏 Pond Volume: {round(pond_volume)} L")
if pond_lpm > 0:
    st.success(f"💧 Required Flow to drain pond: {round(pond_lpm)} LPM")

# --- Underground and particle size ---
underground_depth = st.number_input("Pump Depth Below Ground (m)", min_value=0.0, step=0.1, key="underground_depth")
particle_size = st.number_input("Max Particle Size (mm)", min_value=0.0, step=1.0, key="particle_size")

# --- Auto calculations ---
auto_flow = max(num_faucets * 15, pond_lpm)
auto_tdh = underground_depth if underground_depth > 0 else max(num_floors * 3.5, height)

# --- 🎛️ Manual Input Section ---
st.markdown("### Manual Input")

flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0, value=float(auto_flow), key="flow_value")

head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0, value=float(auto_tdh), key="head_value")

# --- Estimated application from manual ---
estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0

st.markdown("### 💡 Estimated Application (based on Manual Input)")
col1, col2 = st.columns(2)
col1.metric("Estimated Floors", estimated_floors)
col2.metric("Estimated Faucets", estimated_faucets)

# --- 🔄 Reset Button ---
if st.button("🔄 Reset All Inputs"):
    changed = False
    for key, val in default_values.items():
        if st.session_state.get(key) != val:
            st.session_state[key] = val
            changed = True
    if changed:
        st.experimental_rerun()
    else:
        st.info("Inputs are already at default values.")

# --- Result Display Limit ---
st.markdown("### 📊 Result Display Control")
result_percent = st.slider("Show Top Percentage of Results", min_value=5, max_value=100, value=100, step=5)

# --- Search Logic ---
if st.button("🔍 Search"):
    filtered_pumps = pumps.copy()
    filtered_pumps = filtered_pumps[
        (filtered_pumps["Frequency (Hz)"] == frequency) &
        (filtered_pumps["Phase"] == int(phase))
    ]

    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Convert flow to LPM
    flow_lpm = flow_value
    if flow_unit == "L/sec": flow_lpm *= 60
    elif flow_unit == "m³/hr": flow_lpm = flow_value * 1000 / 60
    elif flow_unit == "m³/min": flow_lpm *= 1000
    elif flow_unit == "US gpm": flow_lpm *= 3.785

    # Convert head to meters
    head_m = head_value if head_unit == "m" else head_value * 0.3048

    # Ensure numeric conversion
    filtered_pumps["Max Flow (LPM)"] = pd.to_numeric(filtered_pumps["Max Flow (LPM)"], errors="coerce")

    # Apply filters
    if flow_lpm > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Flow (LPM)"] >= flow_lpm]
    if head_m > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Head (M)"] >= head_m]
    if particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
        filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]

    st.subheader("✅ Matching Pumps")

    if not filtered_pumps.empty:
        results = filtered_pumps.copy()

        def make_clickable_link(url):
            return f'<a href="{url}" target="_blank">🔗 View Product</a>'

        if "Product Link" in results.columns:
            results["Product Link"] = results["Product Link"].apply(make_clickable_link)

        max_to_show = max(1, int(len(results) * (result_percent / 100)))
        st.write(results.head(max_to_show).to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
