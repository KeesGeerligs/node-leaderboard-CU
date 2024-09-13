import json
import pandas as pd
import os
import argparse

# Market ID to market name mapping
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
    "3EWVbggirRpDY2npzPDA7k21yzwz5wgwGxVVv6zCnRpa": "Laptop",
    "F3aGGSMb73XHbJbDXVbcXo7iYM9fyevvAZGQfwgrnWtB": "A100 40GB"
}

# Load JSON data from file
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Check if the job contains all necessary information
def has_valid_performance_data(job):
    required_fields = ["totalDuration", "totalTokensProduced", "totalInputTokens", "averageTokensPerSecond", "NosanaPrice"]
    if not job.get("node") or not job.get("market") or not job.get("price") or not job.get("duration"):
        return False
    performance = job.get("data", {}).get("performance", {})
    if not performance:
        return False
    for metrics in performance.values():
        if not all(field in metrics and metrics[field] is not None for field in required_fields):
            return False
    return True

# Calculate startup time
def calculate_startup_time(duration, total_cu_duration):
    return duration - total_cu_duration

# Calculate price per million tokens, netto token per second, and GPU price per hour
def calculate_price_per_million_tokens(produced_tokens, input_tokens, total_duration, price, nosana_price):
    if not all([produced_tokens, input_tokens, total_duration, nosana_price]):
        return None, None, None
    total_tokens = produced_tokens + input_tokens
    netto_token_per_second = total_tokens / total_duration
    million_tokens_per_second = netto_token_per_second / 1_000_000
    price_per_second = (price / 1_000_000) * nosana_price
    gpu_price_per_hour = price_per_second * 3600
    price_per_million_tokens = price_per_second / million_tokens_per_second if million_tokens_per_second != 0 else None
    return price_per_million_tokens, netto_token_per_second, gpu_price_per_hour

# Extract performance data from the JSON
def extract_performance_data(data):
    performance_data = []
    
    for job_id, job in data.items():
        if not has_valid_performance_data(job):
            continue

        node_id = job.get("node")
        market_name = MARKET_MAP.get(job.get("market"), "Unknown")
        specs = job.get("data", {}).get("specs", {})
        performance = job.get("data", {}).get("performance", {})
        price = float(job.get("price", 0))
        duration = float(job.get("duration", 0))

        nosana_price = next(iter(performance.values()), {}).get("NosanaPrice", None)
        cpu = specs.get("cpu")
        gpu_info = specs.get("gpu_info", {}).get("1", {})
        gpu_name = gpu_info.get("name", "Unknown GPU")
        
        total_cu_duration = sum(metrics.get("totalDuration", 0) for metrics in performance.values())

        # Initialize a dictionary to store CU-specific metrics
        cu_metrics = {
            "Node": node_id,
            "Market": market_name,
            "GPU": gpu_name,
            "CPU": cpu,
            "Price": price,
            "Duration": duration,
            "StartupTime": calculate_startup_time(duration, total_cu_duration),
            "ModelName": None,
            "NosanaPrice": nosana_price,
            "GPU-Price-Per-Hour": None
        }

        # Iterate over each CU configuration
        for cu_key, metrics in performance.items():
            cu_count = metrics.get("concurrentUsers", 0)
            tokens_per_second = metrics.get("averageTokensPerSecond", 0)
            total_tokens_produced = metrics.get("totalTokensProduced", 0)
            total_duration = metrics.get("totalDuration", 0)
            average_latency = metrics.get("averageLatency", 0)
            total_input_tokens = metrics.get("totalInputTokens", 0)
            avg_clock_speed = metrics.get("AvgClockSpeed", 0)
            avg_power_usage = metrics.get("AvgPowerUsage", 0)
            avg_utilization = metrics.get("AvgUtilization", 0)
            model_name = metrics.get("modelName", "Unknown Model")

            cu_metrics["ModelName"] = model_name

            # Calculate price per million tokens and netto token per second
            price_per_million_tokens, netto_token_per_second, gpu_price_per_hour = calculate_price_per_million_tokens(
                total_tokens_produced, total_input_tokens, total_duration, price, nosana_price)

            if cu_metrics["GPU-Price-Per-Hour"] is None:
                cu_metrics["GPU-Price-Per-Hour"] = gpu_price_per_hour

            cu_prefix = f"CU{cu_count}"
            cu_metrics.update({
                f"{cu_prefix}_MeanTokensPerSecond": tokens_per_second,
                f"{cu_prefix}_TotalDuration": total_duration,
                f"{cu_prefix}_TotalProducedTokens": total_tokens_produced,
                f"{cu_prefix}_AverageLatency": average_latency,
                f"{cu_prefix}_TotalInputTokens": total_input_tokens,
                f"{cu_prefix}_AvgClockSpeed": avg_clock_speed,
                f"{cu_prefix}_AvgPowerUsage": avg_power_usage,
                f"{cu_prefix}_AvgUtilization": avg_utilization,
                f"{cu_prefix}_PricePerMillionTokens": price_per_million_tokens,
                f"{cu_prefix}_NettoTokensPerSecond": netto_token_per_second
            })

        performance_data.append(cu_metrics)

    return pd.DataFrame(performance_data)

# Main function to process data and save to CSV
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

    performance_summary_file = os.path.join(results_dir, 'CU_benchmark_results_Nosana.csv')
    performance_df.to_csv(performance_summary_file, index=False)

    print("\nCompressed Performance Summary:")
    print(performance_df.to_string(index=False))

if __name__ == "__main__":
    main()
