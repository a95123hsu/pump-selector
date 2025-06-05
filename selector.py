import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load environment variables from .env file
load_dotenv()

# --- Language Support ---
# Translation dictionary with ALL categories from your database
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
        "Update Curves": "📈 Update Curves",
        
        # Step 1
        "Step 1": "### 🔧 Step 1: Select Basic Criteria",
        "Category": "* Category:",
        "Frequency": "* Frequency (Hz):",
        "Phase": "* Phase:",
        "Select...": "Select...",
        "All Categories": "All Categories",
        "Show All Frequency": "Show All Frequency",
        "Show All Phase": "Show All Phase",
        
        # Column Selection - NEW
        "Column Selection": "📋 Column Selection",
        "Select Columns": "Select columns to display in results:",
        "Select All": "Select All",
        "Deselect All": "Deselect All",
        "Essential Columns": "Essential Columns (always shown)",
        
        # Categories from your actual database
        "Dirty Water": "Dirty Water",
        "Clean Water": "Clean Water",
        "Speciality Pump": "Speciality Pump",
        "Grinder": "Grinder",
        "Construction": "Construction",
        "Sewage and Wastewater": "Sewage and Wastewater",
        "High Pressure": "High Pressure",
        "Booster": "Booster",
        "BLDC": "BLDC",
        
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
        "View Product": "View Product",
        "Show Curve": "Show Curve",
        
        # Pump Curves - NEW
        "Pump Curves": "📈 Pump Performance Curves Comparison",
        "Curves Info": "Select pumps above to display their performance curves",
        "Curves Selected": "Comparing {count} selected pumps",
        "Flow LPM": "Flow (LPM)",
        "Head M": "Head (m)",
        "Pump Curve": "Performance Comparison",
        "No Curve Data": "No curve data available for selected pumps",
        "Curve Data Error": "Error loading curve data: {error}",
        "No Selection": "Please select pumps using the checkboxes above to display curves",
        
        # Column headers - UPDATED FOR NEW FIELDS
        "Q Rated/LPM": "Q Rated/LPM",
        "Rated flow rate in liters per minute": "Rated flow rate in liters per minute",
        "Head Rated/M": "Head Rated/M",
        "Rated head in meters": "Rated head in meters",
        
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
        "Hung Pump": "宏泵集團",
        "Pump Selection Tool": "水泵選型工具",
        "Data loaded": "已載入資料: {n_records} 筆記錄 | 最後更新: {timestamp}",
        
        # Buttons
        "Refresh Data": "🔄 刷新資料",
        "Reset Inputs": "🔄 重置輸入",
        "Search": "🔍 搜尋",
        "Update Curves": "📈 更新曲線",
        
        # Step 1
        "Step 1": "### 🔧 步驟一: 選擇基本條件",
        "Category": "* 類別:",
        "Frequency": "* 頻率 (赫茲):",
        "Phase": "* 相數:",
        "Select...": "請選擇...",
        "All Categories": "所有類別",
        "Show All Frequency": "顯示所有頻率",
        "Show All Phase": "顯示所有相數",
        
        # Column Selection - NEW
        "Column Selection": "📋 欄位選擇",
        "Select Columns": "選擇要在結果中顯示的欄位:",
        "Select All": "全選",
        "Deselect All": "全部取消",
        "Essential Columns": "必要欄位 (總是顯示)",
        
        # Categories from your actual database - translated to Traditional Chinese
        "Dirty Water": "污水泵",
        "Clean Water": "清水泵",
        "Speciality Pump": "特殊用途泵",
        "Grinder": "研磨泵",
        "Construction": "工業泵",
        "Sewage and Wastewater": "污水和廢水泵",
        "High Pressure": "高壓泵",
        "Booster": "加壓泵",
        "BLDC": "無刷直流泵",
        
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
        "View Product": "查看產品",
        "Show Curve": "顯示曲線",
        
        # Pump Curves - NEW
        "Pump Curves": "📈 幫浦性能曲線比較",
        "Curves Info": "在上方選擇幫浦以顯示其性能曲線",
        "Curves Selected": "比較 {count} 個選中的幫浦",
        "Flow LPM": "流量 (LPM)",
        "Head M": "揚程 (米)",
        "Pump Curve": "性能比較",
        "No Curve Data": "所選幫浦無可用曲線數據",
        "Curve Data Error": "載入曲線數據錯誤: {error}",
        "No Selection": "請使用上方的復選框選擇幫浦以顯示曲線",
        
        # Column headers - UPDATED FOR NEW FIELDS
        "Q Rated/LPM": "額定流量 (LPM)",
        "Rated flow rate in liters per minute": "每分鐘額定流量（公升）",
        "Head Rated/M": "額定揚程 (M)",
        "Rated head in meters": "額定揚程（米）",
        
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

# Function to normalize category names
def normalize_category(category):
    """Normalize category names for consistent comparison"""
    if not category:
        return ""
    # Convert to string, lowercase, strip whitespace
    return str(category).lower().strip()

# Function to get translated text
def get_text(key, **kwargs):
    # First try exact match
    if key in translations[st.session_state.language]:
        text = translations[st.session_state.language][key]
        return text.format(**kwargs) if kwargs else text
    
    # For categories, try case-insensitive match
    normalized_key = normalize_category(key)
    for trans_key in translations[st.session_state.language]:
        if normalize_category(trans_key) == normalized_key:
            text = translations[st.session_state.language][trans_key]
            return text.format(**kwargs) if kwargs else text
    
    # Fallback to English if translation missing
    if key in translations["English"]:
        return translations["English"][key].format(**kwargs) if kwargs else translations["English"][key]
    
    # For categories in English, try case-insensitive match
    for trans_key in translations["English"]:
        if normalize_category(trans_key) == normalized_key:
            text = translations["English"][trans_key]
            return text.format(**kwargs) if kwargs else text
    
    # If all else fails, return the key itself
    return key

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
@st.cache_data(ttl=60)
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

# --- Load Pump Curve Data ---
@st.cache_data(ttl=60)
def load_pump_curve_data():
    try:
        # Fetch pump curve data from Supabase
        all_records = []
        page_size = 1000
        current_page = 0
        
        while True:
            response = supabase.table("pump_curve_data").select("*") \
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
        st.error(get_text("Curve Data Error", error=str(e)))
        return pd.DataFrame()

# --- Function to create COMBINED pump curves using Plotly ---
def create_combined_pump_curves(curve_data_df, pump_models):
    """Create a SINGLE interactive plotly chart with ALL pump curves overlaid"""
    if curve_data_df.empty or not pump_models:
        return None
    
    # Filter curve data for the selected pump models
    filtered_curves = curve_data_df[curve_data_df['Model No.'].isin(pump_models)].copy()
    
    if filtered_curves.empty:
        return None
    
    # Create a single figure for comparison
    fig = go.Figure()
    
    # Different colors for each pump
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for idx, model in enumerate(pump_models):
        model_data = filtered_curves[filtered_curves['Model No.'] == model]
        
        if not model_data.empty:
            # Get the first row for this model
            row_data = model_data.iloc[0]
            
            # Extract flow and head data from columns
            flows = []
            heads = []
            
            # Define the head columns to check (in meters)
            head_columns = ['1M', '1.5M', '2M', '3M', '4M', '4.5M', '5M', '6M', '7.5M', '8M', 
                           '9M', '10M', '10.5', '12M', '14M', '15M', '16M', '18M', '20M', 
                           '21M', '24M', '25M', '27M', '30M', '36M', '40M', '45M', '50M']
            
            for col in head_columns:
                if col in row_data and pd.notna(row_data[col]) and row_data[col] != '':
                    try:
                        flow_value = float(row_data[col])
                        # Extract head value from column name
                        if col.endswith('M'):
                            head_value = float(col.replace('M', ''))
                        elif col == '10.5':
                            head_value = 10.5
                        else:
                            continue
                        
                        if flow_value > 0:  # Only add positive flow values
                            flows.append(flow_value)
                            heads.append(head_value)
                    except (ValueError, TypeError):
                        continue
            
            # Sort by head for proper curve plotting
            if flows and heads:
                sorted_data = sorted(zip(heads, flows))
                heads, flows = zip(*sorted_data)
                
                # Add trace to the single figure
                fig.add_trace(
                    go.Scatter(
                        x=list(flows),
                        y=list(heads),
                        mode='lines+markers',
                        name=f"{model}",
                        line=dict(
                            color=colors[idx % len(colors)], 
                            width=3
                        ),
                        marker=dict(
                            size=8,
                            color=colors[idx % len(colors)]
                        ),
                        hovertemplate=f"<b>{model}</b><br>" +
                                    f"{get_text('Flow LPM')}: %{{x}}<br>" +
                                    f"{get_text('Head M')}: %{{y}}<br>" +
                                    "<extra></extra>"
                    )
                )
    
    # Update layout for the combined chart
    fig.update_layout(
        title={
            'text': get_text("Pump Curve"),
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title=get_text("Flow LPM"),
        yaxis_title=get_text("Head M"),
        height=600,  # Single chart height
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        font=dict(size=12),
        hovermode='closest',
        # Add grid
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=1,
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='lightgray',
            gridwidth=1,
            showgrid=True
        ),
        # Set background
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

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

# Initialize selected pumps for curve display
if 'selected_pumps_for_curves' not in st.session_state:
    st.session_state.selected_pumps_for_curves = set()

# Initialize table state to prevent reloads
if 'table_state' not in st.session_state:
    st.session_state.table_state = None

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
curve_data = load_pump_curve_data()

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
        st.rerun()
    
with col2:
    # Reset All Inputs Button - with shortened text
    reset_clicked = st.button(get_text("Reset Inputs"), key="reset_button", help="Reset all fields to default", type="secondary", use_container_width=True)
    if reset_clicked:
        for key, val in default_values.items():
            st.session_state[key] = val
        # Also reset selected pumps for curves
        st.session_state.selected_pumps_for_curves = set()
        st.session_state.table_state = None

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
    
    # Create a mapping between translated categories and original categories
    translated_categories = []
    original_to_translated = {}
    translated_to_original = {}
    
    # First, add the "All Categories" option
    all_categories_translated = get_text("All Categories")
    translated_categories.append(all_categories_translated)
    translated_to_original[all_categories_translated] = get_text("All Categories")
    
    # Then process each category from the database
    for cat in sorted(unique_categories):
        # Get translated category if available, otherwise use the original
        translated_cat = get_text(cat)
        translated_categories.append(translated_cat)
        # Store mappings in both directions
        original_to_translated[cat] = translated_cat
        translated_to_original[translated_cat] = cat
    
    # Use translated categories for display
    category_options = translated_categories
else:
    category_options = [get_text("All Categories")]
    translated_to_original = {get_text("All Categories"): get_text("All Categories")}

# Display the translated category dropdown
category_translated = st.selectbox(get_text("Category"), category_options)

# Get the original category name for filtering
if category_translated in translated_to_original:
    category = translated_to_original[category_translated]
else:
    category = category_translated  # Fallback if translation not found

# Use "Show All Frequency" instead of "Select..." for frequency
if "Frequency (Hz)" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Frequency (Hz)"] = pd.to_numeric(pumps["Frequency (Hz)"], errors='coerce')
    freq_options = sorted(pumps["Frequency (Hz)"].dropna().unique())
    frequency = st.selectbox(get_text("Frequency"), [get_text("Show All Frequency")] + freq_options)
else:
    frequency = st.selectbox(get_text("Frequency"), [get_text("Show All Frequency")])

# Use "Show All Phase" instead of "Select..." for phase
if "Phase" in pumps.columns:
    # Convert to numeric first to handle consistency
    pumps["Phase"] = pd.to_numeric(pumps["Phase"], errors='coerce')
    # Filter to only include 1 and 3 phase options that exist in the data
    phase_options = [p for p in sorted(pumps["Phase"].dropna().unique()) if p in [1, 3]]
    phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase")] + phase_options)
else:
    phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase"), 1, 3])

# Get all available columns from the dataset for later use in column selection
if not pumps.empty:
    # Define essential columns that are always shown
    essential_columns = ["DB ID", "id", "ID", "Model", "Product Link"]
    available_columns = [col for col in pumps.columns if col not in ["Category"]]  # Exclude original Category
    
    # Add translated category to available columns
    available_columns.append("Category Display")
    
    # Separate essential and optional columns
    optional_columns = [col for col in available_columns if col not in essential_columns]
else:
    essential_columns = []
    optional_columns = []

# --- Continue with the rest of the form sections ---
# (The application input, pond drainage, manual input sections remain the same)

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

# Continuation of the pump selector with combined curves...

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
if category == "Booster":
    estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
    estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0

    st.markdown(get_text("Estimated Application"))
    col1, col2 = st.columns(2)
    col1.metric(get_text("Estimated Floors"), estimated_floors)
    col2.metric(get_text("Estimated Faucets"), estimated_faucets)

# --- Result Display Limit ---
st.markdown(get_text("Result Display"))

# Column Selection in Result Display Control section
if not pumps.empty and optional_columns:
    with st.expander(get_text("Column Selection"), expanded=False):
        # Create two columns for the selection interface
        col_selection_left, col_selection_right = st.columns([1, 1])
        
        with col_selection_left:
            st.caption(get_text("Essential Columns"))
            st.write(", ".join([col for col in essential_columns if col in available_columns]))
            
            # Select/Deselect All buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                select_all = st.button(get_text("Select All"), key="select_all_cols", use_container_width=True)
            with col_btn2:
                deselect_all = st.button(get_text("Deselect All"), key="deselect_all_cols", use_container_width=True)
        
        with col_selection_right:
            st.caption(get_text("Select Columns"))
            
            # Initialize selected columns in session state if not exists
            if 'selected_columns' not in st.session_state:
                # Default selection - include some commonly used columns
                default_selected = [
                    "Category Display", "Q Rated/LPM", "Head Rated/M", "Max Flow LPM", "Max Head m",
                    "Frequency (Hz)", "Phase", "Pass Solid Dia(mm)", "Product Link"
                ]
                st.session_state.selected_columns = [col for col in default_selected if col in optional_columns]
            
            # Handle Select All / Deselect All button clicks
            if select_all:
                st.session_state.selected_columns = optional_columns.copy()
            if deselect_all:
                st.session_state.selected_columns = []
            
            # Create checkboxes for each optional column - store current state without immediate update
            current_selection = []
            for col in optional_columns:
                is_selected = col in st.session_state.selected_columns
                if st.checkbox(col, value=is_selected, key=f"col_check_{col}"):
                    current_selection.append(col)
            
            # Store the current selection in a temporary state (don't update main state yet)
            st.session_state.temp_selected_columns = current_selection
else:
    # Use the last confirmed selection from search, or default if none
    selected_optional_columns = st.session_state.get('selected_columns', [])

result_percent = st.slider(get_text("Show Percentage"), min_value=5, max_value=100, value=100, step=1)

# --- Search Logic ---
if st.button(get_text("Search")):
    # Update the column selection when search is pressed
    if 'temp_selected_columns' in st.session_state:
        st.session_state.selected_columns = st.session_state.temp_selected_columns
        selected_optional_columns = st.session_state.selected_columns
    else:
        selected_optional_columns = st.session_state.get('selected_columns', [])
    
    # Reset selected pumps for curves when new search is performed
    st.session_state.selected_pumps_for_curves = set()
    st.session_state.table_state = None
    
    filtered_pumps = pumps.copy()
    
    # Handle frequency and phase filtering with "Show All" options
    try:
        # Convert types appropriately with error handling before filtering
        filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
        filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
        
        # Apply frequency filter - skip filtering if "Show All Frequency" is selected
        if frequency != get_text("Show All Frequency"):
            if isinstance(frequency, str):
                try:
                    freq_value = float(frequency)
                    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == freq_value]
                except ValueError:
                    filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
            else:
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
        # Apply phase filter - skip filtering if "Show All Phase" is selected
        if phase != get_text("Show All Phase"):
            if isinstance(phase, str):
                try:
                    phase_value = int(phase)
                    filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase_value]
                except ValueError:
                    filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
            else:
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == int(phase)]
    except Exception as e:
        st.error(f"Error filtering by frequency/phase: {e}")
        # If filtering fails, show a message but continue with other filters

    # Apply category filter - use the original English category name for filtering
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

    # Use Q Rated/LPM and Head Rated/M instead of Max Flow and Max Head
    # Ensure numeric conversion for flow and head with improved handling
    # Replace NaN with 0 to avoid comparison issues
    filtered_pumps["Q Rated/LPM"] = pd.to_numeric(filtered_pumps["Q Rated/LPM"], errors="coerce").fillna(0)
    filtered_pumps["Head Rated/M"] = pd.to_numeric(filtered_pumps["Head Rated/M"], errors="coerce").fillna(0)

    # Apply filters with safe handling of missing values
    if flow_lpm > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Q Rated/LPM"] >= flow_lpm]
    if head_m > 0:
        filtered_pumps = filtered_pumps[filtered_pumps["Head Rated/M"] >= head_m]
    if particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
        # Convert to numeric first to handle potential string values
        filtered_pumps["Pass Solid Dia(mm)"] = pd.to_numeric(filtered_pumps["Pass Solid Dia(mm)"], errors="coerce").fillna(0)
        filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]

    st.subheader(get_text("Matching Pumps"))
    st.write(get_text("Found Pumps", count=len(filtered_pumps)))

    if not filtered_pumps.empty:
        results = filtered_pumps.copy()
        
        # Sort by Q Rated/LPM and Head Rated/M for better user experience
        if "Q Rated/LPM" in results.columns and "Head Rated/M" in results.columns:
            # Properly handle data types before calculations
            results["Q Rated/LPM"] = pd.to_numeric(results["Q Rated/LPM"], errors="coerce").fillna(0)
            results["Head Rated/M"] = pd.to_numeric(results["Head Rated/M"], errors="coerce").fillna(0)
            
            # Sort by closest match to requested flow and head
            results["Flow Difference"] = abs(results["Q Rated/LPM"] - flow_lpm)
            results["Head Difference"] = abs(results["Head Rated/M"] - head_m)
            
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
        
        # Create the translated category column and remove English category
        if "Category" in displayed_results.columns:
            displayed_results["Category Display"] = displayed_results["Category"].apply(
                lambda x: get_text(x) if x and isinstance(x, str) else x
            )
            # Remove the original English Category column
            displayed_results = displayed_results.drop(columns=["Category"])
        
        # Store the table data in session state to prevent reloads
        st.session_state.table_state = {
            'data': displayed_results,
            'selected_optional_columns': selected_optional_columns,
            'essential_columns': essential_columns
        }

# --- Display results table if we have data ---
if st.session_state.table_state:
    displayed_results = st.session_state.table_state['data']
    selected_optional_columns = st.session_state.table_state['selected_optional_columns']
    essential_columns = st.session_state.table_state['essential_columns']
    
    # --- NEW: Add checkbox column for curve selection ---
    # Find the model column
    model_column = None
    for col in ["Model", "Model No.", "Model No", "model", "model_no"]:
        if col in displayed_results.columns:
            model_column = col
            break
    
    if model_column:
        # Get unique models and their indices for checkbox management
        unique_models = displayed_results[model_column].dropna().unique()
        
        # Auto-select first 5 pumps for curves if this is a new search (no selections yet)
        if len(st.session_state.selected_pumps_for_curves) == 0:
            st.session_state.selected_pumps_for_curves = set(unique_models[:5])
        
        # Add checkbox column to the dataframe
        checkbox_data = []
        for idx, row in displayed_results.iterrows():
            model_name = str(row[model_column]) if pd.notna(row[model_column]) else ""
            is_selected = model_name in st.session_state.selected_pumps_for_curves
            checkbox_data.append(is_selected)
        
        # Add checkbox column to the beginning of the dataframe
        displayed_results_with_checkbox = displayed_results.copy()
        displayed_results_with_checkbox.insert(0, get_text("Show Curve"), checkbox_data)
        
        # Apply column selection - only show selected columns (but always include checkbox column)
        # Determine which columns to show based on user selection
        columns_to_show = [get_text("Show Curve")]  # Always include checkbox column first
        
        # Always include essential columns that exist in the data
        for col in essential_columns:
            if col in displayed_results_with_checkbox.columns:
                columns_to_show.append(col)
        
        # Add user-selected optional columns that exist in the data
        for col in selected_optional_columns:
            if col in displayed_results_with_checkbox.columns and col not in columns_to_show:
                columns_to_show.append(col)
        
        # If no columns selected (except checkbox), show a message
        if len(columns_to_show) <= 1:
            st.warning("⚠️ No columns selected for display. Please select at least one column from the Column Selection section above.")
        else:
            # Filter the dataframe to only show selected columns
            displayed_results_filtered = displayed_results_with_checkbox[columns_to_show]
            
            # Reorder columns - move Head Rated/M and Q Rated/LPM after Pass Solid Dia(mm) if they're selected
            def reorder_columns(df):
                """Reorder dataframe columns to put Q Rated/LPM and Head Rated/M after Pass Solid Dia(mm)"""
                cols = list(df.columns)
                
                # Always keep checkbox column first
                checkbox_col = get_text("Show Curve")
                if checkbox_col in cols:
                    cols.remove(checkbox_col)
                    new_cols = [checkbox_col]
                else:
                    new_cols = []
                
                # Find the positions of key columns
                pass_solid_idx = None
                q_rated_idx = None
                head_rated_idx = None
                
                for i, col in enumerate(cols):
                    if "Pass Solid Dia" in str(col):
                        pass_solid_idx = i
                    elif col == "Q Rated/LPM":
                        q_rated_idx = i
                    elif col == "Head Rated/M":
                        head_rated_idx = i
                
                # If we have the required columns, reorder them
                if pass_solid_idx is not None and (q_rated_idx is not None or head_rated_idx is not None):
                    # Remove Q Rated/LPM and Head Rated/M from their current positions
                    reorder_cols = ["Q Rated/LPM", "Head Rated/M"]
                    new_cols_remaining = [col for col in cols if col not in reorder_cols]
                    
                    # Insert them after Pass Solid Dia(mm)
                    insert_position = pass_solid_idx + 1
                    if "Q Rated/LPM" in cols:
                        new_cols_remaining.insert(insert_position, "Q Rated/LPM")
                        insert_position += 1
                    if "Head Rated/M" in cols:
                        new_cols_remaining.insert(insert_position, "Head Rated/M")
                    
                    new_cols.extend(new_cols_remaining)
                else:
                    # If we can't find the reference columns, return as is
                    new_cols.extend(cols)
                
                return df[new_cols]
            
            # Apply column reordering
            displayed_results_filtered = reorder_columns(displayed_results_filtered)
            
            # Display the results
            st.write(get_text("Matching Results"))
            
            # Show information about displayed results and columns
            if len(displayed_results_filtered) > 0:
                st.write(get_text("Showing Results", count=len(displayed_results_filtered)))
                st.caption(f"📋 Displaying {len(displayed_results_filtered.columns)} columns: {', '.join(displayed_results_filtered.columns[:5])}{'...' if len(displayed_results_filtered.columns) > 5 else ''}")
            
            # Create column configuration for product links and proper formatting
            column_config = {}
            
            # Configure the checkbox column
            column_config[get_text("Show Curve")] = st.column_config.CheckboxColumn(
                get_text("Show Curve"),
                help="Select pumps to display in performance curves",
                default=False
            )
            
            # Configure the ID column for default sorting if it exists
            if "DB ID" in displayed_results_filtered.columns:
                column_config["DB ID"] = st.column_config.NumberColumn(
                    "DB ID",
                    help="Database ID",
                    format="%d"
                )
            elif "id" in displayed_results_filtered.columns:
                column_config["id"] = st.column_config.NumberColumn(
                    "ID",
                    help="Database ID",
                    format="%d"
                )
            elif "ID" in displayed_results_filtered.columns:
                column_config["ID"] = st.column_config.NumberColumn(
                    "ID",
                    help="Database ID",
                    format="%d"
                )
            
            # Configure the Product Link column if it exists
            if "Product Link" in displayed_results_filtered.columns:
                column_config["Product Link"] = st.column_config.LinkColumn(
                    "Product Link",
                    help="Click to view product details",
                    display_text=get_text("View Product")
                )
            
            # Better formatting for Q Rated/LPM and Head Rated/M columns
            if "Q Rated/LPM" in displayed_results_filtered.columns:
                flow_label = get_text("Q Rated/LPM")
                flow_help = get_text("Rated flow rate in liters per minute")
                column_config["Q Rated/LPM"] = st.column_config.NumberColumn(
                    flow_label,
                    help=flow_help,
                    format="%.1f LPM"
                )
            
            if "Head Rated/M" in displayed_results_filtered.columns:
                head_label = get_text("Head Rated/M")
                head_help = get_text("Rated head in meters")
                column_config["Head Rated/M"] = st.column_config.NumberColumn(
                    head_label,
                    help=head_help,
                    format="%.1f m"
                )
            
            # Configure the translated category column
            if "Category Display" in displayed_results_filtered.columns:
                column_config["Category Display"] = st.column_config.TextColumn(
                    get_text("Category"),
                    help="Translated pump category"
                )
            
            # Display the results with error handling - use data_editor for interactive checkboxes
            try:
                # Use data_editor to allow checkbox interaction
                edited_data = st.data_editor(
                    displayed_results_filtered,
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True,
                    key="pump_results_table_with_checkbox"
                )
                
                # Update selected pumps based on checkbox changes
                if get_text("Show Curve") in edited_data.columns and model_column:
                    # Find which pumps are now selected
                    new_selected_pumps = set()
                    
                    # Iterate through the edited data to find selected pumps
                    for idx, row in edited_data.iterrows():
                        if row[get_text("Show Curve")]:
                            # Get the corresponding model from the original data
                            original_row = displayed_results_with_checkbox.iloc[idx]
                            if model_column in original_row:
                                model_name = str(original_row[model_column]) if pd.notna(original_row[model_column]) else ""
                                if model_name:
                                    new_selected_pumps.add(model_name)
                    
                    # Update session state
                    st.session_state.selected_pumps_for_curves = new_selected_pumps
                
            except Exception as e:
                # If the data_editor with column_config fails, fall back to simple dataframe
                st.error(f"Error displaying interactive table: {e}")
                st.dataframe(
                    displayed_results_filtered,
                    hide_index=True,
                    use_container_width=True
                )
            
            # Show selection status
            if st.session_state.selected_pumps_for_curves:
                st.info(f"🎯 {len(st.session_state.selected_pumps_for_curves)} pumps selected for curves: {', '.join(list(st.session_state.selected_pumps_for_curves)[:3])}{'...' if len(st.session_state.selected_pumps_for_curves) > 3 else ''}")
            
            # --- Display COMBINED Pump Curves for Selected Results ---
            st.markdown("---")  # Add separator
            st.markdown(get_text("Pump Curves"))
            
            if st.session_state.selected_pumps_for_curves:
                st.caption(get_text("Curves Selected", count=len(st.session_state.selected_pumps_for_curves)))
                
                # Get the selected pump models
                selected_models = list(st.session_state.selected_pumps_for_curves)
                
                if selected_models and not curve_data.empty:
                    try:
                        # Create and display the COMBINED pump curves using Plotly
                        curve_fig = create_combined_pump_curves(curve_data, selected_models)
                        
                        if curve_fig:
                            st.plotly_chart(curve_fig, use_container_width=True)
                        else:
                            st.info(get_text("No Curve Data"))
                            
                    except Exception as e:
                        st.error(get_text("Curve Data Error", error=str(e)))
                else:
                    st.info(get_text("No Curve Data"))
            else:
                st.info(get_text("No Selection"))
                st.caption(get_text("Curves Info"))
else:
    # No search performed yet
    if pumps.empty:
        st.warning(get_text("No Matches"))
    else:
        st.info("👆 Please perform a search to see pump results and curves.")
