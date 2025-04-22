import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# --- Supabase Configuration ---
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
@st.cache_resource
def init_connection():
    return create_client(supabase_url, supabase_key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.stop()

# --- Load Pump Data ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_pump_data():
    try:
        # Use pagination to fetch all records instead of a single query with limit
        all_records = []
        page_size = 1000
        current_page = 0
        
        while True:
            response = supabase.table("pump_selection_data").select("*") \
                              .range(current_page * page_size, (current_page + 1) * page_size - 1) \
                              .execute()
            
            if not response.data:
                break
                
            all_records.extend(response.data)
            current_page += 1
            
            if len(response.data) < page_size:
                break
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load data from Supabase: {e}")
        # Fallback to CSV if Supabase fetch fails
        try:
            df = pd.read_csv("Pump Selection Data.csv")
            return df
        except Exception as csv_error:
            st.error(f"❌ Failed to load CSV file: {csv_error}")
            return pd.DataFrame()

# Load the data
pumps = load_pump_data()

if pumps.empty:
    st.error("❌ No pump data available. Please check your Supabase connection or CSV file.")
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
    st.markdown("<h1 style='color: #0057B8; margin: 0; padding-left: 15px;'>Hung Pump</h1>", unsafe_allow_html=True)

# --- Title and Reset Button ---
st.title("Pump Selection Tool")

# Reset All Inputs Button
reset_clicked = st.button("🔄 Reset All Inputs", key="reset_button", help="Reset all fields to default", type="secondary")
if reset_clicked:
    for key, val in default_values.items():
        st.session_state[key] = val

# Apply custom styling
st.markdown("""
<style>
button[data-testid="baseButton-secondary"] {
    background-color: #e63946;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- Step 1: Initial Selection ---
st.markdown("### 🔧 Step 1: Select Basic Criteria")

# Clean up Category values to ensure consistent filtering
if "Category" in pumps.columns:
    # Convert all category values to strings and strip whitespace
    pumps["Category"] = pumps["Category"].astype(str).str.strip()
    # Replace NaN, None, etc. with empty string for consistent handling
    pumps["Category"] = pumps["Category"].replace(["nan", "None", "NaN"], "")
    # Get unique categories excluding blank/empty values
    unique_categories = [c for c in pumps["Category"].unique() if c and c.strip() and c.lower() not in ["nan", "none"]]
    category_options = ["All Categories"] + sorted(unique_categories)
else:
    category_options = ["All Categories"]

category = st.selectbox("* Category:", category_options)

# Use dropna() to handle missing values in frequency and phase
if "Frequency (Hz)" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Frequency (Hz)"] = pd.to_numeric(pumps["Frequency (Hz)"], errors='coerce')
    freq_options = sorted(pumps["Frequency (Hz)"].dropna().unique())
    frequency = st.selectbox("* Frequency (Hz):", ["Select..."] + freq_options)
else:
    frequency = st.selectbox("* Frequency (Hz):", ["Select..."])

if "Phase" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Phase"] = pd.to_numeric(pumps["Phase"], errors='coerce')
    # Filter to only include 1 and 3 phase options that exist in the data
    phase_options = [p for p in sorted(pumps["Phase"].dropna().unique()) if p in [1, 3]]
    phase = st.selectbox("* Phase:", ["Select..."] + phase_options)
else:
    phase = st.selectbox("* Phase:", ["Select...", 1, 3])

if frequency == "Select..." or phase == "Select...":
    st.warning("Please select Frequency and Phase to proceed.")
    st.stop()

# --- 🏢 Application Section - Only show when Booster is selected ---
if category == "Booster":
    st.markdown("### 🏢 Application Input")
    st.caption("💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM")

    num_floors = st.number_input("Number of Floors", min_value=0, step=1, key="floors")
    num_faucets = st.number_input("Number of Faucets", min_value=0, step=1, key="faucets")
    
    # Calculate auto values for Booster application
    auto_flow = num_faucets * 15
    auto_tdh = num_floors * 3.5
else:
    # Reset these values when Booster is not selected
    auto_flow = 0
    auto_tdh = 0
    num_floors = 0
    num_faucets = 0

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
# Update auto calculations considering both booster and pond drainage
if category == "Booster":
    auto_flow = max(num_faucets * 15, pond_lpm)
    auto_tdh = max(num_floors * 3.5, height)
else:
    auto_flow = pond_lpm
    auto_tdh = underground_depth if underground_depth > 0 else height

# --- 🎛️ Manual Input Section ---
st.markdown("### Manual Input")

flow_unit = st.radio("Flow Unit", ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"], horizontal=True)
flow_value = st.number_input("Flow Value", min_value=0.0, step=10.0, value=float(auto_flow), key="flow_value")

head_unit = st.radio("Head Unit", ["m", "ft"], horizontal=True)
head_value = st.number_input("Total Dynamic Head (TDH)", min_value=0.0, step=1.0, value=float(auto_tdh), key="head_value")

# --- Estimated application from manual ---
# Only show estimated application metrics when Booster is selected
if category == "Booster":
    estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
    estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0

    st.markdown("### 💡 Estimated Application (based on Manual Input)")
    col1, col2 = st.columns(2)
    col1.metric("Estimated Floors", estimated_floors)
    col2.metric("Estimated Faucets", estimated_faucets)

# --- Result Display Limit ---
st.markdown("### 📊 Result Display Control")
result_percent = st.slider("Show Top Percentage of Results", min_value=5, max_value=100, value=100, step=1)

# --- Search Logic ---
if st.button("🔍 Search"):
    filtered_pumps = pumps.copy()
    
    # Ensure Frequency and Phase are treated properly - improved error handling
    try:
        # Convert types appropriately with error handling before filtering
        filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
        filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
        
        # Apply frequency filter with improved type handling
        if isinstance(frequency, str) and frequency != "Select...":
            try:
                freq_value = float(frequency)
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == freq_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
        elif frequency != "Select...":
            filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
            
        # Apply phase filter with improved type handling
        if isinstance(phase, str) and phase != "Select...":
            try:
                phase_value = int(phase)
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
        elif phase != "Select...":
            filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == int(phase)]
    except Exception as e:
        st.error(f"Error filtering by frequency/phase: {e}")
        # If filtering fails, show a message but continue with other filters

    # Apply category filter
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

    # Ensure numeric conversion for flow and head with improved handling
    # Replace NaN with 0 to avoid comparison issues
    filtered_pumps["Max Flow (LPM)"] = pd.to_numeric(filtered_pumps["Max Flow (LPM)"], errors="coerce").fillna(0)
    filtered_pumps["Max Head (M)"] = pd.to_numeric(filtered_pumps["Max Head (M)"], errors="coerce").fillna(0)

    # Apply filters with safe handling of missing values
    if flow_lpm > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Flow (LPM)"] >= flow_lpm]
    if head_m > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Max Head (M)"] >= head_m]
    if particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
        # Convert to numeric first to handle potential string values
        filtered_pumps["Pass Solid Dia(mm)"] = pd.to_numeric(filtered_pumps["Pass Solid Dia(mm)"], errors="coerce").fillna(0)
        filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]

    st.subheader("✅ Matching Pumps")
    st.write(f"Found {len(filtered_pumps)} matching pumps")

    if not filtered_pumps.empty:
        results = filtered_pumps.copy()
        
        # Sort by relevant criteria for better user experience
        if "Max Flow (LPM)" in results.columns and "Max Head (M)" in results.columns:
            # Properly handle data types before calculations
            results["Max Flow (LPM)"] = pd.to_numeric(results["Max Flow (LPM)"], errors="coerce").fillna(0)
            results["Max Head (M)"] = pd.to_numeric(results["Max Head (M)"], errors="coerce").fillna(0)
            
            # Sort by closest match to requested flow and head
            results["Flow Difference"] = abs(results["Max Flow (LPM)"] - flow_lpm)
            results["Head Difference"] = abs(results["Max Head (M)"] - head_m)
            
            # Weight differences properly and handle NaN values
            results["Match Score"] = results["Flow Difference"] + results["Head Difference"]
            results = results.sort_values("Match Score")
            
            # Remove temporary columns used for sorting
            results = results.drop(columns=["Flow Difference", "Head Difference", "Match Score"])
        
        # Default sorting by DB ID (ascending)
        if "id" in results.columns:
            results = results.sort_values("id")
        elif "ID" in results.columns:
            results = results.sort_values("ID")
        
        # Sort by DB ID first, then apply percentage filter
        if "DB ID" in results.columns:
            results = results.sort_values("DB ID")
        elif "id" in results.columns:
            results = results.sort_values("id")
        elif "ID" in results.columns:
            results = results.sort_values("ID")
        
        # Apply percentage limit after sorting by DB ID
        max_to_show = max(1, int(len(results) * (result_percent / 100)))
        displayed_results = results.head(max_to_show).copy()
        
        # Show all data without pagination
        if len(displayed_results) > 0:
            st.write(f"Showing all {len(displayed_results)} results")
            
        # No pagination - use entire dataset
        start_idx = 0
        end_idx = len(displayed_results)
        
        # Create column configuration for product links and proper formatting
        column_config = {}
        
        # Configure the ID column for default sorting if it exists
        id_column = None
        if "id" in displayed_results.columns:
            id_column = "id"
            column_config["id"] = st.column_config.NumberColumn(
                "ID",
                help="Database ID",
                format="%d"
            )
        elif "ID" in displayed_results.columns:
            id_column = "ID"
            column_config["ID"] = st.column_config.NumberColumn(
                "ID",
                help="Database ID",
                format="%d"
            )
        
        # Configure the Product Link column if it exists
        if "Product Link" in displayed_results.columns:
            column_config["Product Link"] = st.column_config.LinkColumn(
                "Product Link",
                help="Click to view product details",
                display_text="View Product"
            )
        
        # Better formatting for numeric columns
        if "Max Flow (LPM)" in displayed_results.columns:
            column_config["Max Flow (LPM)"] = st.column_config.NumberColumn(
                "Max Flow (LPM)",
                help="Maximum flow rate in liters per minute",
                format="%.1f LPM"
            )
        
        if "Max Head (M)" in displayed_results.columns:
            column_config["Max Head (M)"] = st.column_config.NumberColumn(
                "Max Head (M)",
                help="Maximum head in meters",
                format="%.1f m"
            )
        
        # We don't need to sort again since it's already sorted
        # Display the results
        st.write("### Matching Pumps Results")
        
        st.data_editor(
            displayed_results.iloc[start_idx:end_idx],
            column_config=column_config,
            hide_index=True,
            disabled=True,
            use_container_width=True
        )
    else:
        st.warning("⚠️ No pumps match your criteria. Try adjusting the parameters.")
