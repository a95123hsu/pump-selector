import streamlit as st
import pandas as pd

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# -- Custom Header with Logo and Title --
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
    st.error(f"❌ Failed to load local CSV file: {e}")
    st.stop()

# --- Application Input (Auto Fill) ---
st.markdown("### 🏢 Application Input (Auto Fill)")
num_floors = st.number_input("Number of Floors", min_value=0, step=1)
num_faucets = st.number_input("Number of Faucets", min_value=0, step=1)

# Auto-calculate TDH and Flow from application inputs
auto_tdh = num_floors * 3.5  # m
auto_flow = num_faucets * 15  # LPM

# --- UI Inputs (Vertical Layout) ---
st.markdown("### Manual Input")
frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))
category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))
flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0, value=float(auto_flow) if auto_flow > 0 else 0.0)
head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0, value=float(auto_tdh) if auto_tdh > 0 else 0.0)

# -- Search Form with Custom Green Button --
with st.form("search_form"):
    submitted = st.form_submit_button("🔍 Search")

# -- Run Search Logic --
if submitted:
    filtered_pumps = pumps.copy()
    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]

    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Convert flow units to LPM
    flow_lpm = flow_value
    if flow_unit == "L/sec": flow_lpm *= 60
    elif flow_unit == "m³/hr": flow_lpm = flow_value * 1000 / 60
    elif flow_unit == "m³/min": flow_lpm *= 1000
    elif flow_unit == "US gpm": flow_lpm *= 3.785

    # Convert head units to meters
    head_m = head_value if head_unit == "m" else head_value * 0.3048

    # Apply flow/head filters
    if flow_value > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Flow (LPM)"] >= flow_lpm]
    if head_value > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Head (M)"] >= head_m]

    st.subheader("✅ Matching Pumps")

    if not filtered_pumps.empty:
        results = filtered_pumps.copy()

        # Make Product Link clickable
        def make_clickable_link(url):
            return f'<a href="{url}" target="_blank">🔗 View Product</a>'

        results["Product Link"] = results["Product Link"].apply(make_clickable_link)

        # Display full table with clickable Product Link
        st.write(results.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
