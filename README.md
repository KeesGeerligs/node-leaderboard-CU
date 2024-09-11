# Nosana Analysis

## Overview

This repository contains tools to extract LLM benchmarking info from the Nosana network, aswell as tools for analyzing Nosana LLM benchmarking metrics of different hardware configurations.

## Repository Structure

- `collecting`: Contains the `extract.js` script used for data extraction.
- `analysis`: Contains the `statistics.py` script used for performing statistical analysis on the collected data.
- `leaderboard`: Contains the `leaderboard_app.py` script used for visualizing the collected data.

## Prerequisites

- Node.js and npm (for running JavaScript code in the `collecting` folder)
- Python 3 and pip (for running Python code in the `analysis` folder)

## Setup and Running Instructions

### Data Collection

1. **Install Python Dependencies:**  
    ```bash
    pip install -r requirements.txt
    ```

2. **Navigate to the Collecting Folder:**
   ```bash
   cd collecting
   ```
3. **Install JavaScript Dependencies:**
    ```bash
    npm install
    ```
4. **Run the Data Extraction Script:**
    ```bash
    npm run extract
    ```

### Data Analysis
5. **Navigate to the Analysis Folder:**
    ```bash
    cd analysis
    ```
6. **Run the Statistical Analysis Script:**
    ```bash
    python statistics.py
    ```

### Leaderboard Application

7. **Navigate to the Leaderboard Folder:**
   ```bash
   cd leaderboard
    ```
8. **Run the streamlit application:**
    ```bash
    streamlit run leaderboard_app.py
    ```