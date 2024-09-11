import streamlit as st
import pandas as pd
import os

# Load the CSV files
results_dir = '../results'
overall_file = 'small_model_node_performance_summary.csv'
overall_data = pd.read_csv(os.path.join(results_dir, overall_file))

# Get list of model-specific CSV files
model_files = [f for f in os.listdir(results_dir) if f.startswith('model_') and f.endswith('_performance_summary.csv')]
models = ['Overall'] + [f.split('_')[1] for f in model_files]

# Function to load data based on selected model
def load_data(model):
    if model == 'Overall':
        return overall_data
    else:
        file_name = f'model_{model}_performance_summary.csv'
        return pd.read_csv(os.path.join(results_dir, file_name))

# Select the required columns
columns_to_select = ['Node', 'GPU', 'CPU', 'MeanTokensPerSecond', 'TotalProducedTokens', 'Jobs', 'Market']

# Streamlit app
st.set_page_config(page_title="Nosana Node Leaderboard", page_icon=":trophy:", layout="wide")

# Custom CSS styles (unchanged)
st.markdown(
    """
    <style>
    ... [Your existing CSS styles] ...
    </style>
    """,
    unsafe_allow_html=True
)

# Centered title with icon
st.markdown("<h1 style='text-align: center;'>🏆 Nosana Node Leaderboard 🏆</h1>", unsafe_allow_html=True)

# Load initial data
leaderboard_data = overall_data[columns_to_select]

# Rename the columns
leaderboard_data.rename(columns={
    'MeanTokensPerSecond': 'Tokens per Second',
    'TotalProducedTokens': 'Total Tokens',
}, inplace=True)

# Calculate the total amount of jobs and total amount of nodes
total_jobs = leaderboard_data['Jobs'].sum()
total_nodes = leaderboard_data['Node'].nunique()

# Round Tokens per Second column to 2 decimal places and convert to string for formatting
leaderboard_data['Tokens per Second'] = leaderboard_data['Tokens per Second'].map('{:.2f}'.format)

# Get unique markets
markets = ['All'] + sorted(leaderboard_data['Market'].unique().tolist())

# Display counter widgets
col1, col2, col3, col4 = st.columns([11, 3, 3, 9])
col2.metric(label="Total Jobs", value=total_jobs)
col3.metric(label="Total Nodes", value=total_nodes)

# Add a description about the leaderboard
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <p>
            This leaderboard showcases the performance of nodes based on their Large Language Model benchmarking results.
            Each node is evaluated based on their aggregated tokens per second. This leaderboard allows for the identification of
            the most efficient nodes within the Nosana network.
        </p>
        <p>
            Below, you will find a breakdown of each node's performance, including their hardware. You can
            search and filter the leaderboard to find specific nodes or hardware specifications.
        </p>
        <p>
            <i>*Nodes can appear multiple times in the list if they have changed their GPU or CPU configurations</i>
        </p>
        <p>
            <i>*Lamma3-70B is excluded from the overall performance because there are no benchmark results for all markets</i>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Function to display leaderboard for a specific market
def display_leaderboard(market):
    # Expander for search functionality
    with st.expander("Search Leaderboard"):
        selected_model = st.selectbox("Select Model", models, key=f"{market}_model_select")
        search_column = st.selectbox('Select column to search:', ['Node', 'GPU', 'CPU'], key=f"{market}_search_column")
        search_value = st.text_input('Enter search value:', key=f"{market}_search_value")

    # Load data for the selected model
    model_data = load_data(selected_model)
    model_data = model_data[columns_to_select]
    model_data.rename(columns={
        'MeanTokensPerSecond': 'Tokens per Second',
        'TotalProducedTokens': 'Total Tokens',
    }, inplace=True)
    model_data['Tokens per Second'] = model_data['Tokens per Second'].map('{:.2f}'.format)

    if market == 'All':
        filtered_data = model_data
    else:
        filtered_data = model_data[model_data['Market'] == market]
    
    # Remove the 'Market' column from the displayed data
    display_data = filtered_data.drop(columns=['Market'])
    
    if search_value:
        display_data = display_data[display_data[search_column].astype(str).str.contains(search_value, case=False, na=False)]
    
    # Display the styled leaderboard
    st.table(display_data)

# Create tabs for market selection
tabs = st.tabs(markets)

# Display leaderboard for each market in its respective tab
for market, tab in zip(markets, tabs):
    with tab:
        display_leaderboard(market)