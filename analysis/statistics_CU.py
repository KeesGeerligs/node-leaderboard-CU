import json
import pandas as pd
import os
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

def extract_performance_data(data):
    performance_data = []

    for job_id, job in data.items():
        node_id = job.get("node")
        market_id = job.get("market")
        market_name = MARKET_MAP.get(market_id, "Unknown")
        specs = job.get("data", {}).get("specs", {})
        performance = job.get("data", {}).get("performance", {})
        price = job.get("price", None)
        duration = job.get("duration", None)

        # Skip jobs with empty specs or performance data
        if not specs or not performance:
            continue

        cpu = specs.get("cpu")
        gpu_info = specs.get("gpu_info", {})

        if gpu_info and isinstance(gpu_info.get("1"), dict):
            gpu_name = gpu_info["1"].get("name", "Unknown GPU")
        else:
            gpu_name = "Unknown GPU"

        # Initialize a dictionary to hold CU metrics, including price, duration, and total input tokens
        cu_metrics = {
            "Node": node_id,
            "Market": market_name,
            "GPU": gpu_name,
            "CPU": cpu,
            "Price": price,
            "Duration": duration,
            "ModelName": None,
            "Jobs": len(performance),
            "CU1_MeanTokensPerSecond": None,
            "CU1_TotalDuration": None,
            "CU1_TotalProducedTokens": None,
            "CU1_AverageLatency": None,
            "CU1_TotalInputTokens": None,
            "CU5_MeanTokensPerSecond": None,
            "CU5_TotalDuration": None,
            "CU5_TotalProducedTokens": None,
            "CU5_AverageLatency": None,
            "CU5_TotalInputTokens": None,
            "CU10_MeanTokensPerSecond": None,
            "CU10_TotalDuration": None,
            "CU10_TotalProducedTokens": None,
            "CU10_AverageLatency": None,
            "CU10_TotalInputTokens": None,
            "CU50_MeanTokensPerSecond": None,
            "CU50_TotalDuration": None,
            "CU50_TotalProducedTokens": None,
            "CU50_AverageLatency": None,
            "CU50_TotalInputTokens": None,
            "CU100_MeanTokensPerSecond": None,
            "CU100_TotalDuration": None,
            "CU100_TotalProducedTokens": None,
            "CU100_AverageLatency": None,
            "CU100_TotalInputTokens": None
        }

        for cu_key, metrics in performance.items():
            cu_count = metrics.get("concurrentUsers", 0)
            tokens_per_second = metrics.get("averageTokensPerSecond", 0)
            total_tokens_produced = metrics.get("totalTokensProduced", 0)
            total_duration = metrics.get("totalDuration", 0)
            average_latency = metrics.get("averageLatency", 0)
            total_input_tokens = metrics.get("totalInputTokens", 0)  # Assuming this field is present
            model_name = metrics.get("modelName", "Unknown Model")

            # Assign the model name
            cu_metrics["ModelName"] = model_name

            # Update CU-specific fields, including total input tokens
            if cu_count == 1:
                cu_metrics["CU1_MeanTokensPerSecond"] = tokens_per_second
                cu_metrics["CU1_TotalDuration"] = total_duration
                cu_metrics["CU1_TotalProducedTokens"] = total_tokens_produced
                cu_metrics["CU1_AverageLatency"] = average_latency
                cu_metrics["CU1_TotalInputTokens"] = total_input_tokens
            elif cu_count == 5:
                cu_metrics["CU5_MeanTokensPerSecond"] = tokens_per_second
                cu_metrics["CU5_TotalDuration"] = total_duration
                cu_metrics["CU5_TotalProducedTokens"] = total_tokens_produced
                cu_metrics["CU5_AverageLatency"] = average_latency
                cu_metrics["CU5_TotalInputTokens"] = total_input_tokens
            elif cu_count == 10:
                cu_metrics["CU10_MeanTokensPerSecond"] = tokens_per_second
                cu_metrics["CU10_TotalDuration"] = total_duration
                cu_metrics["CU10_TotalProducedTokens"] = total_tokens_produced
                cu_metrics["CU10_AverageLatency"] = average_latency
                cu_metrics["CU10_TotalInputTokens"] = total_input_tokens
            elif cu_count == 50:
                cu_metrics["CU50_MeanTokensPerSecond"] = tokens_per_second
                cu_metrics["CU50_TotalDuration"] = total_duration
                cu_metrics["CU50_TotalProducedTokens"] = total_tokens_produced
                cu_metrics["CU50_AverageLatency"] = average_latency
                cu_metrics["CU50_TotalInputTokens"] = total_input_tokens
            elif cu_count == 100:
                cu_metrics["CU100_MeanTokensPerSecond"] = tokens_per_second
                cu_metrics["CU100_TotalDuration"] = total_duration
                cu_metrics["CU100_TotalProducedTokens"] = total_tokens_produced
                cu_metrics["CU100_AverageLatency"] = average_latency
                cu_metrics["CU100_TotalInputTokens"] = total_input_tokens

        performance_data.append(cu_metrics)

    return pd.DataFrame(performance_data)

def main():
    parser = argparse.ArgumentParser(description='Analyze benchmark data.')
    parser.add_argument('--file_path', default='data/benchmark_data.json', help='Path to the benchmark data JSON file')
    args = parser.parse_args()

    data = load_data(args.file_path)

    performance_df = extract_performance_data(data)

    print(f"\nTotal number of jobs analyzed: {len(performance_df)}")

    # Save the final DataFrame to CSV
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    performance_summary_file = os.path.join(results_dir, 'CU_benchmark_results_with_price_duration_input_tokens.csv')
    performance_df.to_csv(performance_summary_file, index=False)

    print("\nCompressed Performance Summary:")
    print(performance_df.to_string(index=False))

if __name__ == "__main__":
    main()
