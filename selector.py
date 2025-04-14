import streamlit as st
import pandas as pd

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# -- Custom Header with Logo and Title --
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("https://www.hungpump.com/images/340357", width=160)  # ✅ Logo enlarged here
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

# -- UI Inputs (Vertical Layout) --
frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))
category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))
flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0)
head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0)

# -- Search Logic --
with st.form("search_form"):
    submitted = st.form_submit_button(
        label="🔍 Search"
    )
    st.markdown("""
        <style>
            div.stButton > button:first-child {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                font-weight: bold;
                transition: 0.2s;
            }
            div.stButton > button:first-child:hover {
                background-color: #218838;
            }
        </style>
    """, unsafe_allow_html=True)

    filtered_pumps = pumps.copy()
    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]

    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Convert units
    flow_lpm = flow_value
    if flow_unit == "L/sec":
        flow_lpm *= 60
    elif flow_unit == "m³/hr":
        flow_lpm = flow_value * 1000 / 60
    elif flow_unit == "m³/min":
        flow_lpm *= 1000
    elif flow_unit == "US gpm":
        flow_lpm *= 3.785

    head_m = head_value if head_unit == "m" else head_value * 0.3048

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

        # Display table with clickable Product Link
        st.write(results.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
