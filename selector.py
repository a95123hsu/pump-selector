import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv

# --- Environment Setup ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Translation Dictionary ---
translations = {
    # ... (keep your existing translations here, truncated for brevity)
}

def get_text(key, **kwargs):
    lang = st.session_state.get("language", "English")
    if key in translations[lang]:
        text = translations[lang][key]
        return text.format(**kwargs) if kwargs else text
    # fallback to English
    if key in translations["English"]:
        return translations["English"][key].format(**kwargs) if kwargs else translations["English"][key]
    return key

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=60)
def load_pump_data():
    try:
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
        return df
    except Exception as e:
        st.error(get_text("Failed Data", error=str(e)))
        try:
            return pd.read_csv("Pump Selection Data.csv")
        except Exception as csv_error:
            st.error(get_text("Failed CSV", error=str(csv_error)))
            return pd.DataFrame()

@st.cache_data(ttl=60)
def load_pump_curve_data():
    try:
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
            return pd.read_csv("pump_curve_data_rows 1.csv")
        except Exception as csv_error:
            st.error(get_text("Failed CSV", error=str(csv_error)))
            return pd.DataFrame()

def create_pump_curve_chart(curve_data, model_no, user_flow=None, user_head=None):
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
        sorted_data = sorted(zip(flows, heads))
        flows, heads = zip(*sorted_data)
        fig.add_trace(go.Scatter(
            x=flows, y=heads, mode='lines+markers',
            name=f'{model_no} - Head Curve',
            line=dict(color='blue', width=3), marker=dict(size=8)
        ))
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        fig.add_trace(go.Scatter(
            x=[user_flow], y=[user_head], mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {user_flow} LPM<br>Head: {user_head} M<extra></extra>'
        ))
    fig.update_layout(
        title=get_text("Performance Curve", model=model_no),
        xaxis_title=get_text("Flow Rate"), yaxis_title=get_text("Head"),
        hovermode='closest', showlegend=True, height=500, template='plotly_white'
    )
    return fig

def create_comparison_chart(curve_data, model_nos, user_flow=None, user_head=None):
    fig = go.Figure()
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
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
            fig.add_trace(go.Scatter(
                x=flows, y=heads, mode='lines+markers',
                name=model_no,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=6)
            ))
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        fig.add_trace(go.Scatter(
            x=[user_flow], y=[user_head], mode='markers',
            name=get_text("Operating Point"),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {user_flow} LPM<br>Head: {user_head} M<extra></extra>'
        ))
    fig.update_layout(
        title=get_text("Multiple Curves"),
        xaxis_title=get_text("Flow Rate"),
        yaxis_title=get_text("Head"),
        hovermode='closest', showlegend=True, height=500, template='plotly_white'
    )
    return fig

# --- Default values ---
default_values = {
    "floors": 0, "faucets": 0,
    "length": 0.0, "width": 0.0, "height": 0.0,
    "drain_time_hr": 0.01, "underground_depth": 0.0, "particle_size": 0.0,
    "flow_value": 0.0, "head_value": 0.0
}
for key, val in default_values.items():
    st.session_state.setdefault(key, val)
st.session_state.setdefault('language', "English")
st.session_state.setdefault('selected_curve_models', [])
st.session_state.setdefault('selected_columns', [])
st.session_state.setdefault('filtered_pumps', None)
st.session_state.setdefault('user_flow', 0)
st.session_state.setdefault('user_head', 0)

# --- App Config & Header ---
st.set_page_config(page_title="Pump Selector", layout="wide")
try:
    supabase = init_connection()
except Exception as e:
    st.error(get_text("Failed Connection", error=str(e)))
    st.stop()

col_logo, col_title, col_lang = st.columns([1, 5, 3])
with col_logo:
    st.image("https://www.hungpump.com/images/340357", width=160)
with col_title:
    st.markdown(f"<h1 style='color: #0057B8; margin: 0; padding-left: 15px;'>{get_text('Hung Pump')}</h1>", unsafe_allow_html=True)
with col_lang:
    selected_lang = st.selectbox(
        "Language / 語言", list(translations.keys()),
        index=list(translations.keys()).index(st.session_state.language), key="lang_selector"
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

st.title(get_text("Pump Selection Tool"))

# --- Data Loading ---
pumps, curve_data = load_pump_data(), load_pump_curve_data()
if pumps.empty:
    st.error(get_text("No Data"))
    st.stop()

col_data1, col_data2 = st.columns(2)
with col_data1:
    st.caption(get_text("Data loaded", n_records=len(pumps), timestamp=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')))
with col_data2:
    if not curve_data.empty:
        st.caption(get_text("Curve Data Loaded", count=len(curve_data)))

# --- Refresh & Reset Buttons ---
col1, col2, col_space = st.columns([1, 1.2, 5.8])
with col1:
    if st.button(get_text("Refresh Data"), help="Refresh data from database", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col2:
    if st.button(get_text("Reset Inputs"), key="reset_button", help="Reset all fields to default", type="secondary", use_container_width=True):
        for key, val in default_values.items():
            st.session_state[key] = val
        st.session_state.selected_curve_models = []
        st.session_state.filtered_pumps = None
        st.session_state.selected_columns = []

# --- Step 1: Basic Search Inputs ---
st.markdown(get_text("Step 1"))
if "Category" in pumps.columns:
    pumps["Category"] = pumps["Category"].astype(str).str.strip().replace(["nan", "None", "NaN"], "")
    unique_categories = [c for c in pumps["Category"].unique() if c and c.strip() and c.lower() not in ["nan", "none"]]
    translated_categories, original_to_translated, translated_to_original = [], {}, {}
    all_categories_translated = get_text("All Categories")
    translated_categories.append(all_categories_translated)
    translated_to_original[all_categories_translated] = get_text("All Categories")
    for cat in sorted(unique_categories):
        translated_cat = get_text(cat)
        translated_categories.append(translated_cat)
        original_to_translated[cat] = translated_cat
        translated_to_original[translated_cat] = cat
    category_options = translated_categories
else:
    category_options = [get_text("All Categories")]
    translated_to_original = {get_text("All Categories"): get_text("All Categories")}
category_translated = st.selectbox(get_text("Category"), category_options)
category = translated_to_original.get(category_translated, category_translated)

if "Frequency (Hz)" in pumps.columns:
    pumps["Frequency (Hz)"] = pd.to_numeric(pumps["Frequency (Hz)"], errors='coerce')
    freq_options = sorted(pumps["Frequency (Hz)"].dropna().unique())
    frequency = st.selectbox(get_text("Frequency"), [get_text("Show All Frequency")] + freq_options)
else:
    frequency = st.selectbox(get_text("Frequency"), [get_text("Show All Frequency")])
if "Phase" in pumps.columns:
    pumps["Phase"] = pd.to_numeric(pumps["Phase"], errors='coerce')
    phase_options = [p for p in sorted(pumps["Phase"].dropna().unique()) if p in [1, 3]]
    phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase")] + phase_options)
else:
    phase = st.selectbox(get_text("Phase"), [get_text("Show All Phase"), 1, 3])

# --- Column Selection Section ---
essential_columns = ["Model", "Model No."]
all_columns = [col for col in pumps.columns if col not in ["DB ID"]]
optional_columns = [col for col in all_columns if col not in essential_columns]

with st.expander(get_text("Column Selection"), expanded=False):
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.caption(get_text("Essential Columns"))
        st.write(", ".join([col for col in essential_columns if col in all_columns]))
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(get_text("Select All"), key="select_all_cols", use_container_width=True):
                st.session_state.selected_columns = optional_columns.copy()
        with col_btn2:
            if st.button(get_text("Deselect All"), key="deselect_all_cols", use_container_width=True):
                st.session_state.selected_columns = []
    with col_right:
        st.caption(get_text("Select Columns"))
        for col in optional_columns:
            checked = col in st.session_state.selected_columns
            if st.checkbox(col, value=checked, key=f"col_check_{col}"):
                if col not in st.session_state.selected_columns:
                    st.session_state.selected_columns.append(col)
            else:
                if col in st.session_state.selected_columns:
                    st.session_state.selected_columns.remove(col)

result_percent = st.slider(get_text("Show Percentage"), min_value=5, max_value=100, value=100, step=1)

# --- Application Section ---
if category == "Booster":
    st.markdown(get_text("Application Input"))
    st.caption(get_text("Floor Faucet Info"))
    num_floors = st.number_input(get_text("Number of Floors"), min_value=0, step=1, key="floors")
    num_faucets = st.number_input(get_text("Number of Faucets"), min_value=0, step=1, key="faucets")
    auto_flow = num_faucets * 15
    auto_tdh = num_floors * 3.5
else:
    auto_flow = 0
    auto_tdh = 0
    num_floors = 0
    num_faucets = 0

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

underground_depth = st.number_input(get_text("Pump Depth"), min_value=0.0, step=0.1, key="underground_depth")
particle_size = st.number_input(get_text("Particle Size"), min_value=0.0, step=1.0, key="particle_size")

if category == "Booster":
    auto_flow = max(num_faucets * 15, pond_lpm)
    auto_tdh = max(num_floors * 3.5, height)
else:
    auto_flow = pond_lpm
    auto_tdh = underground_depth if underground_depth > 0 else height

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

if category == "Booster":
    estimated_floors = round(head_value / 3.5) if head_value > 0 else 0
    estimated_faucets = round(flow_value / 15) if flow_value > 0 else 0
    st.markdown(get_text("Estimated Application"))
    col1, col2 = st.columns(2)
    col1.metric(get_text("Estimated Floors"), estimated_floors)
    col2.metric(get_text("Estimated Faucets"), estimated_faucets)

# --- Search FORM ---
with st.form("search_form"):
    submit_search = st.form_submit_button(get_text("Search"))
    if submit_search:
        filtered_pumps = pumps.copy()
        filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
        filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
        if frequency != get_text("Show All Frequency"):
            try:
                freq_value = float(frequency)
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == freq_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
        if phase != get_text("Show All Phase"):
            try:
                phase_value = int(phase)
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase_value]
            except ValueError:
                filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
        if category != get_text("All Categories"):
            filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]
        flow_lpm = flow_value
        if flow_unit_original == "L/sec": flow_lpm *= 60
        elif flow_unit_original == "m³/hr": flow_lpm = flow_value * 1000 / 60
        elif flow_unit_original == "m³/min": flow_lpm *= 1000
        elif flow_unit_original == "US gpm": flow_lpm *= 3.785
        head_m = head_value if head_unit_original == "m" else head_value * 0.3048
        filtered_pumps["Q Rated/LPM"] = pd.to_numeric(filtered_pumps["Q Rated/LPM"], errors="coerce").fillna(0)
        filtered_pumps["Head Rated/M"] = pd.to_numeric(filtered_pumps["Head Rated/M"], errors="coerce").fillna(0)
        if flow_lpm > 0:
            filtered_pumps = filtered_pumps[filtered_pumps["Q Rated/LPM"] >= flow_lpm]
        if head_m > 0:
            filtered_pumps = filtered_pumps[filtered_pumps["Head Rated/M"] >= head_m]
        if particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
            filtered_pumps["Pass Solid Dia(mm)"] = pd.to_numeric(filtered_pumps["Pass Solid Dia(mm)"], errors="coerce").fillna(0)
            filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]
        max_to_show = max(1, int(len(filtered_pumps) * (result_percent / 100)))
        filtered_pumps = filtered_pumps.head(max_to_show).reset_index(drop=True)
        st.session_state.filtered_pumps = filtered_pumps
        st.session_state.user_flow = flow_lpm
        st.session_state.user_head = head_m
        st.session_state.selected_curve_models = []

# --- Results Table ---
if st.session_state.filtered_pumps is not None and not st.session_state.filtered_pumps.empty:
    filtered_pumps = st.session_state.filtered_pumps
    st.subheader(get_text("Matching Pumps"))
    st.write(get_text("Found Pumps", count=len(filtered_pumps)))
    # build columns to show: essential + user-selected
    columns_to_show = []
    for col in essential_columns:
        if col in filtered_pumps.columns:
            columns_to_show.append(col)
    for col in st.session_state.selected_columns:
        if col in filtered_pumps.columns and col not in columns_to_show:
            columns_to_show.append(col)
    # Always show Select column first
    if "Select" in filtered_pumps.columns and "Select" not in columns_to_show:
        columns_to_show.insert(0, "Select")
    # Add Product Link column at the end if present
    if "Product Link" in filtered_pumps.columns and "Product Link" in columns_to_show:
        columns_to_show.remove("Product Link")
        columns_to_show.append("Product Link")
    display_df = filtered_pumps[columns_to_show].copy()
    # selection column
    model_column = "Model" if "Model" in display_df.columns else "Model No."
    display_df.insert(0, "Select", display_df[model_column].isin(st.session_state.selected_curve_models))
    # column_config
    column_config = {}
    if "Product Link" in display_df.columns:
        column_config["Product Link"] = st.column_config.LinkColumn(
            "Product Link",
            help="Click to view product details",
            display_text=get_text("View Product")
        )
    column_config["Select"] = st.column_config.CheckboxColumn(
        "Select", help="Select pumps to view performance curves", default=False
    )
    edited_df = st.data_editor(
        display_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=[col for col in columns_to_show if col != "Select"],
        key="pump_table_editor"
    )
    # update session state selection
    selected_rows = edited_df[edited_df["Select"] == True]
    st.session_state.selected_curve_models = selected_rows[model_column].tolist()
    st.write("You selected:", st.session_state.selected_curve_models)
else:
    st.info("Run a search to see results.")

# --- Pump Curve Visualization Section ---
if (curve_data is not None and
    st.session_state.filtered_pumps is not None and
    not st.session_state.filtered_pumps.empty):
    selected_models = st.session_state.selected_curve_models
    if selected_models:
        st.markdown(get_text("Pump Curves"))
        selected_count = len(selected_models)
        st.success(get_text("Selected Pumps", count=selected_count))
        user_flow = st.session_state.get('user_flow', flow_value)
        user_head = st.session_state.get('user_head', head_value)
        available_curve_models = [model for model in selected_models if model in curve_data["Model No."].values]
        if available_curve_models:
            if len(available_curve_models) == 1:
                st.subheader(f"Performance Curve - {available_curve_models[0]}")
                with st.spinner(get_text("Loading Curve")):
                    fig = create_pump_curve_chart(curve_data, available_curve_models[0], user_flow, user_head)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key=f"curve_{available_curve_models[0]}")
                    else:
                        st.warning(get_text("No Curve Data"))
            elif len(available_curve_models) > 1:
                st.subheader(f"Performance Comparison - {len(available_curve_models)} Pumps")
                st.caption(f"Comparing: {', '.join(available_curve_models)}")
                with st.spinner(get_text("Loading Comparison")):
                    fig_comp = create_comparison_chart(curve_data, available_curve_models, user_flow, user_head)
                    if fig_comp:
                        st.plotly_chart(fig_comp, use_container_width=True, key="multi_curve")
                with st.expander("View Individual Pump Curves", expanded=False):
                    for model in available_curve_models:
                        st.subheader(f"Performance Curve - {model}")
                        fig = create_pump_curve_chart(curve_data, model, user_flow, user_head)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True, key=f"curve_{model}")
                        else:
                            st.warning(f"No curve data available for {model}")
        else:
            st.warning("The selected pumps do not have curve data available.")
    else:
        st.info("Please select pumps from the results table to view performance curves.")
