import streamlit as st
import pandas as pd
import os

# Load the CSV file
results_dir = 'results'
benchmark_file = 'CU_benchmark_results_Nosana.csv'
benchmark_data = pd.read_csv(os.path.join(results_dir, benchmark_file), dtype={'Market': str})

def get_cu_columns():
    cu_columns = [col for col in benchmark_data.columns if 'MeanTokensPerSecond' in col]
    cu_configs = sorted(set([int(col.split('_')[0][2:]) for col in cu_columns if col.startswith('CU')]))
    cu_configs = [f"Concurrent User {cu}" for cu in cu_configs]
    return cu_configs

def get_models():
    return sorted(benchmark_data['ModelName'].unique())

def get_markets():
    return sorted(benchmark_data['Market'].unique())

def load_cu_data(cu, model, market):
    cu_number = cu.split()[-1]  # Extract the CU number (e.g., '1', '5', '100')
    cu_columns = [col for col in benchmark_data.columns if col.startswith(f'CU{cu_number}_')]
    common_columns = ['Node', 'Market', 'StartupTime', 'ModelName', 'NosanaPrice', 'GPU-Price-Per-Hour']
    columns_to_select = common_columns + cu_columns
    cu_data = benchmark_data[columns_to_select].copy()

    # Filter by model and market
    if model:
        cu_data = cu_data[cu_data['ModelName'] == model]
    if market:
        cu_data = cu_data[cu_data['Market'] == market]

    # Rename CU-specific columns with spaces and full words
    column_mapping = {
        'MeanTokensPerSecond': 'Output Speed (Output Tokens/s)',
        'NettoTokensPerSecond': 'Total Speed (Output+Input Tokens/s)',
        'AverageLatency': 'Latency (s)',
        'PricePerMillionTokens': 'Price ($ per 1M Tokens)',
        'AvgClockSpeed': 'Clock Speed (GHz)',  # Assuming the unit is GHz, adjust if needed
        'AvgPowerUsage': 'Power Usage (W)',  # Assuming the unit is watts, adjust if needed
        'GPU-Price-Per-Hour': 'GPU Price ($/h)',
        'ModelName': 'Model Name',
        'StartupTime': 'Startup Time (s)',
        'NosanaPrice': 'NOS ($)'
    }

    cu_data.columns = [col.replace(f'CU{cu_number}_', '').replace('_', ' ') for col in cu_data.columns]
    cu_data.rename(columns=column_mapping, inplace=True)

    formatter = {}
    for col in cu_data.columns:
        if col == 'Market':  # Skip formatting for the 'Market' column
            continue
        elif cu_data[col].dtype == 'float64':
            formatter[col] = lambda x: f"{x:.2f}" if pd.notna(x) else ""
        elif cu_data[col].dtype == 'int64':
            formatter[col] = lambda x: f"{x:.0f}" if pd.notna(x) else ""

    if 'Output Speed (Output Tokens/s)' in cu_data.columns:
        cu_data = cu_data.sort_values(by='Output Speed (Output Tokens/s)', ascending=False)

    column_order = [
        'Node', 'Market', 'Model Name', 'GPU Price ($/h)', 'NOS ($)',
        'Output Speed (Output Tokens/s)', 'Total Speed (Output+Input Tokens/s)', 'Latency (s)',
        'Price ($ per 1M Tokens)', 'Clock Speed (GHz)', 'Power Usage (W)'
    ]

    return cu_data[[col for col in column_order if col in cu_data.columns]]


st.set_page_config(page_title="Concurrent User Leaderboard", page_icon=":trophy:", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="View"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #010c04; /* Nosana background color */
        color: #FFFFFF;
    }
    .stButton>button {
        font-family: 'Space Grotesk', sans-serif;
        color: #5FFF00;
        background-color: #010c04;
    }
    .stDataFrame, .stDataFrame th, .stDataFrame td {
        font-family: 'Space Mono', monospace; /* Ensuring consistent font for all text */
        color: #FFFFFF;
        font-size: 16px; /* Ensuring readable font size */
        table-layout: fixed; /* Ensuring the table layout respects column width */
        word-wrap: break-word; /* Ensuring text in headers doesn't overflow */
        min-width: 120px; /* Minimum width for each column */
    }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .reportview-container .main .block-container { padding-top: 0; }
    </style>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_path = 'leaderboard/Nosana_Logo_horizontal_color_white.png'
    st.image(logo_path, width=800)

st.markdown("<h1 style='text-align: center;'>Concurrent User Leaderboard</h1>", unsafe_allow_html=True)

cu_configs = get_cu_columns()
models = get_models()
markets = get_markets()

# Select Concurrent User Configuration, Model, and Market
selected_cu = st.selectbox('Select Concurrent User Configuration', cu_configs, index=cu_configs.index('Concurrent User 100'))
selected_model = st.selectbox('Select Model', models, index=models.index('llama3.1_8B_4x'))
selected_market = st.selectbox('Select Market', markets, index=markets.index('4090'))


cu_data = load_cu_data(selected_cu, selected_model, selected_market)


formatter = {}
for col in cu_data.columns:
    if cu_data[col].dtype == 'float64':  # Assuming your decimal columns are float type
        formatter[col] = lambda x: f"{x:.2f}" if pd.notna(x) else ""  # Retain two decimal places
    elif cu_data[col].dtype == 'int64':
        formatter[col] = lambda x: f"{x:.0f}" if pd.notna(x) else ""  # No commas for integers

st.dataframe(cu_data.style.format(formatter), width=1800)

total_jobs = cu_data.shape[0]
total_nodes = cu_data['Node'].nunique()

col1, col2, col3, col4 = st.columns([10, 3, 3, 10])
col2.metric(label="Total Jobs", value=total_jobs)
col3.metric(label="Total Nodes", value=total_nodes)

st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <p>
            This leaderboard showcases the performance of nodes based on their Concurrent User-specific Large Language Model benchmarking results.
            Each node is evaluated based on the selected concurrent user configuration's tokens per second, total tokens, and other metrics.
        </p>
        <p>
            Use the dropdown menus above to view results for different concurrent user configurations, models, and markets.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <footer style='text-align: center; color: #FFFFFF; font-family: "Space Mono", monospace;'>
        © NOSANA 2024. All rights reserved.
    </footer>
    """, unsafe_allow_html=True)
