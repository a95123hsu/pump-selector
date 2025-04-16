import streamlit as st
import pandas as pd

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# -- Header with Logo and Title --
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

# -- Load CSV --
try:
    pumps = pd.read_csv("Pump Selection Data.csv")
except Exception as e:
    st.error(f"❌ Failed to load CSV file: {e}")
    st.stop()

# --- Session state for clearing inputs ---
def clear_fields(keys):
    for k in keys:
        st.session_state[k] = 0 if 'value' not in k else 0.0

# --- 🏢 Application Section ---
st.markdown("### 🏢 Application Input")
st.caption("💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM")

if st.button("🧹 Clear Application Input"):
    clear_fields(["floors", "faucets"])

num_floors = st.number_input("Number of Floors", min_value=0, step=1, key="floors")
num_faucets = st.number_input("Number of Faucets", min_value=0, step=1, key="faucets")

# --- 🌊 Pond Drainage ---
st.markdown("### 🌊 Pond Drainage")

if st.button("🧹 Clear Pond Input"):
    clear_fields(["length", "width", "height", "drain_time_hr"])
    st.session_state["drain_time_hr"] = 0.01

length = st.number_input("Pond Length (m)", min_value=0.0, step=0.1, key="length")
width = st.number_input("Pond Width (m)", min_value=0.0, step=0.1, key="width")
height = st.number_input("Pond Height (m)", min_value=0.0, step=0.1, key="height")
drain_time_hr = st.number_input("Drain Time (hours)", min_value=0.01, step=0.1, key="drain_time_hr")

pond_volume = length * width * height * 1000  # liters
drain_time_min = drain_time_hr * 60
pond_lpm = pond_volume / drain_time_min if drain_time_min > 0 else 0

if pond_volume > 0:
    st.caption(f"📏 Pond Volume: {round(pond_volume)} L")
if pond_lpm > 0:
    st.success(f"💧 Required Flow to drain pond: {round(pond_lpm)} LPM")

# --- Underground depth and particle size ---
underground_depth = st.number_input("Pump Depth Below Ground (m)", min_value=0.0, step=0.1)
particle_size = st.number_input("Max Particle Size (mm)", min_value=0.0, step=1.0, key="particle_size")

# --- Calculated Values ---
auto_flow = max(num_faucets * 15, pond_lpm)
auto_tdh = underground_depth if underground_depth > 0 else max(num_floors * 3.5, height)

# --- 🎛️ Manual Input Section ---
st.markdown("### Result Filter")

if st.button("🧹 Clear Manual Input"):
    clear_fields(["flow_value", "head_value", "particle_size", "floors", "faucets"])

category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))
frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))
phase = st.selectbox("* Phase:", [1, 3])  # Single-phase or Three-phase

flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0, value=float(auto_flow) if auto_flow > 0 else 0.0, key="flow_value")

head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0, value=float(auto_tdh) if auto_tdh > 0 else 0.0, key="head_value")

# --- Estimated from manual input ---
estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0

st.markdown("### 💡 Estimated Application (based on Manual Input)")
st.caption("These are the estimated values if you're only using flow & head:")

col1, col2 = st.columns(2)
col1.metric("Estimated Floors", estimated_floors)
col2.metric("Estimated Faucets", estimated_faucets)

# --- Result limit ---
st.markdown("### 📊 Result Display Control")
result_percent = st.slider("Show Top Percentage of Results", min_value=5, max_value=100, value=100, step=1)

# --- Search Logic ---
if st.button("🔍 Search"):
    filtered_pumps = pumps.copy()
    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]

    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Filter by Phase
    filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]

    # Ensure the "Max Flow (LPM)" column is numeric, converting non-numeric values to NaN
    filtered_pumps["Max Flow (LPM)"] = pd.to_numeric(filtered_pumps["Max Flow (LPM)"], errors="coerce")

    # Convert flow to LPM
    flow_lpm = flow_value
    if flow_unit == "L/sec": flow_lpm *= 60
    elif flow_unit == "m³/hr": flow_lpm = flow_value * 1000 / 60
    elif flow_unit == "m³/min": flow_lpm *= 1000
    elif flow_unit == "US gpm": flow_lpm *= 3.785

    # Convert head to meters
    head_m = head_value if head_unit == "m" else head_value * 0.3048

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

        results["Product Link"] = results["Product Link"].apply(make_clickable_link)
        max_to_show = max(1, int(len(results) * (result_percent / 100)))
        st.write(results.head(max_to_show).to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
