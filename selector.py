import streamlit as st
import pandas as pd

st.title("🛠️ Pump Selection Tool")

# ✅ Load the local CSV file
try:
    pumps = pd.read_csv("Pump Selection Data.csv")
except Exception as e:
    st.error(f"❌ Failed to load local CSV file: {e}")
    st.stop()

# Frequency Selection
frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))

# Category Selection
category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))

# Flow Input
st.write("* Flow Requirement:")
flow_unit = st.radio("Select Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow", min_value=0, step=10)

# Head Input
st.write("* Total Dynamic Head (TDH):")
head_unit = st.radio("Select Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("TDH", min_value=0, step=1)

# Search Button
if st.button("🔍 Search"):
    filtered_pumps = pumps.copy()

    # Frequency filter
    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]

    # Category filter
    if category != "All Categories":
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Flow conversion
    if flow_value > 0:
        flow_lpm = flow_value
        if flow_unit == "L/sec":
            flow_lpm = flow_value * 60
        elif flow_unit == "m³/hr":
            flow_lpm = flow_value * 1000 / 60
        elif flow_unit == "m³/min":
            flow_lpm = flow_value * 1000
        elif flow_unit == "US gpm":
            flow_lpm = flow_value * 3.785
        filtered_pumps = filtered_pumps[filtered_pumps["Max Flow (LPM)"] >= flow_lpm]

    # Head conversion
    if head_value > 0:
        head_m = head_value if head_unit == "m" else head_value * 0.3048
        filtered_pumps = filtered_pumps[filtered_pumps["Max Head (M)"] >= head_m]

    st.subheader("✅ Matching Pumps")

    if not filtered_pumps.empty:
        # Make product link clickable
        def make_clickable(url):
            return f'<a href="{url}" target="_blank">🔗 View Product</a>'

        results = filtered_pumps.copy()
        results["Product Link"] = results["Product Link"].apply(make_clickable)

        # Optional: Show selected columns only (you can adjust this list)
        columns_to_display = [
            "Model No.", "Frequency (Hz)", "Power(KW)", "Max Flow (LPM)",
            "Max Head (M)", "Category", "Product Link"
        ]
        results = results[columns_to_display]

        # Show table with HTML links
        st.write(results.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
