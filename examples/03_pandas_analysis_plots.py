"""
Example 03: Loading CSV Results into Pandas and Generating Publication Plots
"""

import pandas as pd
import os

def analyze_and_plot(csv_path="output/benchmark_queries.csv"):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} does not exist. Run benchmark first!")
        return

    df = pd.read_csv(csv_path)
    print("Dataset Overview:")
    print(df.head())

    # Share of model by engine
    sov_by_model = df.groupby("model")["target_mentioned"].apply(lambda s: (s == "YES").mean() * 100)
    print("\nShare of Model (%):")
    print(sov_by_model)

    top1_by_model = df.groupby("model")["target_is_top_1"].apply(lambda s: (s == "YES").mean() * 100)
    print("\nTop-1 Pick Rate (%):")
    print(top1_by_model)

if __name__ == "__main__":
    analyze_and_plot()
