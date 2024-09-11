import matplotlib.pyplot as plt
import pandas as pd

# Data
markets = ['4090', 'A100', 'H100', '3090', 'A6000', '4080', '3080', '4070', 'A5000', '3070', '3060', 'A40', 'Laptop', 'A4000', '4060']
max_performance = [127.19, 113.98, 113.92, 110.96, 104.64, 101.02, 97.39, 97.09, 92.28, 84.90, 81.64, 79.73, 66.49, 64.22, 50.47]
average_performance = [94.17, 73.10, 96.43, 78.90, 82.50, 72.72, 63.15, 63.94, 87.26, 51.15, 45.68, 69.53, 26.71, 52.86, 42.98]

# Create DataFrame
df = pd.DataFrame({
    'Market': markets,
    'Max': max_performance,
    'Average': average_performance
})

# Sort DataFrame by Max performance
df = df.sort_values('Max', ascending=False)

# Create the plot
plt.figure(figsize=(12, 8))
bar_width = 0.35
index = range(len(df['Market']))

plt.bar(index, df['Max'], bar_width, label='Max', color='#1f77b4', alpha=0.8)
plt.bar([i + bar_width for i in index], df['Average'], bar_width, label='Average', color='#ff7f0e', alpha=0.8)

# Customize the plot
plt.xlabel('Market', fontsize=12)
plt.ylabel('Tokens per Second', fontsize=12)
plt.title('Llama3-8B Inference Speed per Market: Max vs Average', fontsize=14)
plt.xticks([i + bar_width/2 for i in index], df['Market'], rotation=45, ha='right')
plt.legend()

# Add value labels on top of each bar
for i, v in enumerate(df['Max']):
    plt.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=8)
for i, v in enumerate(df['Average']):
    plt.text(i + bar_width, v, f'{v:.1f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()