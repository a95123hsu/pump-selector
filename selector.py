import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pump Selector", layout="wide")
st.title("🛠️ Pump Selection Tool")

# ✅ Load the local CSV file
try:
    pumps = pd.read_csv("Pump Selection Data.csv")
except Exception as e:
    st.error(f"❌ Failed to load local CSV file: {e}")
    st.stop()

# --- UI Inputs (Vertical Layout) ---
frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))

category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))

flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0)

head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0)

# --- Search Button ---
if st.button("🔍 Search"):
    filtered_pumps = pumps.copy()

    # Filter frequency
    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]

    # Filter category
    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Convert flow to LPM
    flow_lpm = flow_value
    if flow_unit == "L/sec":
        flow_lpm = flow_value * 60
    elif flow_unit == "m³/hr":
        flow_lpm = flow_value * 1000 / 60
    elif flow_unit == "m³/min":
        flow_lpm = flow_value * 1000
    elif flow_unit == "US gpm":
        flow_lpm = flow_value * 3.785

    # Convert head to meters
    head_m = head_value if head_unit == "m" else head_value * 0.3048

    # Apply flow/head filters
    if flow_value > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Flow (LPM)"] >= flow_lpm]
    if head_value > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Head (M)"] >= head_m]

    st.subheader("✅ Matching Pumps")

    if not filtered_pumps.empty:
        results = filtered_pumps.copy()

        # Make Model No. clickable using Product Link
        def make_clickable_model(row):
            return f'<a href="{row["Product Link"]}" target="_blank">{row["Model No."]}</a>'

        results["Model No."] = results.apply(make_clickable_model, axis=1)

        # Remove Product Link column
        if "Product Link" in results.columns:
            results.drop(columns=["Product Link"], inplace=True)

        # Show table with clickable Model No.
        st.write(results.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
