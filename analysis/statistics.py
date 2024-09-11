import json
import pandas as pd
from collections import defaultdict
import argparse

# Define the mapping from market IDs to market names
MARKET_MAP = {
    "Crop49jpc7prcgAcS82WbWyGHwbN5GgDym3uFbxxCTZg": "H100",
    "GLJHzqRN9fKGBsvsFzmGnaQGknUtLN1dqaFR8n3YdM22": "A100",
    "EjryZ6XEthz3z7nnLfjXBYafyn7VyHgChfbfM47LfAao": "A6000",
    "BLqSzPzcXMX5gseNXE4Ma45f31Eo6tNFVYoRmPG7kxP2": "A40",
    "97G9NnvBDQ2WpKu6fasoMsAKmfj63C9rhysJnkeWodAf": "4090",
    "4uBye3vJ1FAYukDdrvqQ36MZZZxqW3o8utWu8fyomRuN": "A5000",
    "7fnuvPYzfd961iRDPRgMSKLrUf1QjTGnn7viu3P12Zuc": "A4000",
    "3XGECQon74HQwPJuZjgCwqdQ5Nt3wktZ9fcavcDN9qB2": "Enterprise 8xA5000",
    "7RepDm4Xt9k6qV5oiSHvi8oBoty4Q2tfBGnCYjFLj6vA": "3080",
    "77wdaAuYVxBW5u2QiqddkAzoBZ5cuKxH9ZCbx5HfFUb2": "4080",
    "EzuHhkrhmV98HWzREsgLenKj2iHdJgrKmzfL8psP8Aso": "4070",
    "47LQHZwT7gfVoBDYnRYhsYv6vKk8a1oW3Y3SdHAp1gTr": "4060",
    "CA5pMpqkYFKtme7K31pNB1s62X2SdhEv1nN9RdxKCpuQ": "3090",
    "7AtiXMSH6R1jjBxrcYjehCkkSF7zvYWte63gwEDBcGHq": "3060",
    "RXP7JK8MTY4uPJng4UjC9ZJdDDSG6wGr8pvVf3mwgXF": "3070",
    "3EWVbggirRpDY2npzPDA7k21yzwz5wgwGxVVv6zCnRpa": "Laptop"
}

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_info(data):
    cpu_counts = defaultdict(int)
    gpu_counts = defaultdict(int)
    node_job_counts = defaultdict(int)
    seen_nodes = set()
    total_jobs = 0
    gpu_cpu_combinations = defaultdict(int)

    for job_id, job in data.items():
        total_jobs += 1
        node_id = job.get("node")
        node_job_counts[node_id] += 1

        if node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)

        specs = job.get("data", {}).get("specs", {})
        cpu = specs.get("cpu")
        if cpu:
            cpu_counts[cpu] += 1

        gpu_info = specs.get("gpu_info", {})
        for key, value in gpu_info.items():
            if isinstance(value, dict):
                gpu_name = value.get("name")
                if gpu_name:
                    gpu_counts[gpu_name] += 1
                    if cpu:
                        gpu_cpu_combinations[(gpu_name, cpu)] += 1
    
    return cpu_counts, gpu_counts, len(seen_nodes), total_jobs, node_job_counts, gpu_cpu_combinations

def extract_performance_data(data):
    performance_data = []

    for job_id, job in data.items():
        node_id = job.get("node")
        market_id = job.get("market")  # Get the market ID
        market_name = MARKET_MAP.get(market_id, "Unknown")  # Map to market name
        specs = job.get("data", {}).get("specs", {})
        performance = job.get("data", {}).get("performance", {})

        cpu = specs.get("cpu")
        gpu_info = specs.get("gpu_info", {})
        
        for gpu_key, gpu_value in gpu_info.items():
            if isinstance(gpu_value, dict):
                gpu_name = gpu_value.get("name")
                
                for model, metrics in performance.items():
                    tokens_per_second = metrics.get("tokensPerSecond")
                    produced_tokens = metrics.get("producedTokens")
                    
                    if tokens_per_second is not None and produced_tokens is not None:
                        performance_data.append({
                            "Node": node_id,
                            "JobID": job_id,
                            "Market": market_name,
                            "GPU": gpu_name,
                            "CPU": cpu,
                            "Model": model,
                            "TokensPerSecond": tokens_per_second,
                            "ProducedTokens": produced_tokens
                        })
    
    return pd.DataFrame(performance_data)

def analyze_small_model_node_performance(performance_df):
    # Exclude llama3_70b instances
    filtered_df = performance_df[performance_df['Model'] != 'llama3_70b']
    
    small_model_node_performance = filtered_df.groupby(['Node', 'Market', 'GPU', 'CPU']).agg(
        MeanTokensPerSecond=('TokensPerSecond', 'mean'),
        TotalProducedTokens=('ProducedTokens', 'sum')
    ).reset_index()

    job_gpu_node_counts = filtered_df.groupby(['Node', 'Market', 'GPU', 'CPU', 'JobID']).size().groupby(['Node', 'Market', 'GPU', 'CPU']).size().reset_index(name='Jobs')

    small_model_node_performance = pd.merge(small_model_node_performance, job_gpu_node_counts, on=['Node', 'Market', 'GPU', 'CPU'])

    return small_model_node_performance.sort_values(by='MeanTokensPerSecond', ascending=False)

def analyze_model_performance(performance_df, model):
    model_df = performance_df[performance_df['Model'] == model]
    
    model_performance_summary = model_df.groupby(['Node', 'Market', 'GPU', 'CPU']).agg(
        MeanTokensPerSecond=('TokensPerSecond', 'mean'),
        TotalProducedTokens=('ProducedTokens', 'sum')
    ).reset_index()

    job_counts = model_df.groupby(['Node', 'Market', 'GPU', 'CPU', 'JobID']).size().groupby(['Node', 'Market', 'GPU', 'CPU']).size().reset_index(name='Jobs')

    model_performance_summary = pd.merge(model_performance_summary, job_counts, on=['Node', 'Market', 'GPU', 'CPU'])

    model_performance_summary['MeanTokensPerSecond'] = model_performance_summary['MeanTokensPerSecond'].round(2)

    return model_performance_summary.sort_values(by='MeanTokensPerSecond', ascending=False)

def analyze_node_complications(data, node_job_counts):
    node_complications = defaultdict(lambda: {"no_performance_data": 0, "total_jobs": 0})
    seen_nodes_with_complications = set()
    total_complications = 0

    for job_id, job in data.items():
        node_id = job.get("node")
        performance = job.get("data", {}).get("performance", {})

        if not performance:
            node_complications[node_id]["no_performance_data"] += 1
            seen_nodes_with_complications.add(node_id)
            total_complications += 1

        node_complications[node_id]["total_jobs"] = node_job_counts[node_id]

    for node_id in list(node_complications.keys()):
        no_performance_data = node_complications[node_id]["no_performance_data"]
        total_jobs = node_complications[node_id]["total_jobs"]
        if total_jobs > 0:
            node_complications[node_id]["complication_percentage"] = (no_performance_data / total_jobs) * 100
        else:
            node_complications[node_id]["complication_percentage"] = 0

    filtered_node_complications = {node: data for node, data in node_complications.items() if data["no_performance_data"] > 0}

    return pd.DataFrame.from_dict(filtered_node_complications, orient='index').reset_index().rename(columns={'index': 'Node'}), len(seen_nodes_with_complications), total_complications

def calculate_max_tokens_per_second(performance_df):
    max_tokens_per_second = performance_df.groupby(['GPU', 'Model'])['TokensPerSecond'].max().reset_index()
    max_tokens_per_second = max_tokens_per_second.sort_values(by=['GPU', 'TokensPerSecond'], ascending=[True, False])
    max_tokens_per_second['TokensPerSecond'] = max_tokens_per_second['TokensPerSecond'].round(2)
    return max_tokens_per_second

def calculate_max_performance_per_market(performance_df, model='llama3'):
    model_df = performance_df[performance_df['Model'] == model]
    max_performance = model_df.groupby('Market')['TokensPerSecond'].max().reset_index()
    max_performance = max_performance.sort_values('TokensPerSecond', ascending=False)
    max_performance['TokensPerSecond'] = max_performance['TokensPerSecond'].round(2)
    return max_performance

def calculate_avg_performance_per_market(performance_df, model='llama3'):
    model_df = performance_df[performance_df['Model'] == model]
    avg_performance = model_df.groupby('Market')['TokensPerSecond'].mean().reset_index()
    avg_performance = avg_performance.sort_values('TokensPerSecond', ascending=False)
    avg_performance['TokensPerSecond'] = avg_performance['TokensPerSecond'].round(2)
    return avg_performance

def main():
    parser = argparse.ArgumentParser(description='Analyze benchmark data.')
    parser.add_argument('--hardware', action='store_true', help='Print unique GPU and CPU counts')
    parser.add_argument('--node', action='store_true', help='Print node performance')
    parser.add_argument('--gpu', action='store_true', help='Print GPU performance')
    parser.add_argument('--max', action='store_true', help='Print maximum observed tokens per second for each GPU and model')
    parser.add_argument('--complications', action='store_true', help='Print node complications')
    parser.add_argument('file_path', nargs='?', default='../data/benchmark_data.json', type=str, help='Path to the benchmark data JSON file')
    args = parser.parse_args()

    data = load_data(args.file_path)

    cpu_counts, gpu_counts, unique_nodes_count, total_jobs, node_job_counts, gpu_cpu_combinations = extract_info(data)


    cpu_df = pd.DataFrame(cpu_counts.items(), columns=['CPU', 'Count'])
    gpu_df = pd.DataFrame(gpu_counts.items(), columns=['GPU', 'Count'])

    # Create a DataFrame for GPU-CPU combinations
    combinations_df = pd.DataFrame([(gpu, cpu, count) for (gpu, cpu), count in gpu_cpu_combinations.items()],
                                   columns=['GPU', 'CPU', 'Count'])
    combinations_df = combinations_df.sort_values('Count', ascending=False).head(10)


    performance_df = extract_performance_data(data)

    print(f"\nTotal number of unique nodes analyzed: {unique_nodes_count}")
    print(f"Total number of jobs analyzed: {total_jobs}")

    if args.hardware:
        print("CPU Overview:")
        print(cpu_df.to_string(index=False))
        print("\nGPU Overview:")
        print(gpu_df.to_string(index=False))
        print(f"\nTotal number of unique GPUs: {gpu_df.shape[0]}")
        print(f"Total number of unique CPUs: {cpu_df.shape[0]}")

        print("\nTop 10 Most Frequent GPU-CPU Combinations:")
        print(combinations_df.to_string(index=False))

    models = performance_df['Model'].unique()
    for model in models:
        model_performance_summary = analyze_model_performance(performance_df, model)
        # If model name is llama3_70b, save the file as llama3-70b_performance_summary.csv
        if model == 'llama3_70b':
            csv_filename = f'../results/model_llama3-70b_performance_summary.csv'
        else:
            csv_filename = f'../results/model_{model}_performance_summary.csv'
        model_performance_summary.to_csv(csv_filename, index=False)

    small_model_gpu_performance = performance_df[performance_df['Model'] != 'llama3_70b'].groupby('GPU').agg(
        MeanTokensPerSecond=('TokensPerSecond', 'mean'),
        TotalProducedTokens=('ProducedTokens', 'sum')
    ).reset_index()

    small_model_gpu_performance['MeanTokensPerSecond'] = small_model_gpu_performance['MeanTokensPerSecond'].round(2)

    gpu_job_counts = performance_df[performance_df['Model'] != 'llama3_70b'].groupby(['GPU', 'Node', 'JobID']).size().groupby('GPU').size().reset_index(name='Jobs')

    small_model_gpu_performance = pd.merge(small_model_gpu_performance, gpu_job_counts, on='GPU')

    small_model_gpu_performance = small_model_gpu_performance.sort_values(by='MeanTokensPerSecond', ascending=False)

    if args.gpu:
        print("\nSmall Model GPU Performance:")
        print(small_model_gpu_performance.to_string(index=False))
        print(f"\nTotal number of unique jobs with GPU data: {gpu_job_counts['Jobs'].sum()}")

    small_model_gpu_performance.to_csv('../results/small_model_gpu_performance.csv', index=False)

    small_model_node_performance = analyze_small_model_node_performance(performance_df)

    small_model_node_performance['MeanTokensPerSecond'] = small_model_node_performance['MeanTokensPerSecond'].round(2)

    if args.node:
        print("\nSmall Model Node Performance Summary:")
        print(small_model_node_performance.to_string(index=False))
        print(f"\nTotal number of jobs with performance data: {small_model_node_performance['Jobs'].sum()}")

    small_model_node_performance.to_csv('../results/small_model_node_performance_summary.csv', index=False)

    node_complications_df, unique_nodes_with_complications, total_complications = analyze_node_complications(data, node_job_counts)

    if args.complications:
        print("\nNode Complications:")
        print(node_complications_df.to_string(index=False))
        print(f"\nTotal number of unique nodes with complications: {unique_nodes_with_complications}")
        print(f"Total number of complications: {total_complications}")

    if args.max:
        max_tokens_per_second = calculate_max_tokens_per_second(performance_df)
        llama3_max_tokens_per_second = max_tokens_per_second[max_tokens_per_second['Model'] == 'llama3']
        print("\nMaximum Observed Tokens per Second for llama3:")
        print(llama3_max_tokens_per_second.to_string(index=False))

        # New addition: Highest performance per market for llama3
        max_performance_per_market = calculate_max_performance_per_market(performance_df, 'llama3')
        print("\nHighest Performance per Market for llama3:")
        print(max_performance_per_market.to_string(index=False))

         # New addition: Average performance per market for llama3
        avg_performance_per_market = calculate_avg_performance_per_market(performance_df, 'llama3')
        print("\nAverage Performance per Market for llama3:")
        print(avg_performance_per_market.to_string(index=False))

if __name__ == "__main__":
    main()
