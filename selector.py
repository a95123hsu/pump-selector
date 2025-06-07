import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client
import os
from dotenv import load_dotenv

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
        "Show Curve": "📈 Show Pump Curve",
        
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
        
        # Pump Curve Section - NEW
        "Pump Curves": "### 📈 Pump Performance Curves",
        "Select Pump": "Select a pump to view its performance curve:",
        "No Curve Data": "No curve data available for this pump model",
        "Curve Data Loaded": "Curve data loaded: {count} pumps with curve data",
        "Performance Curve": "Performance Curve - {model}",
        "Flow Rate": "Flow Rate (LPM)",
        "Head": "Head (M)",
        "Operating Point": "Your Operating Point",
        "Efficiency Curve": "Efficiency Curve - {model}",
        "Efficiency": "Efficiency (%)",
        "Power Curve": "Power Curve - {model}",
        "Power": "Power (kW)",
        "Multiple Curves": "Performance Comparison",
        "Compare Pumps": "Compare Selected Pumps",
        "Select Multiple": "Select multiple pumps to compare:",
        
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
        "No Data": "❌ No pump data available. Please check your Supabase connection or CSV file.",
        "Failed Curve Data": "❌ Failed to load curve data: {error}"
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
        "Show Curve": "📈 顯示泵浦曲線",
        
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
        
        # Pump Curve Section - NEW
        "Pump Curves": "### 📈 幫浦性能曲線",
        "Select Pump": "選擇幫浦以查看其性能曲線:",
        "No Curve Data": "此幫浦型號無曲線資料",
        "Curve Data Loaded": "曲線資料已載入: {count} 個幫浦有曲線資料",
        "Performance Curve": "性能曲線 - {model}",
        "Flow Rate": "流量 (LPM)",
        "Head": "揚程 (M)",
        "Operating Point": "您的操作點",
        "Efficiency Curve": "效率曲線 - {model}",
        "Efficiency": "效率 (%)",
        "Power Curve": "功率曲線 - {model}",
        "Power": "功率 (kW)",
        "Multiple Curves": "性能比較",
        "Compare Pumps": "比較選定的幫浦",
        "Select Multiple": "選擇多個幫浦進行比較:",
        
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
        "No Data": "❌ 無可用幫浦資料。請檢查您的 Supabase 連接或 CSV 檔案。",
        "Failed Curve Data": "❌ 載入曲線資料失敗: {error}"
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
        # Load curve data from Supabase
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
        st.error(get_text("Failed Curve Data", error=str(e)))
        # Fallback to CSV if Supabase fetch fails
        try:
            df = pd.read_csv("pump_curve_data_rows 1.csv")
            return df
        except Exception as csv_error:
            st.error(get_text("Failed CSV", error=str(csv_error)))
            return pd.DataFrame()

# --- Function to create pump curve chart ---
def create_pump_curve_chart(curve_data, model_no, user_flow=None, user_head=None):
    """Create an interactive pump curve chart using Plotly"""
    
    # Extract head columns (columns ending with 'M')
    head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
    
    # Extract pressure columns (columns with 'Kg/cm²')
    pressure_columns = [col for col in curve_data.columns if 'Kg/cm²' in col]
    
    fig = go.Figure()
    
    # Find the pump data
    pump_data = curve_data[curve_data['Model No.'] == model_no]
    
    if pump_data.empty:
        return None
    
    pump_row = pump_data.iloc[0]
    
    # Create head-flow curve
    if head_columns:
        flows = []
        heads = []
        
        for col in head_columns:
            try:
                head_value = float(col.replace('M', ''))
                flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                if not pd.isna(flow_value) and flow_value > 0:
                    flows.append(flow_value)
                    heads.append(head_value)
            except:
                continue
        
        if flows and heads:
            # Sort by flow for proper curve
            sorted_data = sorted(zip(flows, heads))
            flows, heads = zip(*sorted_data)
            
            fig.add_trace(go.Scatter(
                x=flows,
                y=heads,
                mode='lines+markers',
                name=f'{model_no} - Head Curve',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
    
    # Add pressure curves if available
    if pressure_columns:
        for i, col in enumerate(pressure_columns[:3]):  # Limit to 3 pressure curves
            try:
                pressure_value = float(col.split('Kg/cm²')[0])
                flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                if not pd.isna(flow_value) and flow_value > 0:
                    fig.add_trace(go.Scatter(
                        x=[flow_value],
                        y=[pressure_value * 10],  # Convert kg/cm² to approximate meters
                        mode='markers',
                        name=f'{pressure_value} Kg/cm²',
                        marker=dict(size=10, symbol='diamond')
                    ))
            except:
                continue
    
    # Add user operating point if provided
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        fig.add_trace(go.Scatter(
            x=[user_flow],
            y=[user_head],
            mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {user_flow} LPM<br>Head: {user_head} M<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=get_text("Performance Curve", model=model_no),
        xaxis_title=get_text("Flow Rate"),
        yaxis_title=get_text("Head"),
        hovermode='closest',
        showlegend=True,
        height=500,
        template='plotly_white'
    )
    
    return fig

# --- Function to create comparison chart ---
def create_comparison_chart(curve_data, model_nos, user_flow=None, user_head=None):
    """Create a comparison chart for multiple pumps"""
    
    fig = go.Figure()
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    for i, model_no in enumerate(model_nos):
        pump_data = curve_data[curve_data['Model No.'] == model_no]
        
        if pump_data.empty:
            continue
            
        pump_row = pump_data.iloc[0]
        color = colors[i % len(colors)]
        
        # Extract head columns
        head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
        
        flows = []
        heads = []
        
        for col in head_columns:
            try:
                head_value = float(col.replace('M', ''))
                flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                if not pd.isna(flow_value) and flow_value > 0:
                    flows.append(flow_value)
                    heads.append(head_value)
            except:
                continue
        
        if flows and heads:
            # Sort by flow for proper curve
            sorted_data = sorted(zip(flows, heads))
            flows, heads = zip(*sorted_data)
            
            fig.add_trace(go.Scatter(
                x=flows,
                y=heads,
                mode='lines+markers',
                name=model_no,
                line=dict(color=color, width=3),
                marker=dict(size=6)
            ))
    
    # Add user operating point if provided
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        fig.add_trace(go.Scatter(
            x=[user_flow],
            y=[user_head],
            mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {user_flow} LPM<br>Head: {user_head} M<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=get_text("Multiple Curves"),
        xaxis_title=get_text("Flow Rate"),
        yaxis_title=get_text("Head"),
        hovermode='closest',
        showlegend=True,
        height=500,
        template='plotly_white'
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
col_data1, col_data2 = st.columns(2)
with col_data1:
    st.caption(get_text("Data loaded", n_records=len(pumps), timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')))
with col_data2:
    if not curve_data.empty:
        st.caption(get_text("Curve Data Loaded", count=len(curve_data)))

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
    # Continuation from previous code...

    phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase"), 1, 3])

# Get all available columns from the dataset for later use in column selection
if not pumps.empty:
    # Define essential columns that are always shown - REMOVED DB ID
    essential_columns = ["id", "ID", "Model", "Model No."]
    # Include all columns except DB ID - KEEP ORIGINAL CATEGORY
    available_columns = [col for col in pumps.columns if col not in ["DB ID"]]
    
    # Separate essential and optional columns
    optional_columns = [col for col in available_columns if col not in essential_columns]
else:
    essential_columns = []
    optional_columns = []

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
                # Default selection - Model will be first as essential, then these optional columns
                default_selected = [
                    "Category", "Frequency (Hz)", "Phase", "Q Rated/LPM", "Head Rated/M", "Max Flow (LPM)", "Max Head (M)",
                    "Product Link"
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

    # Store filtered pumps in session state for curve visualization
    st.session_state.filtered_pumps = filtered_pumps
    st.session_state.user_flow = flow_lpm
    st.session_state.user_head = head_m

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
        
        # Sort by ID first (excluding DB ID), then apply percentage filter
        if "id" in results.columns:
            results = results.sort_values("id")
        elif "ID" in results.columns:
            results = results.sort_values("ID")
        elif "Model" in results.columns:
            results = results.sort_values("Model")
        elif "Model No." in results.columns:
            results = results.sort_values("Model No.")
        
        # Apply percentage limit after sorting by ID
        max_to_show = max(1, int(len(results) * (result_percent / 100)))
        displayed_results = results.head(max_to_show).copy()
        
        # Apply column selection - build columns in logical order
        columns_to_show = []
        
        # 1. Essential identification columns first
        if "Model" in displayed_results.columns:
            columns_to_show.append("Model")
        elif "Model No." in displayed_results.columns:
            columns_to_show.append("Model No.")
        
        # Add other essential columns (id, ID) - excluding DB ID
        for col in essential_columns:
            if col in displayed_results.columns and col not in columns_to_show and col not in ["DB ID"]:
                columns_to_show.append(col)
        
        # 2. Category (if selected) - ORIGINAL ENGLISH CATEGORY
        if "Category" in selected_optional_columns and "Category" in displayed_results.columns:
            columns_to_show.append("Category")
        
        # 3. Performance specifications (if selected)
        performance_cols = ["Q Rated/LPM", "Head Rated/M", "Max Flow (LPM)", "Max Head (M)"]
        for col in performance_cols:
            if col in selected_optional_columns and col in displayed_results.columns and col not in columns_to_show:
                columns_to_show.append(col)
        
        # 4. Electrical specifications (if selected)
        electrical_cols = ["Frequency (Hz)", "Phase"]
        for col in electrical_cols:
            if col in selected_optional_columns and col in displayed_results.columns and col not in columns_to_show:
                columns_to_show.append(col)
        
        # 5. Physical specifications (if selected)
        physical_cols = ["Pass Solid Dia(mm)", "HP", "Power(KW)", "Outlet (mm)", "Outlet (inch)"]
        for col in physical_cols:
            if col in selected_optional_columns and col in displayed_results.columns and col not in columns_to_show:
                columns_to_show.append(col)
        
        # 6. Other selected columns (excluding Product Link for now)
        for col in selected_optional_columns:
            if col in displayed_results.columns and col not in columns_to_show and col != "Product Link":
                columns_to_show.append(col)
        
        # 7. Product Link always last (if selected)
        if "Product Link" in selected_optional_columns and "Product Link" in displayed_results.columns:
            columns_to_show.append("Product Link")
        
        # If no columns selected, show a message
        if not columns_to_show:
            st.warning("⚠️ No columns selected for display. Please select at least one column from the Column Selection section above.")
        else:
            # Filter the dataframe to only show selected columns (ensuring DB ID is excluded)
            displayed_results = displayed_results[columns_to_show]
            
            # Display the results
            st.write(get_text("Matching Results"))
            
            # Show information about displayed results and columns
            if len(displayed_results) > 0:
                st.write(get_text("Showing Results", count=len(displayed_results)))
                st.caption(f"📋 Displaying {len(displayed_results.columns)} columns: {', '.join(displayed_results.columns[:5])}{'...' if len(displayed_results.columns) > 5 else ''}")
            
            # Create column configuration for product links and proper formatting
            column_config = {}
            
            # Configure the ID column for default sorting if it exists (excluding DB ID)
            if "id" in displayed_results.columns:
                column_config["id"] = st.column_config.NumberColumn(
                    "ID",
                    help="ID",
                    format="%d"
                )
            elif "ID" in displayed_results.columns:
                column_config["ID"] = st.column_config.NumberColumn(
                    "ID",
                    help="ID",
                    format="%d"
                )
            
            # Configure the Product Link column if it exists
            if "Product Link" in displayed_results.columns:
                column_config["Product Link"] = st.column_config.LinkColumn(
                    "Product Link",
                    help="Click to view product details",
                    display_text=get_text("View Product")
                )
            
            # Better formatting for Q Rated/LPM and Head Rated/M columns
            if "Q Rated/LPM" in displayed_results.columns:
                flow_label = get_text("Q Rated/LPM")
                flow_help = get_text("Rated flow rate in liters per minute")
                column_config["Q Rated/LPM"] = st.column_config.NumberColumn(
                    flow_label,
                    help=flow_help,
                    format="%.1f LPM"
                )
            
            if "Head Rated/M" in displayed_results.columns:
                head_label = get_text("Head Rated/M")
                head_help = get_text("Rated head in meters")
                column_config["Head Rated/M"] = st.column_config.NumberColumn(
                    head_label,
                    help=head_help,
                    format="%.1f m"
                )
            
            # Configure other numeric columns with proper formatting
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
            
            # Display the results with error handling
            try:
                st.dataframe(
                    displayed_results,
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True
                )
            except Exception as e:
                # If the dataframe with column_config fails, fall back to simple dataframe
                st.error(f"Error displaying results with column configuration: {e}")
                st.dataframe(
                    displayed_results,
                    hide_index=True,
                    use_container_width=True
                )
                
            # --- NEW: Pump Curve Visualization Section ---
            if not curve_data.empty:
                st.markdown(get_text("Pump Curves"))
                
                # Get available pump models from both selection results and curve data
                available_models = []
                model_column = None
                
                # Find the model column name
                for col in ["Model", "Model No."]:
                    if col in displayed_results.columns:
                        model_column = col
                        break
                
                if model_column:
                    # Get models from search results that also have curve data
                    result_models = displayed_results[model_column].dropna().unique()
                    curve_models = curve_data["Model No."].dropna().unique()
                    available_models = [model for model in result_models if model in curve_models]
                
                if available_models:
                    # Store available models in session state to prevent reloads
                    st.session_state.available_models = available_models
                    
                    # Pump selection for curve visualization with container to prevent reload
                    with st.container():
                        st.subheader("📈 Select Pumps for Curve Visualization")
                        
                        # Initialize selected models in session state if not exists
                        if 'selected_curve_models' not in st.session_state:
                            st.session_state.selected_curve_models = []
                        
                        # Multi-select for pump selection - use session state to maintain selection
                        current_selection = st.multiselect(
                            "Select pumps to display their performance curves:",
                            available_models,
                            default=st.session_state.selected_curve_models,
                            key="curve_pump_select",
                            help="You can select multiple pumps to compare their performance curves"
                        )
                        
                        # Update session state only if selection changed
                        if current_selection != st.session_state.selected_curve_models:
                            st.session_state.selected_curve_models = current_selection
                        
                        # Use session state selection for display to prevent reload issues
                        selected_models = st.session_state.selected_curve_models
                        
                        if selected_models:
                            user_flow = st.session_state.get('user_flow', 0)
                            user_head = st.session_state.get('user_head', 0)
                            
                            # Use container to prevent reloads during chart display
                            with st.container():
                                if len(selected_models) == 1:
                                    # Show single pump curve
                                    st.subheader(f"Performance Curve - {selected_models[0]}")
                                    fig = create_pump_curve_chart(curve_data, selected_models[0], user_flow, user_head)
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True, key=f"single_chart_{selected_models[0]}")
                                    else:
                                        st.warning(get_text("No Curve Data"))
                                        
                                elif len(selected_models) > 1:
                                    # Show comparison chart
                                    st.subheader(f"Performance Comparison - {len(selected_models)} Pumps")
                                    st.caption(f"Comparing: {', '.join(selected_models)}")
                                    fig_comp = create_comparison_chart(curve_data, selected_models, user_flow, user_head)
                                    if fig_comp:
                                        # Use unique key based on selected models to prevent reload issues
                                        chart_key = f"comp_chart_{'_'.join(sorted(selected_models))}"
                                        st.plotly_chart(fig_comp, use_container_width=True, key=chart_key)
                        else:
                            st.info("👆 Please select one or more pumps above to view their performance curves")
                        
                else:
                    st.info("No curve data available for the selected pumps")
            else:
                st.info("Curve data not available")
    else:
        st.warning(get_text("No Matches"))
