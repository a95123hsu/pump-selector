import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Language Support ---
# Translation dictionary
translations = {
    "English": {
        # App title and headers
        "Hung Pump": "Hung Pump",
        "Pump Selection Tool": "Pump Selection Tool",
        "Data loaded": "Data loaded: {n_records} records | Last update: {timestamp}",
        
        # Buttons
        "Refresh Data": "🔄 Refresh Data",
        "Reset Inputs": "🔄 Reset Inputs",
        "Search": "🔍 Search",
        
        # Step 1
        "Step 1": "### 🔧 Step 1: Select Basic Criteria",
        "Category": "* Category:",
        "Frequency": "* Frequency (Hz):",
        "Phase": "* Phase:",
        "Select...": "Select...",
        "All Categories": "All Categories",
        
        # Application section
        "Application Input": "### 🏢 Application Input",
        "Floor Faucet Info": "💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM",
        "Number of Floors": "Number of Floors",
        "Number of Faucets": "Number of Faucets",
        
        # Pond drainage
        "Pond Drainage": "### 🌊 Pond Drainage",
        "Pond Length": "Pond Length (m)",
        "Pond Width": "Pond Width (m)",
        "Pond Height": "Pond Height (m)",
        "Drain Time": "Drain Time (hours)",
        "Pond Volume": "📏 Pond Volume: {volume} L",
        "Required Flow": "💧 Required Flow to drain pond: {flow} LPM",
        
        # Underground
        "Pump Depth": "Pump Depth Below Ground (m)",
        "Particle Size": "Max Particle Size (mm)",
        
        # Manual Input
        "Manual Input": "### Manual Input",
        "Flow Unit": "Flow Unit",
        "Flow Value": "Flow Value",
        "Head Unit": "Head Unit",
        "TDH": "Total Dynamic Head (TDH)",
        
        # Estimated application
        "Estimated Application": "### 💡 Estimated Application (based on Manual Input)",
        "Estimated Floors": "Estimated Floors",
        "Estimated Faucets": "Estimated Faucets",
        
        # Results
        "Result Display": "### 📊 Result Display Control",
        "Show Percentage": "Show Top Percentage of Results",
        "Matching Pumps": "✅ Matching Pumps",
        "Found Pumps": "Found {count} matching pumps",
        "Matching Results": "### Matching Pumps Results",
        "Showing Results": "Showing all {count} results",
        
        # Flow units
        "L/min": "L/min",
        "L/sec": "L/sec",
        "m³/hr": "m³/hr",
        "m³/min": "m³/min",
        "US gpm": "US gpm",
        
        # Head units
        "m": "m",
        "ft": "ft",
        
        # Warnings & Errors
        "Select Warning": "Please select Frequency and Phase to proceed.",
        "No Matches": "⚠️ No pumps match your criteria. Try adjusting the parameters.",
        "Failed Connection": "❌ Failed to connect to Supabase: {error}",
        "Failed Data": "❌ Failed to load data from Supabase: {error}",
        "Failed CSV": "❌ Failed to load CSV file: {error}",
        "No Data": "❌ No pump data available. Please check your Supabase connection or CSV file."
    },
    "繁體中文": {
        # App title and headers
        "Hung Pump": "宏泵",
        "Pump Selection Tool": "水泵選型工具",
        "Data loaded": "已載入資料: {n_records} 筆記錄 | 最後更新: {timestamp}",
        
        # Buttons
        "Refresh Data": "🔄 刷新資料",
        "Reset Inputs": "🔄 重置輸入",
        "Search": "🔍 搜尋",
        
        # Step 1
        "Step 1": "### 🔧 步驟一: 選擇基本條件",
        "Category": "* 類別:",
        "Frequency": "* 頻率 (赫茲):",
        "Phase": "* 相數:",
        "Select...": "請選擇...",
        "All Categories": "所有類別",
        
        # Application section
        "Application Input": "### 🏢 應用輸入",
        "Floor Faucet Info": "💡 每樓層 = 3.5 米揚程 | 每水龍頭 = 15 LPM",
        "Number of Floors": "樓層數量",
        "Number of Faucets": "水龍頭數量",
        
        # Pond drainage
        "Pond Drainage": "### 🌊 池塘排水",
        "Pond Length": "池塘長度 (米)",
        "Pond Width": "池塘寬度 (米)",
        "Pond Height": "池塘高度 (米)",
        "Drain Time": "排水時間 (小時)",
        "Pond Volume": "📏 池塘體積: {volume} 升",
        "Required Flow": "💧 所需排水流量: {flow} LPM",
        
        # Underground
        "Pump Depth": "幫浦地下深度 (米)",
        "Particle Size": "最大固體顆粒尺寸 (毫米)",
        
        # Manual Input
        "Manual Input": "### 手動輸入",
        "Flow Unit": "流量單位",
        "Flow Value": "流量值",
        "Head Unit": "揚程單位",
        "TDH": "總動態揚程 (TDH)",
        
        # Estimated application
        "Estimated Application": "### 💡 估計應用 (基於手動輸入)",
        "Estimated Floors": "估計樓層",
        "Estimated Faucets": "估計水龍頭",
        
        # Results
        "Result Display": "### 📊 結果顯示控制",
        "Show Percentage": "顯示前百分比的結果",
        "Matching Pumps": "✅ 符合條件的幫浦",
        "Found Pumps": "找到 {count} 個符合的幫浦",
        "Matching Results": "### 符合幫浦結果",
        "Showing Results": "顯示全部 {count} 筆結果",
        
        # Flow units
        "L/min": "公升/分鐘",
        "L/sec": "公升/秒",
        "m³/hr": "立方米/小時",
        "m³/min": "立方米/分鐘",
        "US gpm": "美制加侖/分鐘",
        
        # Head units
        "m": "米",
        "ft": "英尺",
        
        # Warnings & Errors
        "Select Warning": "請選擇頻率和相數以繼續。",
        "No Matches": "⚠️ 沒有符合您條件的幫浦。請調整參數。",
        "Failed Connection": "❌ 連接到 Supabase 失敗: {error}",
        "Failed Data": "❌ 從 Supabase 載入資料失敗: {error}",
        "Failed CSV": "❌ 載入 CSV 檔案失敗: {error}",
        "No Data": "❌ 無可用幫浦資料。請檢查您的 Supabase 連接或 CSV 檔案。"
    }
}

# Function to get translated text
def get_text(key, **kwargs):
    if key not in translations[st.session_state.language]:
        # Fallback to English if translation missing
        return translations["English"].get(key, key).format(**kwargs) if kwargs else translations["English"].get(key, key)
    text = translations[st.session_state.language][key]
    return text.format(**kwargs) if kwargs else text

# App config
st.set_page_config(page_title="Pump Selector", layout="wide")

# Initialize language in session state if not already set
if 'language' not in st.session_state:
    st.session_state.language = "English"

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
    st.error(get_text("Failed Connection", error=str(e)))
    st.stop()

# --- Load Pump Data ---
@st.cache_data(ttl=60)  # Cache data for 1 minute instead of 10 minutes for more frequent updates
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
        st.error(get_text("Failed Data", error=str(e)))
        # Fallback to CSV if Supabase fetch fails
        try:
            df = pd.read_csv("Pump Selection Data.csv")
            return df
        except Exception as csv_error:
            st.error(get_text("Failed CSV", error=str(csv_error)))
            return pd.DataFrame()

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
col_logo, col_title, col_lang = st.columns([1, 5, 3])
with col_logo:
    st.image("https://www.hungpump.com/images/340357", width=160)
with col_title:
    st.markdown(f"<h1 style='color: #0057B8; margin: 0; padding-left: 15px;'>{get_text('Hung Pump')}</h1>", unsafe_allow_html=True)
with col_lang:
    # Language selector in the header
    selected_lang = st.selectbox(
        "Language / 語言",
        options=list(translations.keys()),
        index=list(translations.keys()).index(st.session_state.language),
        key="lang_selector"
    )
    # Update language when selector changes
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

# --- Title and Reset Button ---
st.title(get_text("Pump Selection Tool"))

# Load the data
pumps = load_pump_data()

if pumps.empty:
    st.error(get_text("No Data"))
    st.stop()

# Show data freshness information
st.caption(get_text("Data loaded", n_records=len(pumps), timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')))

# Create columns with buttons close together on the left side
col1, col2, col_space = st.columns([1, 1.2, 5.8])

with col1:
    refresh_clicked = st.button(get_text("Refresh Data"), help="Refresh data from database", type="secondary", use_container_width=True)
    if refresh_clicked:
        # Clear cache to force data reload
        st.cache_data.clear()
        # Use st.rerun() instead of the deprecated experimental_rerun
        st.rerun()
    
with col2:
    # Reset All Inputs Button - with shortened text
    reset_clicked = st.button(get_text("Reset Inputs"), key="reset_button", help="Reset all fields to default", type="secondary", use_container_width=True)
    if reset_clicked:
        for key, val in default_values.items():
            st.session_state[key] = val

# Apply custom styling - using the same style for both buttons
st.markdown("""
<style>
button[data-testid="baseButton-secondary"] {
    background-color: #e63946;
    color: white;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# --- Step 1: Initial Selection ---
st.markdown(get_text("Step 1"))

# Clean up Category values to ensure consistent filtering
if "Category" in pumps.columns:
    # Convert all category values to strings and strip whitespace
    pumps["Category"] = pumps["Category"].astype(str).str.strip()
    # Replace NaN, None, etc. with empty string for consistent handling
    pumps["Category"] = pumps["Category"].replace(["nan", "None", "NaN"], "")
    # Get unique categories excluding blank/empty values
    unique_categories = [c for c in pumps["Category"].unique() if c and c.strip() and c.lower() not in ["nan", "none"]]
    category_options = [get_text("All Categories")] + sorted(unique_categories)
else:
    category_options = [get_text("All Categories")]

category = st.selectbox(get_text("Category"), category_options)

# Use dropna() to handle missing values in frequency and phase
if "Frequency (Hz)" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Frequency (Hz)"] = pd.to_numeric(pumps["Frequency (Hz)"], errors='coerce')
    freq_options = sorted(pumps["Frequency (Hz)"].dropna().unique())
    frequency = st.selectbox(get_text("Frequency"), [get_text("Select...")] + freq_options)
else:
    frequency = st.selectbox(get_text("Frequency"), [get_text("Select...")])

if "Phase" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Phase"] = pd.to_numeric(pumps["Phase"], errors='coerce')
    # Filter to only include 1 and 3 phase options that exist in the data
    phase_options = [p for p in sorted(pumps["Phase"].dropna().unique()) if p in [1, 3]]
    phase = st.selectbox(get_text("Phase"), [get_text("Select...")] + phase_options)
else:
    phase = st.selectbox(get_text("Phase"), [get_text("Select..."), 1, 3])

if frequency == get_text("Select...") or phase == get_text("Select..."):
    st.warning(get_text("Select Warning"))
    st.stop()

# --- 🏢 Application Section - Only show when Booster is selected ---
if category == "Booster":
    st.markdown(get_text("Application Input"))
    st.caption(get_text("Floor Faucet Info"))

    num_floors = st.number_input(get_text("Number of Floors"), min_value=0, step=1, key="floors")
    num_faucets = st.number_input(get_text("Number of Faucets"), min_value=0, step=1, key="faucets")
    
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
st.markdown(get_text("Pond Drainage"))

length = st.number_input(get_text("Pond Length"), min_value=0.0, step=0.1, key="length")
width = st.number_input(get_text("Pond Width"), min_value=0.0, step=0.1, key="width")
height = st.number_input(get_text("Pond Height"), min_value=0.0, step=0.1, key="height")
drain_time_hr = st.number_input(get_text("Drain Time"), min_value=0.01, step=0.1, key="drain_time_hr")

pond_volume = length * width * height * 1000
drain_time_min = drain_time_hr * 60
pond_lpm = pond_volume / drain_time_min if drain_time_min > 0 else 0

if pond_volume > 0:
    st.caption(get_text("Pond Volume", volume=round(pond_volume)))
if pond_lpm > 0:
    st.success(get_text("Required Flow", flow=round(pond_lpm)))

# --- Underground and particle size ---
underground_depth = st.number_input(get_text("Pump Depth"), min_value=0.0, step=0.1, key="underground_depth")
particle_size = st.number_input(get_text("Particle Size"), min_value=0.0, step=1.0, key="particle_size")

# --- Auto calculations ---
# Update auto calculations considering both booster and pond drainage
if category == "Booster":
    auto_flow = max(num_faucets * 15, pond_lpm)
    auto_tdh = max(num_floors * 3.5, height)
else:
    auto_flow = pond_lpm
    auto_tdh = underground_depth if underground_depth > 0 else height

# --- 🎛️ Manual Input Section ---
st.markdown(get_text("Manual Input"))

flow_unit_options = ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"]
flow_unit_translated = [get_text(unit) for unit in flow_unit_options]
flow_unit_map = dict(zip(flow_unit_translated, flow_unit_options))

flow_unit = st.radio(get_text("Flow Unit"), flow_unit_translated, horizontal=True)
flow_unit_original = flow_unit_map.get(flow_unit, "L/min")
flow_value = st.number_input(get_text("Flow Value"), min_value=0.0, step=10.0, value=float(auto_flow), key="flow_value")

head_unit_options = ["m", "ft"]
head_unit_translated = [get_text(unit) for unit in head_unit_options]
head_unit_map = dict(zip(head_unit_translated, head_unit_options))

head_unit = st.radio(get_text("Head Unit"), head_unit_translated, horizontal=True)
head_unit_original = head_unit_map.get(head_unit, "m")
head_value = st.number_input(get_text("TDH"), min_value=0.0, step=1.0, value=float(auto_tdh), key="head_value")

# --- Estimated application from manual ---
# Only show estimated application metrics when Booster is selected
if category == "Booster":
    estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
    estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0

    st.markdown(get_text("Estimated Application"))
    col1, col2 = st.columns(2)
    col1.metric(get_text("Estimated Floors"), estimated_floors)
    col2.metric(get_text("Estimated Faucets"), estimated_faucets)

# --- Result Display Limit ---
st.markdown(get_text("Result Display"))
result_percent = st.slider(get_text("Show Percentage"), min_value=5, max_value=100, value=100, step=1)

# --- Search Logic ---
if st.button(get_text("Search")):
    filtered_pumps = pumps.copy()
    
    # Ensure Frequency and Phase are treated properly - improved error handling
    try:
        # Convert types appropriately with error handling before filtering
        filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
        filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
        
        # Apply frequency filter with improved type handling
        if isinstance(frequency, str) and frequency != get_text("Select..."):
            try:
                freq_value = float(frequency)
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == freq_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
        elif frequency != get_text("Select..."):
            filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
            
        # Apply phase filter with improved type handling
        if isinstance(phase, str) and phase != get_text("Select..."):
            try:
                phase_value = int(phase)
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
        elif phase != get_text("Select..."):
            filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == int(phase)]
    except Exception as e:
        st.error(f"Error filtering by frequency/phase: {e}")
        # If filtering fails, show a message but continue with other filters

    # Apply category filter
    if category != get_text("All Categories"):
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]

    # Convert flow to LPM
    flow_lpm = flow_value
    if flow_unit_original == "L/sec": flow_lpm *= 60
    elif flow_unit_original == "m³/hr": flow_lpm = flow_value * 1000 / 60
    elif flow_unit_original == "m³/min": flow_lpm *= 1000
    elif flow_unit_original == "US gpm": flow_lpm *= 3.785

    # Convert head to meters
    head_m = head_value if head_unit_original == "m" else head_value * 0.3048

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

    st.subheader(get_text("Matching Pumps"))
    st.write(get_text("Found Pumps", count=len(filtered_pumps)))

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
        
        # Display the results
        st.write(get_text("Matching Results"))
        
        # Show all data without pagination
        if len(displayed_results) > 0:
            st.write(get_text("Showing Results", count=len(displayed_results)))
            
        # No pagination - use entire dataset
        start_idx = 0
        end_idx = len(displayed_results)
        
        # Create column configuration for product links and proper formatting
        column_config = {}
        
        # Configure the ID column for default sorting if it exists
        id_column = None
        if "DB ID" in displayed_results.columns:
            id_column = "DB ID"
            column_config["DB ID"] = st.column_config.NumberColumn(
                "DB ID",
                help="Database ID",
                format="%d"
            )
        elif "id" in displayed_results.columns:
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
                display_text=get_text("View Product") if "View Product" in translations[st.session_state.language] else "View Product"
            )
        
        # Better formatting for numeric columns
        if "Max Flow (LPM)" in displayed_results.columns:
            flow_label = get_text("Max Flow (LPM)") if "Max Flow (LPM)" in translations[st.session_state.language] else "Max Flow (LPM)"
            flow_help = get_text("Maximum flow rate in liters per minute") if "Maximum flow rate in liters per minute" in translations[st.session_state.language] else "Maximum flow rate in liters per minute"
            column_config["Max Flow (LPM)"] = st.column_config.NumberColumn(
                flow_label,
                help=flow_help,
                format="%.1f LPM"
            )
        
        if "Max Head (M)" in displayed_results.columns:
            head_label = get_text("Max Head (M)") if "Max Head (M)" in translations[st.session_state.language] else "Max Head (M)"
            head_help = get_text("Maximum head in meters") if "Maximum head in meters" in translations[st.session_state.language] else "Maximum head in meters"
            column_config["Max Head (M)"] = st.column_config.NumberColumn(
                head_label,
                help=head_help,
                format="%.1f m"
            )
        
        # Display the results
        st.data_editor(
            displayed_results.iloc[start_idx:end_idx],
            column_config=column_config,
            hide_index=True,
            disabled=True,
            use_container_width=True
        )
    else:
        st.warning(get_text("No Matches"))
