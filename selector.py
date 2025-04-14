import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pump Selector", layout="wide")
st.title("🛠️ Pump Selection Tool")

# ✅ Load the local CSV file
try:
    pumps = pd.read_csv("Pump Selection Data.csv")
except Exception as e:
    st.error(f"❌ Failed to load local CSV file: {e}")
    st.stop()

# --- UI for User Input ---
col1, col2 = st.columns(2)

with col1:
    frequency = st.selectbox("* Frequency:", sorted(pumps["Frequency (Hz)"].dropna().unique()))
    flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
    flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0)

with col2:
    category = st.selectbox("* Category:", ["All Categories"] + sorted(pumps["Category"].dropna().unique()))
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
        # Make model number clickable
        results = filtered_pumps.copy()

        def make_clickable_model(row):
            return f'<a href="{row["Product Link"]}" target="_blank">{row["Model No."]}</a>'

        results["Model No."] = results.apply(make_clickable_model, axis=1)

        # Show full table with clickable model numbers
        st.write(results.to_html(escape=False, index=False), unsafe_allow_html=True)

        # --- Draw Pump Curve-style Graph ---
        st.subheader("📈 Pump Curve Comparison")
        fig, ax = plt.subplots()

        for _, row in filtered_pumps.iterrows():
            model = row["Model No."]
            flow = row["Max Flow (LPM)"]
            head = row["Max Head (M)"]
            ax.plot([0, flow], [head, 0], label=model, linewidth=1.5)

        ax.scatter([flow_lpm], [head_m], color='red', marker='x', s=100, label='User Requirement')

        ax.set_xlabel("Flow (LPM)")
        ax.set_ylabel("Head (m)")
        ax.set_title("Pump Performance Curves")
        ax.grid(True)
        ax.legend(fontsize="small", loc="upper right")

        st.pyplot(fig)

    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
