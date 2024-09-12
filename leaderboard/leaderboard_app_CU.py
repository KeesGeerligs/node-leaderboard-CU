import streamlit as st
import pandas as pd
import os

# Load the CSV file
results_dir = 'results'
benchmark_file = 'CU_benchmark_results_Nosana.csv'
benchmark_data = pd.read_csv(os.path.join(results_dir, benchmark_file))

def get_cu_columns():
    cu_columns = [col for col in benchmark_data.columns if 'MeanTokensPerSecond' in col]
    cu_configs = sorted(set([int(col.split('_')[0][2:]) for col in cu_columns if col.startswith('CU')]))
    cu_configs = [f"Concurrent User {cu}" for cu in cu_configs]
    return cu_configs

def load_cu_data(cu):
    cu_number = cu.split()[-1]  # Extract the CU number (e.g., '1', '5', '100')
    cu_columns = [col for col in benchmark_data.columns if col.startswith(f'CU{cu_number}_')]
    common_columns = ['Node', 'Market', 'StartupTime', 'ModelName', 'NosanaPrice', 'GPU_Price_Per_Hour']
    columns_to_select = common_columns + cu_columns
    cu_data = benchmark_data[columns_to_select].copy()

    # Rename CU-specific columns with spaces and full words
    column_mapping = {
        'MeanTokensPerSecond': 'Tokens Per Second',
        'NettoTokensPerSecond': 'Total Tokens Per Second',
        'AverageLatency': 'Latency',
        'PricePerMillionTokens': 'Price Per Million Tokens',
        'AvgClockSpeed': 'Clock Speed',
        'AvgPowerUsage': 'Power Usage',
        'GPU_Price_Per_Hour': 'GPU Price Per Hour',
        'ModelName': 'Model Name',  # Renaming ModelName to Model Name
        'StartupTime': 'Startup Time Seconds',  # Renaming StartupTime to Startup Time Seconds
        'NosanaPrice': 'Nosana Price'  # Renaming NosanaPrice to Nosana Price
    }
    
    cu_data.columns = [col.replace(f'CU{cu_number}_', '').replace('_', ' ') for col in cu_data.columns]
    cu_data.rename(columns=column_mapping, inplace=True)

    # Round all numeric values except for 'GPU Price Per Hour', 'Nosana Price', 'Latency', and 'Price Per Million Tokens'
    for column in cu_data.columns:
        if column not in ['GPU Price Per Hour', 'Nosana Price', 'Latency', 'Price Per Million Tokens']:
            cu_data[column] = pd.to_numeric(cu_data[column], errors='coerce').round(0).fillna(cu_data[column]).astype('Int64', errors='ignore')

    # Reorder the columns and exclude 'Utilization'
    column_order = [
        'Node', 'Market', 'Model Name', 'Startup Time Seconds', 'GPU Price Per Hour', 'Nosana Price', 'Tokens Per Second',
        'Total Tokens Per Second', 'Latency', 'Price Per Million Tokens', 
        'Clock Speed', 'Power Usage'
    ]
    
    return cu_data[[col for col in column_order if col in cu_data.columns]]

st.set_page_config(page_title="Concurrent User Leaderboard", page_icon=":trophy:", layout="wide")

# Nosana CSS Styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #010c04;  /* Nosana background color */
        color: #FFFFFF;
    }
    h1 {
        font-family: 'Space Mono', monospace;
        color: #FFFFFF; /* Adjusting header color to white */
    }
    .stSelectbox, .stButton>button {
        font-family: 'Space Grotesk', sans-serif;
        color: #5FFF00;
        background-color: #010c04;
    }
    .css-2trqyj {
        font-family: 'Space Grotesk', sans-serif;
    }
    /* Specific styling for dataframe */
    .dataframe-container table {
        font-family: 'Space Mono', monospace;
    }
    .dataframe-container th {
        font-family: 'Space Mono', monospace;  /* Setting table headers font */
        color: #FFFFFF;  /* Making table headers white */
        background-color: #010c04;  /* Ensuring background matches Nosana style */
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_path = os.path.join(r'C:\Users\User\OneDrive\Documenten\GitHub\node-leaderboard-CU\leaderboard\Nosana_Logo_horizontal_color_white.png')
    st.image(logo_path, width=800)

st.markdown("<h1 style='text-align: center;'>Concurrent User Leaderboard</h1>", unsafe_allow_html=True)

cu_configs = get_cu_columns()

# CU dropdown menu (sorted and formatted)
selected_cu = st.selectbox('Select Concurrent User Configuration', cu_configs)

# Load and display data for the selected CU configuration
cu_data = load_cu_data(selected_cu)

# Display the styled leaderboard
st.dataframe(cu_data, width=1800)  # Adjust width as needed

# Calculate and display the total number of jobs and nodes
total_jobs = cu_data.shape[0]
total_nodes = cu_data['Node'].nunique()

# Counter widgets for jobs and nodes
col1, col2, col3 = st.columns([11, 3, 3])
col2.metric(label="Total Jobs", value=total_jobs)
col3.metric(label="Total Nodes", value=total_nodes)

# Add a description about the leaderboard
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <p>
            This leaderboard showcases the performance of nodes based on their Concurrent User-specific Large Language Model benchmarking results.
            Each node is evaluated based on the selected concurrent user configuration's tokens per second, total tokens, and other metrics.
        </p>
        <p>
            Use the dropdown menu above to view results for different concurrent user configurations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <footer style='text-align: center; color: #FFFFFF; font-family: "Space Grotesk", sans-serif;'>
        © NOSANA 2024. All rights reserved.
    </footer>
    """,
    unsafe_allow_html=True
)