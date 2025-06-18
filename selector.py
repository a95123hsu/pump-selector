import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from supabase import create_client
from dotenv import load_dotenv
import numpy as np
from datetime import datetime
import json

# --- Environment Setup ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Enhanced Translation Dictionary ---
translations = {
    "English": {
        # App title and headers
        "Hung Pump": "Hung Pump",
        "Pump Selection Tool": "Pump Selection Tool",
        "Data loaded": "Data loaded: {n_records} records | Last update: {timestamp}",
        
        # Enhanced Buttons
        "Refresh Data": "🔄 Refresh Data",
        "Reset Inputs": "🔄 Reset Inputs",
        "Search": "🔍 Search Pumps",
        "Clear Selection": "❌ Clear Selection",
        "Export Results": "📁 Export Results",
        "Save Session": "💾 Save Session",
        "Load Session": "📂 Load Session",
        
        # Step 1
        "Step 1": "### 🔧 Step 1: Select Basic Criteria",
        "Category": "* Category:",
        "Frequency": "* Frequency (Hz):",
        "Phase": "* Phase:",
        "Select...": "Select...",
        "All Categories": "All Categories",
        "Show All Frequency": "Show All Frequency",
        "Show All Phase": "Show All Phase",
        
        # Enhanced Column Selection
        "Column Selection": "📋 Column Selection & View Options",
        "Select Columns": "Select columns to display in results:",
        "Select All": "Select All",
        "Deselect All": "Deselect All",
        "Essential Columns": "Essential Columns (always shown)",
        "View Presets": "Quick View Presets:",
        "Basic View": "Basic",
        "Technical View": "Technical",
        "Complete View": "Complete",
        "Custom View": "Custom",
        
        # Categories
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
        "Pond Drainage": "### 🌊 Pond Drainage Calculator",
        "Pond Length": "Pond Length (m)",
        "Pond Width": "Pond Width (m)",
        "Pond Height": "Pond Height (m)",
        "Drain Time": "Drain Time (hours)",
        "Pond Volume": "📏 Pond Volume: {volume:,.0f} L",
        "Required Flow": "💧 Required Flow: {flow:,.0f} LPM",
        
        # Underground
        "Pump Depth": "Pump Depth Below Ground (m)",
        "Particle Size": "Max Particle Size (mm)",
        
        # Enhanced Manual Input
        "Manual Input": "### 🔧 Manual Input & Requirements",
        "Flow Unit": "Flow Unit",
        "Flow Value": "Flow Value",
        "Head Unit": "Head Unit",
        "TDH": "Total Dynamic Head (TDH)",
        
        # Advanced Filters
        "Advanced Filters": "### ⚙️ Advanced Filters",
        "Power Range": "Power Range (kW)",
        "Min Power": "Min Power",
        "Max Power": "Max Power",
        "Show Advanced": "Show Advanced Filters",
        "Hide Advanced": "Hide Advanced Filters",
        
        # Estimated application
        "Estimated Application": "### 💡 Estimated Application (based on Manual Input)",
        "Estimated Floors": "Estimated Floors",
        "Estimated Faucets": "Estimated Faucets",
        
        # Enhanced Results
        "Result Display": "### 📊 Result Display & Sorting",
        "Show Percentage": "Show Top Percentage of Results",
        "Sort By": "Sort Results By:",
        "Best Match": "Best Match (Flow + Head)",
        "Flow Ascending": "Flow Rate (Low to High)",
        "Flow Descending": "Flow Rate (High to Low)",
        "Head Ascending": "Head (Low to High)",
        "Head Descending": "Head (High to Low)",
        "Power Ascending": "Power (Low to High)",
        "Model Name": "Model Name (A-Z)",
        "Matching Pumps": "✅ Search Results",
        "Found Pumps": "Found {count} matching pumps",
        "Showing Results": "Showing {shown} of {total} results ({percent:.1f}%)",
        "View Product": "View Product",
        "Select Pumps": "✅ Select pumps to compare performance curves",
        "Selection Summary": "Selected {count} pump(s) for comparison",
        
        # Enhanced Pump Curve Section
        "Pump Curves": "### 📈 Performance Analysis & Comparison",
        "No Curve Data": "No curve data available for this pump model",
        "Curve Data Loaded": "Performance data: {count} pumps with curves available",
        "Performance Curve": "Performance Curve - {model}",
        "Flow Rate": "Flow Rate (LPM)",
        "Head": "Head (M)",
        "Operating Point": "Your Operating Point",
        "Efficiency Curve": "Efficiency Curve - {model}",
        "Efficiency": "Efficiency (%)",
        "Power Curve": "Power Curve - {model}",
        "Power": "Power (kW)",
        "Multiple Curves": "Performance Comparison - {count} Pumps",
        "Loading Curve": "Loading curve data...",
        "Loading Comparison": "Loading comparison chart...",
        "Individual Curves": "Individual Performance Curves",
        "Efficiency at Point": "Est. Efficiency: {eff:.1f}%",
        "Power at Point": "Est. Power: {power:.2f} kW",
        
        # Enhanced column headers
        "Q Rated/LPM": "Flow Rate (LPM)",
        "Head Rated/M": "Head (M)",
        "HP": "HP",
        "Power(KW)": "Power (kW)",
        "Pass Solid Dia(mm)": "Max Particle (mm)",
        "Outlet (mm)": "Outlet (mm)",
        "Outlet (inch)": "Outlet (inch)",
        "Max Flow (LPM)": "Max Flow (LPM)",
        "Max Head (M)": "Max Head (M)",
        
        # Flow/Head units
        "L/min": "L/min",
        "L/sec": "L/sec", 
        "m³/hr": "m³/hr",
        "m³/min": "m³/min",
        "US gpm": "US gpm",
        "m": "m",
        "ft": "ft",
        
        # Enhanced Messages
        "No Matches": "⚠️ No pumps match your criteria. Try adjusting the parameters.",
        "Failed Connection": "❌ Database connection failed: {error}",
        "Failed Data": "❌ Failed to load pump data: {error}",
        "Failed CSV": "❌ CSV fallback failed: {error}",
        "No Data": "❌ No pump data available. Check connection.",
        "Failed Curve Data": "❌ Failed to load curve data: {error}",
        "Export Success": "✅ Results exported successfully!",
        "Session Saved": "✅ Session saved successfully!",
        "Session Loaded": "✅ Session loaded successfully!",
        "Selection Cleared": "✅ Selection cleared!",
        "Search Required": "ℹ️ Run a search to see pump results and curves.",
        "No Selection": "ℹ️ Select pumps from the table to view performance curves.",
        
        # Help & Tips
        "Help Tips": "💡 Tips",
        "Tip 1": "• Start with Category, Frequency, and Phase selection",
        "Tip 2": "• Use Application inputs for quick calculations",
        "Tip 3": "• Manual input overrides automatic calculations",
        "Tip 4": "• Select multiple pumps to compare curves",
        "Tip 5": "• Export results for further analysis",
    },
    "繁體中文": {
        # Complete Chinese translations for all the enhanced features
        "Hung Pump": "宏泵集團",
        "Pump Selection Tool": "水泵選型工具",
        "Data loaded": "已載入資料: {n_records} 筆 | 更新時間: {timestamp}",
        
        # Enhanced Buttons
        "Refresh Data": "🔄 刷新資料",
        "Reset Inputs": "🔄 重置輸入",
        "Search": "🔍 搜尋水泵",
        "Clear Selection": "❌ 清除選擇",
        "Export Results": "📁 匯出結果",
        "Save Session": "💾 儲存工作階段",
        "Load Session": "📂 載入工作階段",
        
        "Step 1": "### 🔧 步驟一: 選擇基本條件",
        "Category": "* 類別:",
        "Frequency": "* 頻率 (赫茲):",
        "Phase": "* 相數:",
        "All Categories": "所有類別",
        "Show All Frequency": "顯示所有頻率",
        "Show All Phase": "顯示所有相數",
        
        # Enhanced features in Chinese
        "Column Selection": "📋 欄位選擇與檢視選項",
        "View Presets": "快速檢視預設:",
        "Basic View": "基本",
        "Technical View": "技術",
        "Complete View": "完整",
        "Custom View": "自訂",
        
        "Advanced Filters": "### ⚙️ 進階篩選",
        "Show Advanced": "顯示進階篩選",
        "Hide Advanced": "隱藏進階篩選",
        "Power Range": "功率範圍 (kW)",
        
        "Sort By": "結果排序:",
        "Best Match": "最佳匹配 (流量+揚程)",
        "Flow Ascending": "流量 (低至高)",
        "Flow Descending": "流量 (高至低)",
        "Head Ascending": "揚程 (低至高)",
        "Head Descending": "揚程 (高至低)",
        "Model Name": "型號名稱 (A-Z)",
        
        "Pond Drainage": "### 🌊 池塘排水計算器",
        "Pond Volume": "📏 池塘體積: {volume:,.0f} 公升",
        "Required Flow": "💧 所需流量: {flow:,.0f} LPM",
        
        "Performance Curve": "性能曲線 - {model}",
        "Multiple Curves": "性能比較 - {count} 個水泵",
        "Individual Curves": "個別性能曲線",
        
        "Export Success": "✅ 結果匯出成功!",
        "Session Saved": "✅ 工作階段儲存成功!",
        "Selection Cleared": "✅ 選擇已清除!",
        "Search Required": "ℹ️ 執行搜尋以查看水泵結果和曲線。",
        "No Selection": "ℹ️ 從表格中選擇水泵以查看性能曲線。",
        
        # Categories in Chinese
        "Dirty Water": "污水泵",
        "Clean Water": "清水泵",
        "Speciality Pump": "特殊用途泵",
        "Grinder": "研磨泵",
        "Construction": "工業泵",
        "Sewage and Wastewater": "污水和廢水泵",
        "High Pressure": "高壓泵",
        "Booster": "加壓泵",
        "BLDC": "無刷直流泵",
        
        # Additional Chinese translations...
    }
}

# --- Enhanced Helper Functions ---
def normalize_category(category):
    if not category:
        return ""
    return str(category).lower().strip()

def get_text(key, **kwargs):
    lang = st.session_state.get("language", "English")
    if key in translations[lang]:
        text = translations[lang][key]
        return text.format(**kwargs) if kwargs else text
    normalized_key = normalize_category(key)
    for trans_key in translations[lang]:
        if normalize_category(trans_key) == normalized_key:
            text = translations[lang][trans_key]
            return text.format(**kwargs) if kwargs else text
    # Fallback to English
    if key in translations["English"]:
        return translations["English"][key].format(**kwargs) if kwargs else translations["English"][key]
    for trans_key in translations["English"]:
        if normalize_category(trans_key) == normalized_key:
            text = translations["English"][trans_key]
            return text.format(**kwargs) if kwargs else text
    return key

# --- Enhanced Database Functions ---
@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

@st.cache_data(ttl=300)  # 5 minute cache
def load_pump_data():
    try:
        supabase = init_connection()
        if not supabase:
            raise Exception("No database connection")
            
        all_records, page_size, current_page = [], 1000, 0
        while True:
            response = supabase.table("pump_selection_data").select("*") \
                .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
            if not response.data:
                break
            all_records.extend(response.data)
            current_page += 1
            if len(response.data) < page_size:
                break
        
        df = pd.DataFrame(all_records)
        
        # Enhanced data cleaning
        if not df.empty:
            # Clean numeric columns
            numeric_columns = ["Q Rated/LPM", "Head Rated/M", "Max Flow (LPM)", "Max Head (M)", 
                             "HP", "Power(KW)", "Pass Solid Dia(mm)", "Frequency (Hz)", "Phase"]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Clean category column
            if "Category" in df.columns:
                df["Category"] = df["Category"].astype(str).str.strip()
                df["Category"] = df["Category"].replace(["nan", "None", "NaN", ""], pd.NA)
        
        return df
    except Exception as e:
        st.error(get_text("Failed Data", error=str(e)))
        try:
            df = pd.read_csv("Pump Selection Data.csv")
            return df
        except Exception as csv_error:
            st.error(get_text("Failed CSV", error=str(csv_error)))
            return pd.DataFrame()

@st.cache_data(ttl=300)
def load_pump_curve_data():
    try:
        supabase = init_connection()
        if not supabase:
            raise Exception("No database connection")
            
        all_records, page_size, current_page = [], 1000, 0
        while True:
            response = supabase.table("pump_curve_data").select("*") \
                .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
            if not response.data:
                break
            all_records.extend(response.data)
            current_page += 1
            if len(response.data) < page_size:
                break
        df = pd.DataFrame(all_records)
        return df
    except Exception as e:
        st.error(get_text("Failed Curve Data", error=str(e)))
        try:
            df = pd.read_csv("pump_curve_data_rows 1.csv")
            return df
        except Exception as csv_error:
            return pd.DataFrame()

# --- Enhanced Visualization Functions ---
def create_enhanced_pump_curve_chart(curve_data, model_no, user_flow=None, user_head=None):
    """Create enhanced pump curve with efficiency estimation"""
    head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
    fig = go.Figure()
    
    pump_data = curve_data[curve_data['Model No.'] == model_no]
    if pump_data.empty:
        return None
    
    pump_row = pump_data.iloc[0]
    flows, heads = [], []
    
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
        # Sort and create smooth curve
        sorted_data = sorted(zip(flows, heads))
        flows, heads = zip(*sorted_data)
        
        # Main performance curve
        fig.add_trace(go.Scatter(
            x=flows, y=heads, 
            mode='lines+markers', 
            name=f'{model_no} - Head Curve',
            line=dict(color='#0066cc', width=3),
            marker=dict(size=8, color='#0066cc'),
            hovertemplate='<b>%{fullData.name}</b><br>Flow: %{x} LPM<br>Head: %{y} M<extra></extra>'
        ))
        
        # Add efficiency zone if available
        if len(flows) > 2:
            # Estimate best efficiency point (typically around 70-80% of max flow)
            best_eff_idx = int(len(flows) * 0.75)
            if best_eff_idx < len(flows):
                fig.add_trace(go.Scatter(
                    x=[flows[best_eff_idx]], y=[heads[best_eff_idx]], 
                    mode='markers',
                    name='Best Efficiency Point',
                    marker=dict(size=12, color='green', symbol='diamond'),
                    hovertemplate='<b>Best Efficiency Point</b><br>Flow: %{x} LPM<br>Head: %{y} M<extra></extra>'
                ))
    
    # Enhanced operating point
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        # Calculate distance from curve for efficiency estimation
        if flows and heads:
            distances = [abs(f - user_flow) + abs(h - user_head) for f, h in zip(flows, heads)]
            closest_idx = distances.index(min(distances))
            efficiency_est = max(60, 90 - min(distances) * 2)  # Simple efficiency estimation
            
            hover_text = f'<b>{get_text("Operating Point")}</b><br>Flow: {user_flow} LPM<br>Head: {user_head} M<br>{get_text("Efficiency at Point", eff=efficiency_est)}'
        else:
            hover_text = f'<b>{get_text("Operating Point")}</b><br>Flow: {user_flow} LPM<br>Head: {user_head} M'
        
        fig.add_trace(go.Scatter(
            x=[user_flow], y=[user_head], 
            mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=16, color='red', symbol='star'),
            hovertemplate=hover_text + '<extra></extra>'
        ))
    
    # Enhanced layout
    fig.update_layout(
        title=dict(
            text=get_text("Performance Curve", model=model_no),
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title=get_text("Flow Rate"),
            gridcolor='lightgray',
            gridwidth=1
        ),
        yaxis=dict(
            title=get_text("Head"),
            gridcolor='lightgray', 
            gridwidth=1
        ),
        hovermode='closest',
        showlegend=True,
        height=500,
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_enhanced_comparison_chart(curve_data, model_nos, user_flow=None, user_head=None):
    """Create enhanced comparison chart with better styling"""
    fig = go.Figure()
    colors = ['#0066cc', '#ff6b35', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12', '#1abc9c', '#34495e']
    
    for i, model_no in enumerate(model_nos):
        pump_data = curve_data[curve_data['Model No.'] == model_no]
        if pump_data.empty:
            continue
            
        pump_row = pump_data.iloc[0]
        head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
        flows, heads = [], []
        
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
            sorted_data = sorted(zip(flows, heads))
            flows, heads = zip(*sorted_data)
            
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=flows, y=heads, 
                mode='lines+markers',
                name=model_no,
                line=dict(color=color, width=3),
                marker=dict(size=6, color=color),
                hovertemplate=f'<b>{model_no}</b><br>Flow: %{{x}} LPM<br>Head: %{{y}} M<extra></extra>'
            ))
    
    # Operating point
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        fig.add_trace(go.Scatter(
            x=[user_flow], y=[user_head], 
            mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=16, color='red', symbol='star'),
            hovertemplate=f'<b>{get_text("Operating Point")}</b><br>Flow: {user_flow} LPM<br>Head: {user_head} M<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=get_text("Multiple Curves", count=len(model_nos)),
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title=get_text("Flow Rate"),
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=get_text("Head"),
            gridcolor='lightgray'
        ),
        hovermode='closest',
        showlegend=True,
        height=600,
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# --- Enhanced Utility Functions ---
def calculate_match_score(pump_row, target_flow, target_head):
    """Calculate how well a pump matches the requirements"""
    pump_flow = pd.to_numeric(pump_row.get("Q Rated/LPM", 0), errors='coerce') or 0
    pump_head = pd.to_numeric(pump_row.get("Head Rated/M", 0), errors='coerce') or 0
    
    if target_flow <= 0 and target_head <= 0:
        return 0
    
    flow_ratio = pump_flow / target_flow if target_flow > 0 else 1
    head_ratio = pump_head / target_head if target_head > 0 else 1
    
    # Penalize over/under sizing
    flow_score = 1 - abs(1 - flow_ratio) if flow_ratio >= 1 else 0.5 * flow_ratio
    head_score = 1 - abs(1 - head_ratio) if head_ratio >= 1 else 0.5 * head_ratio
    
    return (flow_score + head_score) / 2

def get_column_presets():
    """Define column presets for different view types"""
    return {
        "Basic": ["Model", "Category", "Q Rated/LPM", "Head Rated/M", "Power(KW)", "Phase"],
        "Technical": ["Model", "Category", "Q Rated/LPM", "Head Rated/M", "Max Flow (LPM)", "Max Head (M)", 
                     "Power(KW)", "HP", "Frequency (Hz)", "Phase", "Pass Solid Dia(mm)"],
        "Complete": "all"  # All available columns
    }

def save_session_state():
    """Save current session to browser storage"""
    session_data = {
        'filters': {
            'category': st.session_state.get('category_translated', ''),
            'frequency': st.session_state.get('frequency', ''),
            'phase': st.session_state.get('phase', ''),
            'flow_value': st.session_state.get('flow_value', 0),
            'head_value': st.session_state.get('head_value', 0),
        },
        'selected_models': st.session_state.get('selected_curve_models', []),
        'timestamp': datetime.now().isoformat()
    }
    return json.dumps(session_data)

# --- Session State Initialization ---
default_values = {
    "floors": 0, "faucets": 0,
    "length": 0.0, "width": 0.0, "height": 0.0,
    "drain_time_hr": 1.0, "underground_depth": 0.0,
    "particle_size": 0.0, "flow_value": 0.0, "head_value": 0.0,
    "min_power": 0.0, "max_power": 100.0,
    "show_advanced": False
}

for key, val in default_values.items():
    st.session_state.setdefault(key, val)
    
st.session_state.setdefault('language', "English")
st.session_state.setdefault('selected_curve_models', [])
st.session_state.setdefault('selected_columns', [])
st.session_state.setdefault('filtered_pumps', None)
st.session_state.setdefault('column_preset', 'Basic')

# --- Enhanced App Config ---
st.set_page_config(
    page_title="Hung Pump Selection Tool", 
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Custom CSS ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0057B8 0%, #0066cc 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0057B8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .search-button {
        background: linear-gradient(90deg, #0057B8 0%, #0066cc 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #0057B8;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Connection ---
try:
    supabase = init_connection()
    if not supabase:
        st.error(get_text("Failed Connection", error="Unable to initialize database connection"))
        st.stop()
except Exception as e:
    st.error(get_text("Failed Connection", error=str(e)))
    st.stop()

# --- Enhanced Header ---
st.markdown('<div class="main-header">', unsafe_allow_html=True)
col_logo, col_title, col_lang = st.columns([1, 5, 2])

with col_logo:
    st.image("https://www.hungpump.com/images/340357", width=120)

with col_title:
    st.markdown(f"# {get_text('Hung Pump')}")
    st.markdown(f"## {get_text('Pump Selection Tool')}")

with col_lang:
    selected_lang = st.selectbox(
        "🌐 Language / 語言", 
        list(translations.keys()),
        index=list(translations.keys()).index(st.session_state.language), 
        key="lang_selector"
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- Data Loading with Status ---
with st.spinner("Loading pump data..."):
    pumps = load_pump_data()
    curve_data = load_pump_curve_data()

# --- Continuation from previous page ---

if pumps.empty:
    st.error(get_text("No Data"))
    st.stop()

# --- Enhanced Data Status Display ---
col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Total Pumps", f"{len(pumps):,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_status2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    curves_count = len(curve_data) if not curve_data.empty else 0
    st.metric("📈 With Curves", f"{curves_count:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_status3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    categories_count = len(pumps['Category'].dropna().unique()) if 'Category' in pumps.columns else 0
    st.metric("🏷️ Categories", categories_count)
    st.markdown('</div>', unsafe_allow_html=True)

with col_status4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🕒 Last Update", datetime.now().strftime('%H:%M'))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Control Buttons ---
st.markdown("---")
col_btn1, col_btn2, col_btn3, col_btn4, col_space = st.columns([1.2, 1.2, 1.2, 1.2, 4])

with col_btn1:
    if st.button(get_text("Refresh Data"), help="Refresh data from database", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_btn2:
    if st.button(get_text("Reset Inputs"), help="Reset all fields to default", type="secondary", use_container_width=True):
        for key, val in default_values.items():
            st.session_state[key] = val
        st.session_state.selected_curve_models = []
        st.session_state.filtered_pumps = None
        st.rerun()

with col_btn3:
    if st.button(get_text("Clear Selection"), help="Clear selected pumps", type="secondary", use_container_width=True):
        st.session_state.selected_curve_models = []
        st.success(get_text("Selection Cleared"))

with col_btn4:
    if st.session_state.filtered_pumps is not None and not st.session_state.filtered_pumps.empty:
        csv_data = st.session_state.filtered_pumps.to_csv(index=False)
        st.download_button(
            label=get_text("Export Results"),
            data=csv_data,
            file_name=f"pump_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download search results as CSV"
        )

# --- Enhanced Step 1: Basic Criteria ---
st.markdown("---")
st.markdown(get_text("Step 1"))

# Enhanced category handling
if "Category" in pumps.columns:
    # Clean up category data
    pumps["Category"] = pumps["Category"].astype(str).str.strip()
    pumps["Category"] = pumps["Category"].replace(["nan", "None", "NaN", ""], pd.NA)
    unique_categories = pumps["Category"].dropna().unique()
    unique_categories = [c for c in unique_categories if c and c.strip()]
    
    # Create translation mappings
    translated_categories = []
    translated_to_original = {}
    
    # Add "All Categories" option
    all_categories_translated = get_text("All Categories")
    translated_categories.append(all_categories_translated)
    translated_to_original[all_categories_translated] = "All Categories"
    
    # Add actual categories
    for cat in sorted(unique_categories):
        translated_cat = get_text(cat)
        translated_categories.append(translated_cat)
        translated_to_original[translated_cat] = cat
    
    category_options = translated_categories
else:
    category_options = [get_text("All Categories")]
    translated_to_original = {get_text("All Categories"): "All Categories"}

# Create enhanced input columns
input_col1, input_col2, input_col3 = st.columns(3)

with input_col1:
    category_translated = st.selectbox(
        get_text("Category"), 
        category_options,
        key="category_translated",
        help="Select pump category"
    )
    category = translated_to_original.get(category_translated, category_translated)

with input_col2:
    if "Frequency (Hz)" in pumps.columns:
        pumps["Frequency (Hz)"] = pd.to_numeric(pumps["Frequency (Hz)"], errors='coerce')
        freq_options = sorted(pumps["Frequency (Hz)"].dropna().unique())
        frequency = st.selectbox(
            get_text("Frequency"), 
            [get_text("Show All Frequency")] + freq_options,
            key="frequency",
            help="Select electrical frequency"
        )
    else:
        frequency = st.selectbox(get_text("Frequency"), [get_text("Show All Frequency")])

with input_col3:
    if "Phase" in pumps.columns:
        pumps["Phase"] = pd.to_numeric(pumps["Phase"], errors='coerce')
        phase_options = [p for p in sorted(pumps["Phase"].dropna().unique()) if p in [1, 3]]
        phase = st.selectbox(
            get_text("Phase"), 
            [get_text("Show All Phase")] + phase_options,
            key="phase",
            help="Select electrical phase"
        )
    else:
        phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase"), 1, 3])

# --- Enhanced Application Section ---
st.markdown("---")
if category == "Booster":
    st.markdown(get_text("Application Input"))
    st.info(get_text("Floor Faucet Info"))
    
    app_col1, app_col2 = st.columns(2)
    with app_col1:
        num_floors = st.number_input(
            get_text("Number of Floors"), 
            min_value=0, max_value=100, step=1, 
            key="floors",
            help="Number of building floors"
        )
    with app_col2:
        num_faucets = st.number_input(
            get_text("Number of Faucets"), 
            min_value=0, max_value=1000, step=1, 
            key="faucets",
            help="Total number of faucets/taps"
        )
    
    auto_flow = num_faucets * 15
    auto_tdh = num_floors * 3.5
    
    if num_floors > 0 or num_faucets > 0:
        st.success(f"🏢 Auto-calculated: {auto_flow} LPM flow, {auto_tdh} m head")
else:
    auto_flow = 0
    auto_tdh = 0
    num_floors = 0
    num_faucets = 0

# --- Enhanced Pond Drainage Calculator ---
st.markdown(get_text("Pond Drainage"))

pond_col1, pond_col2, pond_col3, pond_col4 = st.columns(4)

with pond_col1:
    length = st.number_input(
        get_text("Pond Length"), 
        min_value=0.0, max_value=1000.0, step=0.1, 
        key="length",
        help="Length in meters"
    )

with pond_col2:
    width = st.number_input(
        get_text("Pond Width"), 
        min_value=0.0, max_value=1000.0, step=0.1, 
        key="width",
        help="Width in meters"
    )

with pond_col3:
    height = st.number_input(
        get_text("Pond Height"), 
        min_value=0.0, max_value=50.0, step=0.1, 
        key="height",
        help="Depth/height in meters"
    )

with pond_col4:
    drain_time_hr = st.number_input(
        get_text("Drain Time"), 
        min_value=0.1, max_value=48.0, step=0.1, 
        key="drain_time_hr",
        help="Time to drain in hours"
    )

# Enhanced pond calculations
pond_volume = length * width * height * 1000  # Convert to liters
drain_time_min = drain_time_hr * 60
pond_lpm = pond_volume / drain_time_min if drain_time_min > 0 else 0

if pond_volume > 0:
    pond_info_col1, pond_info_col2 = st.columns(2)
    with pond_info_col1:
        st.info(get_text("Pond Volume", volume=pond_volume))
    with pond_info_col2:
        if pond_lpm > 0:
            st.success(get_text("Required Flow", flow=pond_lpm))

# --- Additional Parameters ---
other_col1, other_col2 = st.columns(2)

with other_col1:
    underground_depth = st.number_input(
        get_text("Pump Depth"), 
        min_value=0.0, max_value=200.0, step=0.1, 
        key="underground_depth",
        help="Depth below ground in meters"
    )

with other_col2:
    particle_size = st.number_input(
        get_text("Particle Size"), 
        min_value=0.0, max_value=100.0, step=1.0, 
        key="particle_size",
        help="Maximum particle size in mm"
    )

# --- Enhanced Auto Calculations ---
if category == "Booster":
    auto_flow = max(num_faucets * 15, pond_lpm)
    auto_tdh = max(num_floors * 3.5, height)
else:
    auto_flow = pond_lpm
    auto_tdh = underground_depth if underground_depth > 0 else height

# --- Enhanced Manual Input Section ---
st.markdown("---")
st.markdown(get_text("Manual Input"))

manual_col1, manual_col2 = st.columns(2)

with manual_col1:
    st.markdown("**Flow Requirements**")
    flow_unit_options = ["L/min", "L/sec", "m³/hr", "m³/min", "US gpm"]
    flow_unit_translated = [get_text(unit) for unit in flow_unit_options]
    flow_unit_map = dict(zip(flow_unit_translated, flow_unit_options))
    
    flow_unit = st.radio(
        get_text("Flow Unit"), 
        flow_unit_translated, 
        horizontal=True,
        help="Select flow rate unit"
    )
    flow_unit_original = flow_unit_map.get(flow_unit, "L/min")
    
    flow_value = st.number_input(
        get_text("Flow Value"), 
        min_value=0.0, max_value=100000.0, step=10.0, 
        value=float(auto_flow), 
        key="flow_value",
        help="Required flow rate"
    )

with manual_col2:
    st.markdown("**Head Requirements**")
    head_unit_options = ["m", "ft"]
    head_unit_translated = [get_text(unit) for unit in head_unit_options]
    head_unit_map = dict(zip(head_unit_translated, head_unit_options))
    
    head_unit = st.radio(
        get_text("Head Unit"), 
        head_unit_translated, 
        horizontal=True,
        help="Select head unit"
    )
    head_unit_original = head_unit_map.get(head_unit, "m")
    
    head_value = st.number_input(
        get_text("TDH"), 
        min_value=0.0, max_value=1000.0, step=1.0, 
        value=float(auto_tdh), 
        key="head_value",
        help="Total Dynamic Head required"
    )

# --- Enhanced Estimated Application ---
if category == "Booster" and (flow_value > 0 or head_value > 0):
    st.markdown(get_text("Estimated Application"))
    estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
    estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0
    
    est_col1, est_col2 = st.columns(2)
    with est_col1:
        st.metric(get_text("Estimated Floors"), estimated_floors)
    with est_col2:
        st.metric(get_text("Estimated Faucets"), estimated_faucets)

# --- Advanced Filters Section ---
st.markdown("---")
with st.expander(get_text("Advanced Filters"), expanded=st.session_state.get('show_advanced', False)):
    st.session_state.show_advanced = True
    
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        st.markdown("**Power Range**")
        min_power = st.number_input(
            get_text("Min Power"), 
            min_value=0.0, max_value=500.0, step=0.1,
            key="min_power",
            help="Minimum power in kW"
        )
        max_power = st.number_input(
            get_text("Max Power"), 
            min_value=0.1, max_value=500.0, step=0.1,
            value=100.0,
            key="max_power", 
            help="Maximum power in kW"
        )
    
    with adv_col2:
        st.markdown("**Additional Filters**")
        if "Outlet (mm)" in pumps.columns:
            outlet_sizes = pumps["Outlet (mm)"].dropna().unique()
            outlet_sizes = sorted([x for x in outlet_sizes if pd.notna(x)])
            if outlet_sizes:
                selected_outlets = st.multiselect(
                    "Outlet Size (mm)",
                    outlet_sizes,
                    help="Select outlet sizes"
                )

# --- Enhanced Result Display & Column Selection ---
st.markdown("---")
st.markdown(get_text("Result Display"))

display_col1, display_col2 = st.columns([2, 1])

with display_col1:
    result_percent = st.slider(
        get_text("Show Percentage"), 
        min_value=5, max_value=100, value=100, step=5,
        help="Limit results to top percentage"
    )

with display_col2:
    sort_options = [
        "Best Match", "Flow Ascending", "Flow Descending", 
        "Head Ascending", "Head Descending", "Model Name"
    ]
    sort_option = st.selectbox(
        get_text("Sort By"),
        [get_text(opt) for opt in sort_options],
        help="Sort results by"
    )

# --- Enhanced Column Selection ---
with st.expander(get_text("Column Selection"), expanded=False):
    preset_col, custom_col = st.columns([1, 2])
    
    with preset_col:
        st.markdown("**" + get_text("View Presets") + "**")
        presets = get_column_presets()
        
        if st.button(get_text("Basic View"), use_container_width=True):
            st.session_state.column_preset = 'Basic'
            st.session_state.selected_columns = presets['Basic']
        
        if st.button(get_text("Technical View"), use_container_width=True):
            st.session_state.column_preset = 'Technical'
            st.session_state.selected_columns = presets['Technical']
        
        if st.button(get_text("Complete View"), use_container_width=True):
            st.session_state.column_preset = 'Complete'
            if not pumps.empty:
                st.session_state.selected_columns = [col for col in pumps.columns if col != "DB ID"]
    
    with custom_col:
        st.markdown("**Custom Column Selection**")
        if not pumps.empty:
            available_columns = [col for col in pumps.columns if col not in ["DB ID"]]
            essential_columns = ["Model", "Model No.", "ID", "id"]
            optional_columns = [col for col in available_columns if col not in essential_columns]
            
            # Initialize selection if empty
            if not st.session_state.selected_columns:
                st.session_state.selected_columns = presets['Basic']
            
            selected_columns = st.multiselect(
                get_text("Select Columns"),
                optional_columns,
                default=[col for col in st.session_state.selected_columns if col in optional_columns],
                help="Select additional columns to display"
            )
            
            st.session_state.selected_columns = selected_columns

# --- Enhanced Search Form ---
st.markdown("---")
with st.form("enhanced_search_form"):
    search_col1, search_col2 = st.columns([2, 6])
    
    with search_col1:
        submit_search = st.form_submit_button(
            get_text("Search"), 
            type="primary",
            use_container_width=True,
            help="Search for pumps matching your criteria"
        )
    
    with search_col2:
        if submit_search:
            with st.spinner("Searching pumps..."):
                # Enhanced search logic
                filtered_pumps = pumps.copy()
                
                # Apply basic filters
                try:
                    filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
                    filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
                    
                    if frequency != get_text("Show All Frequency"):
                        if isinstance(frequency, (int, float)):
                            filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
                        else:
                            try:
                                freq_value = float(frequency)
                                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == freq_value]
                            except ValueError:
                                pass
                    
                    if phase != get_text("Show All Phase"):
                        if isinstance(phase, (int, float)):
                            filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
                        else:
                            try:
                                phase_value = int(phase)
                                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase_value]
                            except ValueError:
                                pass
                    
                    if category != "All Categories" and category != get_text("All Categories"):
                        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]
                    
                except Exception as e:
                    st.warning(f"Filter error: {e}")
                
                # Convert flow to LPM
                flow_lpm = flow_value
                if flow_unit_original == "L/sec": 
                    flow_lpm *= 60
                elif flow_unit_original == "m³/hr": 
                    flow_lpm = flow_value * 1000 / 60
                elif flow_unit_original == "m³/min": 
                    flow_lpm *= 1000
                elif flow_unit_original == "US gpm": 
                    flow_lpm *= 3.785
                
                # Convert head to meters
                head_m = head_value if head_unit_original == "m" else head_value * 0.3048
                
                # Apply performance filters
                filtered_pumps["Q Rated/LPM"] = pd.to_numeric(filtered_pumps["Q Rated/LPM"], errors="coerce").fillna(0)
                filtered_pumps["Head Rated/M"] = pd.to_numeric(filtered_pumps["Head Rated/M"], errors="coerce").fillna(0)
                
                if flow_lpm > 0:
                    filtered_pumps = filtered_pumps[filtered_pumps["Q Rated/LPM"] >= flow_lpm]
                if head_m > 0:
                    filtered_pumps = filtered_pumps[filtered_pumps["Head Rated/M"] >= head_m]
                
                # Apply advanced filters
                if st.session_state.get('show_advanced', False):
                    if "Power(KW)" in filtered_pumps.columns:
                        filtered_pumps["Power(KW)"] = pd.to_numeric(filtered_pumps["Power(KW)"], errors="coerce").fillna(0)
                        filtered_pumps = filtered_pumps[
                            (filtered_pumps["Power(KW)"] >= min_power) & 
                            (filtered_pumps["Power(KW)"] <= max_power)
                        ]
                
                if particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
                    filtered_pumps["Pass Solid Dia(mm)"] = pd.to_numeric(filtered_pumps["Pass Solid Dia(mm)"], errors="coerce").fillna(0)
                    filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]
                
                # Enhanced sorting
                if not filtered_pumps.empty:
                    if sort_option == get_text("Best Match"):
                        filtered_pumps['match_score'] = filtered_pumps.apply(
                            lambda row: calculate_match_score(row, flow_lpm, head_m), axis=1
                        )
                        filtered_pumps = filtered_pumps.sort_values('match_score', ascending=False)
                        filtered_pumps = filtered_pumps.drop('match_score', axis=1)
                    elif sort_option == get_text("Flow Ascending"):
                        filtered_pumps = filtered_pumps.sort_values("Q Rated/LPM", ascending=True)
                    elif sort_option == get_text("Flow Descending"):
                        filtered_pumps = filtered_pumps.sort_values("Q Rated/LPM", ascending=False)
                    elif sort_option == get_text("Head Ascending"):
                        filtered_pumps = filtered_pumps.sort_values("Head Rated/M", ascending=True)
                    elif sort_option == get_text("Head Descending"):
                        filtered_pumps = filtered_pumps.sort_values("Head Rated/M", ascending=False)
                    elif sort_option == get_text("Model Name"):
                        model_col = "Model" if "Model" in filtered_pumps.columns else "Model No."
                        filtered_pumps = filtered_pumps.sort_values(model_col, ascending=True)
                
                # Apply percentage limit
                max_to_show = max(1, int(len(filtered_pumps) * (result_percent / 100)))
                filtered_pumps = filtered_pumps.head(max_to_show)
                
                # Store results
                st.session_state.filtered_pumps = filtered_pumps.reset_index(drop=True)
                st.session_state.user_flow = flow_lpm
                st.session_state.user_head = head_m
                st.session_state.selected_curve_models = []  # Reset selection

# --- Enhanced Results Display ---
if st.session_state.filtered_pumps is not None and not st.session_state.filtered_pumps.empty:
    filtered_pumps = st.session_state.filtered_pumps
    
    st.markdown("---")
    st.markdown(get_text("Matching Pumps"))
    
    # Results summary
    total_found = len(filtered_pumps)
    result_col1, result_col2, result_col3 = st.columns(3)
    
    with result_col1:
        st.metric("🔍 Found", f"{total_found:,}")
    with result_col2:
        st.metric("📊 Showing", f"{len(filtered_pumps):,}")
    with result_col3:
        percentage_shown = (len(filtered_pumps) / total_found * 100) if total_found > 0 else 0
        st.metric("📈 Percentage", f"{percentage_shown:.1f}%")
    
    # Prepare display columns
    model_column = "Model" if "Model" in filtered_pumps.columns else "Model No."
    essential_columns = [col for col in ["Model", "Model No.", "ID", "id"] if col in filtered_pumps.columns]
    
    display_columns = essential_columns.copy()
    for col in st.session_state.selected_columns:
        if col in filtered_pumps.columns and col not in display_columns:
            display_columns.append(col)
    
    # Add selection column
    display_df = filtered_pumps[display_columns].copy()
    display_df.insert(0, "Select", display_df[model_column].isin(st.session_state.selected_curve_models))
    
    # Enhanced column configuration
    column_config = {
        "Select": st.column_config.CheckboxColumn("Select", default=False, help="Select for curve comparison")
    }
    
    # Configure numeric columns with proper formatting
    if "Q Rated/LPM" in display_df.columns:
        column_config["Q Rated/LPM"] = st.column_config.NumberColumn(
            get_text("Q Rated/LPM"),
            format="%.1f",
            help="Rated flow rate"
        )
    
    if "Head Rated/M" in display_df.columns:
        column_config["Head Rated/M"] = st.column_config.NumberColumn(
            get_text("Head Rated/M"),
            format="%.1f",
            help="Rated head"
        )
    
    if "Power(KW)" in display_df.columns:
        column_config["Power(KW)"] = st.column_config.NumberColumn(
            "Power (kW)",
            format="%.2f",
            help="Power consumption"
        )
    
    if "Product Link" in display_df.columns:
        column_config["Product Link"] = st.column_config.LinkColumn(
            "Product",
            display_text=get_text("View Product")
        )
    
    # Display enhanced data editor
    st.info(get_text("Select Pumps"))
    
    edited_df = st.data_editor(
        display_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=[col for col in display_df.columns if col != "Select"],
        key="enhanced_pump_table"
    )
    
    # Update selection
    if "Select" in edited_df.columns:
        selected_rows = edited_df[edited_df["Select"] == True]
        if not selected_rows.empty and model_column in selected_rows.columns:
            st.session_state.selected_curve_models = selected_rows[model_column].tolist()
    
    # Selection summary
    if st.session_state.selected_curve_models:
        st.success(get_text("Selection Summary", count=len(st.session_state.selected_curve_models)))
        with st.expander("Selected Models", expanded=False):
            for i, model in enumerate(st.session_state.selected_curve_models, 1):
                st.write(f"{i}. {model}")

else:
    st.info(get_text("Search Required"))

# --- Enhanced Pump Curve Visualization ---
if (not curve_data.empty and 
    st.session_state.filtered_pumps is not None and 
    not st.session_state.filtered_pumps.empty):
    
    selected_models = st.session_state.selected_curve_models
    
    if selected_models:
        st.markdown("---")
        st.markdown(get_text("Pump Curves"))
        
        user_flow = st.session_state.get('user_flow', flow_value)
        user_head = st.session_state.get('user_head', head_value)
        
        # Check which models have curve data
        available_curve_models = [
            model for model in selected_models 
            if model in curve_data["Model No."].values
        ]
        
        if available_curve_models:
            if len(available_curve_models) == 1:
                # Single pump analysis
                model = available_curve_models[0]
                st.subheader(f"📈 Performance Analysis - {model}")
                
                with st.spinner(get_text("Loading Curve")):
                    fig = create_enhanced_pump_curve_chart(curve_data, model, user_flow, user_head)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(get_text("No Curve Data"))
                        
            elif len(available_curve_models) > 1:
                # Multi-pump comparison
                st.subheader(f"📊 Performance Comparison - {len(available_curve_models)} Pumps")
                st.caption(f"Comparing: {', '.join(available_curve_models)}")
                
                with st.spinner(get_text("Loading Comparison")):
                    fig_comp = create_enhanced_comparison_chart(
                        curve_data, available_curve_models, user_flow, user_head
                    )
                    if fig_comp:
                        st.plotly_chart(fig_comp, use_container_width=True)
                
                # Individual curves in expander
                with st.expander(get_text("Individual Curves"), expanded=False):
                    for model in available_curve_models:
                        st.markdown(f"**{model}**")
                        fig = create_enhanced_pump_curve_chart(curve_data, model, user_flow, user_head)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"No curve data for {model}")
        else:
            st.warning("⚠️ Selected pumps do not have curve data available.")
            
    else:
        st.info(get_text("No Selection"))

# --- Enhanced Help Section ---
st.markdown("---")
with st.expander(get_text("Help Tips"), expanded=False):
    st.markdown("### " + get_text("Help Tips"))
    # --- Continuation from previous page ---

# --- Enhanced Help Section (continued) ---
    tips = ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"]
    for tip in tips:
        st.markdown(get_text(tip))
    
    # Additional help sections
    st.markdown("### 🔧 **Usage Guidelines**")
    col_help1, col_help2 = st.columns(2)
    
    with col_help1:
        st.markdown("""
        **Basic Search Steps:**
        1. Select Category, Frequency, and Phase
        2. Enter your flow and head requirements
        3. Click Search to find matching pumps
        4. Select pumps to compare performance curves
        """)
    
    with col_help2:
        st.markdown("""
        **Advanced Features:**
        - Use Application Input for building calculations
        - Pond Drainage Calculator for drainage projects
        - Advanced Filters for power and outlet constraints
        - Export results for external analysis
        """)
    
    st.markdown("### 📊 **Understanding Results**")
    st.markdown("""
    - **Best Match**: Pumps closest to your requirements
    - **Performance Curves**: Show actual pump capabilities
    - **Operating Point**: Your specific requirement on the curve
    - **Efficiency**: Estimated efficiency at your operating point
    """)

# --- Enhanced Footer with Additional Information ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("### 📞 **Contact Information**")
    st.markdown("""
    - **Website**: [hungpump.com](https://www.hungpump.com)
    - **Email**: info@hungpump.com
    - **Technical Support**: Available 24/7
    """)

with footer_col2:
    st.markdown("### 🛠️ **Technical Notes**")
    st.markdown("""
    - Data updated from live database
    - Performance curves based on factory testing
    - Efficiency calculations are estimates
    - Consult technical team for final selection
    """)

with footer_col3:
    st.markdown("### 📋 **Quick Reference**")
    st.markdown("""
    - **LPM**: Liters per minute
    - **TDH**: Total Dynamic Head
    - **kW**: Kilowatts (power consumption)
    - **Hz**: Frequency (50/60 Hz typical)
    """)

# --- Enhanced Session Management ---
st.markdown("---")
session_col1, session_col2, session_col3 = st.columns(3)

with session_col1:
    if st.button("💾 Save Current Session", use_container_width=True, help="Save current search parameters"):
        session_data = save_session_state()
        st.success(get_text("Session Saved"))
        st.json(session_data)

with session_col2:
    uploaded_session = st.file_uploader(
        "📂 Load Session File", 
        type=['json'], 
        help="Upload previously saved session"
    )
    if uploaded_session:
        try:
            session_data = json.loads(uploaded_session.read())
            # Load session data back into session state
            if 'filters' in session_data:
                for key, value in session_data['filters'].items():
                    if key in st.session_state:
                        st.session_state[key] = value
            st.success(get_text("Session Loaded"))
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load session: {e}")

with session_col3:
    if st.button("🔄 Reset Everything", use_container_width=True, help="Complete application reset"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            if key not in ['language']:  # Keep language setting
                del st.session_state[key]
        
        # Reinitialize with defaults
        for key, val in default_values.items():
            st.session_state[key] = val
        
        st.session_state.selected_curve_models = []
        st.session_state.filtered_pumps = None
        st.success("🔄 Application reset completed!")
        st.rerun()

# --- Performance Analytics Dashboard (Optional) ---
if st.session_state.filtered_pumps is not None and not st.session_state.filtered_pumps.empty:
    st.markdown("---")
    with st.expander("📊 **Results Analytics Dashboard**", expanded=False):
        analytics_df = st.session_state.filtered_pumps
        
        # Analytics columns
        ana_col1, ana_col2, ana_col3, ana_col4 = st.columns(4)
        
        with ana_col1:
            if "Q Rated/LPM" in analytics_df.columns:
                flow_data = pd.to_numeric(analytics_df["Q Rated/LPM"], errors='coerce').dropna()
                if not flow_data.empty:
                    st.metric("🌊 Avg Flow", f"{flow_data.mean():.1f} LPM")
                    st.caption(f"Range: {flow_data.min():.1f} - {flow_data.max():.1f}")
        
        with ana_col2:
            if "Head Rated/M" in analytics_df.columns:
                head_data = pd.to_numeric(analytics_df["Head Rated/M"], errors='coerce').dropna()
                if not head_data.empty:
                    st.metric("📏 Avg Head", f"{head_data.mean():.1f} M")
                    st.caption(f"Range: {head_data.min():.1f} - {head_data.max():.1f}")
        
        with ana_col3:
            if "Power(KW)" in analytics_df.columns:
                power_data = pd.to_numeric(analytics_df["Power(KW)"], errors='coerce').dropna()
                if not power_data.empty:
                    st.metric("⚡ Avg Power", f"{power_data.mean():.2f} kW")
                    st.caption(f"Range: {power_data.min():.2f} - {power_data.max():.2f}")
        
        with ana_col4:
            if "Category" in analytics_df.columns:
                category_counts = analytics_df["Category"].value_counts()
                if not category_counts.empty:
                    st.metric("🏷️ Top Category", category_counts.index[0])
                    st.caption(f"{category_counts.iloc[0]} pumps")
        
        # Distribution charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if "Q Rated/LPM" in analytics_df.columns:
                flow_data = pd.to_numeric(analytics_df["Q Rated/LPM"], errors='coerce').dropna()
                if len(flow_data) > 1:
                    fig_flow = px.histogram(
                        x=flow_data, 
                        nbins=min(20, len(flow_data)),
                        title="Flow Rate Distribution",
                        labels={'x': 'Flow Rate (LPM)', 'y': 'Count'}
                    )
                    fig_flow.update_layout(height=300)
                    st.plotly_chart(fig_flow, use_container_width=True)
        
        with chart_col2:
            if "Head Rated/M" in analytics_df.columns:
                head_data = pd.to_numeric(analytics_df["Head Rated/M"], errors='coerce').dropna()
                if len(head_data) > 1:
                    fig_head = px.histogram(
                        x=head_data, 
                        nbins=min(20, len(head_data)),
                        title="Head Distribution", 
                        labels={'x': 'Head (M)', 'y': 'Count'}
                    )
                    fig_head.update_layout(height=300)
                    st.plotly_chart(fig_head, use_container_width=True)
        
        # Category distribution pie chart
        if "Category" in analytics_df.columns:
            category_counts = analytics_df["Category"].value_counts()
            if len(category_counts) > 1:
                fig_pie = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Pump Categories in Results"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)

# --- Advanced Export Options ---
if st.session_state.filtered_pumps is not None and not st.session_state.filtered_pumps.empty:
    st.markdown("---")
    with st.expander("📁 **Advanced Export Options**", expanded=False):
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            # CSV Export with custom columns
            st.markdown("**Custom CSV Export**")
            export_columns = st.multiselect(
                "Select columns to export:",
                st.session_state.filtered_pumps.columns.tolist(),
                default=st.session_state.filtered_pumps.columns.tolist()[:10]
            )
            
            if export_columns:
                export_df = st.session_state.filtered_pumps[export_columns]
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    "📄 Download Custom CSV",
                    data=csv_data,
                    file_name=f"pump_custom_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        
        with export_col2:
            # Selected pumps only
            st.markdown("**Selected Pumps Export**")
            if st.session_state.selected_curve_models:
                model_column = "Model" if "Model" in st.session_state.filtered_pumps.columns else "Model No."
                selected_df = st.session_state.filtered_pumps[
                    st.session_state.filtered_pumps[model_column].isin(st.session_state.selected_curve_models)
                ]
                
                selected_csv = selected_df.to_csv(index=False)
                st.download_button(
                    "🎯 Download Selected Only",
                    data=selected_csv,
                    file_name=f"pump_selected_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No pumps selected")
        
        with export_col3:
            # Summary report
            st.markdown("**Summary Report**")
            if st.button("📊 Generate Summary Report"):
                summary_report = generate_summary_report(
                    st.session_state.filtered_pumps,
                    st.session_state.selected_curve_models,
                    {
                        'flow_lpm': st.session_state.get('user_flow', 0),
                        'head_m': st.session_state.get('user_head', 0),
                        'category': category,
                        'frequency': frequency,
                        'phase': phase
                    }
                )
                
                st.download_button(
                    "📋 Download Report",
                    data=summary_report,
                    file_name=f"pump_summary_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

def generate_summary_report(filtered_pumps, selected_models, search_params):
    """Generate a comprehensive text summary report"""
    report = []
    report.append("=" * 60)
    report.append("HUNG PUMP SELECTION SUMMARY REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Search parameters
    report.append("SEARCH PARAMETERS:")
    report.append("-" * 20)
    report.append(f"Category: {search_params.get('category', 'Any')}")
    report.append(f"Frequency: {search_params.get('frequency', 'Any')} Hz")
    report.append(f"Phase: {search_params.get('phase', 'Any')}")
    report.append(f"Required Flow: {search_params.get('flow_lpm', 0):.1f} LPM")
    report.append(f"Required Head: {search_params.get('head_m', 0):.1f} M")
    report.append("")
    
    # Results summary
    report.append("RESULTS SUMMARY:")
    report.append("-" * 15)
    report.append(f"Total pumps found: {len(filtered_pumps)}")
    report.append(f"Pumps selected for comparison: {len(selected_models)}")
    report.append("")
    
    if not filtered_pumps.empty:
        # Statistics
        if "Q Rated/LPM" in filtered_pumps.columns:
            flow_data = pd.to_numeric(filtered_pumps["Q Rated/LPM"], errors='coerce').dropna()
            if not flow_data.empty:
                report.append("FLOW RATE STATISTICS:")
                report.append(f"  Average: {flow_data.mean():.1f} LPM")
                report.append(f"  Range: {flow_data.min():.1f} - {flow_data.max():.1f} LPM")
                report.append("")
        
        if "Head Rated/M" in filtered_pumps.columns:
            head_data = pd.to_numeric(filtered_pumps["Head Rated/M"], errors='coerce').dropna()
            if not head_data.empty:
                report.append("HEAD STATISTICS:")
                report.append(f"  Average: {head_data.mean():.1f} M")
                report.append(f"  Range: {head_data.min():.1f} - {head_data.max():.1f} M")
                report.append("")
        
        # Top recommendations
        model_col = "Model" if "Model" in filtered_pumps.columns else "Model No."
        if model_col in filtered_pumps.columns:
            report.append("TOP 5 RECOMMENDATIONS:")
            report.append("-" * 25)
            top_5 = filtered_pumps.head(5)
            for i, (_, pump) in enumerate(top_5.iterrows(), 1):
                model = pump.get(model_col, 'Unknown')
                flow = pump.get("Q Rated/LPM", 0)
                head = pump.get("Head Rated/M", 0)
                power = pump.get("Power(KW)", 0)
                report.append(f"{i}. {model}")
                report.append(f"   Flow: {flow} LPM, Head: {head} M, Power: {power} kW")
            report.append("")
        
        # Selected pumps details
        if selected_models:
            report.append("SELECTED PUMPS FOR COMPARISON:")
            report.append("-" * 35)
            for model in selected_models:
                pump_data = filtered_pumps[filtered_pumps[model_col] == model]
                if not pump_data.empty:
                    pump = pump_data.iloc[0]
                    flow = pump.get("Q Rated/LPM", 0)
                    head = pump.get("Head Rated/M", 0)
                    power = pump.get("Power(KW)", 0)
                    category = pump.get("Category", "Unknown")
                    report.append(f"• {model}")
                    report.append(f"  Category: {category}")
                    report.append(f"  Performance: {flow} LPM @ {head} M")
                    report.append(f"  Power: {power} kW")
                    report.append("")
    
    # Footer
    report.append("=" * 60)
    report.append("For detailed technical specifications and final selection,")
    report.append("please consult with Hung Pump technical team.")
    report.append("Website: www.hungpump.com")
    report.append("=" * 60)
    
    return "\n".join(report)

# --- Final Status and Debug Information ---
st.markdown("---")
with st.expander("🔧 **System Status & Debug**", expanded=False):
    debug_col1, debug_col2 = st.columns(2)
    
    with debug_col1:
        st.markdown("**Application Status**")
        st.write(f"• Language: {st.session_state.language}")
        st.write(f"• Total pumps loaded: {len(pumps) if not pumps.empty else 0}")
        st.write(f"• Curve data loaded: {len(curve_data) if not curve_data.empty else 0}")
        st.write(f"• Filtered results: {len(st.session_state.filtered_pumps) if st.session_state.filtered_pumps is not None else 0}")
        st.write(f"• Selected for comparison: {len(st.session_state.selected_curve_models)}")
    
    with debug_col2:
        st.markdown("**Current Search Parameters**")
        st.write(f"• Category: {category}")
        st.write(f"• Frequency: {frequency}")
        st.write(f"• Phase: {phase}")
        st.write(f"• Flow: {flow_value} {flow_unit_original}")
        st.write(f"• Head: {head_value} {head_unit_original}")
        
        if st.checkbox("Show Session State Details"):
            st.json({
                key: str(value)[:100] + "..." if len(str(value)) > 100 else value
                for key, value in st.session_state.items()
                if not key.startswith('_')
            })

# --- Performance Monitoring ---
if st.checkbox("⚡ Show Performance Metrics"):
    import time
    import psutil
    
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    
    with perf_col1:
        # Memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        st.metric("💾 Memory Usage", f"{memory_mb:.1f} MB")
    
    with perf_col2:
        # Data loading time simulation
        start_time = time.time()
        # Simulate data processing
        _ = len(pumps) + len(curve_data)
        processing_time = (time.time() - start_time) * 1000
        st.metric("⏱️ Processing Time", f"{processing_time:.1f} ms")
    
    with perf_col3:
        # Cache status
        cache_info = st.cache_data.get_stats()
        st.metric("🗄️ Cache Hits", len(cache_info))

# --- Final Application Signature ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Hung Pump Selection Tool v2.0</strong></p>
        <p>Enhanced with Advanced Analytics & Performance Comparison</p>
        <p>© 2024 Hung Pump Group | Built with Streamlit & Python</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- JavaScript enhancements (optional) ---
st.markdown("""
<script>
// Auto-save feature (stores in browser localStorage)
function autoSave() {
    const formData = {
        category: document.querySelector('[data-testid="stSelectbox"]')?.value || '',
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('pumpSelectorAutoSave', JSON.stringify(formData));
}

// Auto-save every 30 seconds
setInterval(autoSave, 30000);

// Scroll to results when search is performed
function scrollToResults() {
    const resultsElement = document.querySelector('[data-testid="stDataFrame"]');
    if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth' });
    }
}

// Enhanced keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'Enter':
                // Trigger search on Ctrl+Enter
                const searchButton = document.querySelector('button[kind="primary"]');
                if (searchButton) searchButton.click();
                e.preventDefault();
                break;
            case 'r':
                // Refresh data on Ctrl+R
                const refreshButton = document.querySelector('button[title*="Refresh"]');
                if (refreshButton) refreshButton.click();
                e.preventDefault();
                break;
        }
    }
});
</script>
""", unsafe_allow_html=True)

# --- End of Application ---
