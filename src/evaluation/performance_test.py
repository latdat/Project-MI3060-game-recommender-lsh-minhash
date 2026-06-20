import sys
import os
import time
import csv

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.DataIO import DataIO
from core.Recommender import Recommender
from evaluation.metrics import evaluate_system

def run_performance_test():
    print("Running performance test...")
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    review_file = os.path.join(base_dir, 'data', 'Video_Games_filtered.csv')
    meta_file = os.path.join(base_dir, 'data', 'meta_Video_Games_filtered.csv')
    results_dir = os.path.join(base_dir, 'results')
    charts_dir = os.path.join(results_dir, 'charts')
    
    os.makedirs(charts_dir, exist_ok=True)
    
    # Load data
    data_io = DataIO(review_file, meta_file)
    data_io.load_data(min_interactions=3)
    user_index = data_io.get_user_index()
    item_index = data_io.get_item_index()
    
    # Measure build time
    start = time.time()
    recommender = Recommender(user_index, item_index, num_hashes=100, num_bands=50, rows_per_band=2)
    build_time = time.time() - start
    
    # Measure query time for 100 users
    import random
    sample_users = random.sample(list(user_index.keys()), min(100, len(user_index)))
    start = time.time()
    for u in sample_users:
        recommender.recommend(u, top_k=10)
    query_time_100 = time.time() - start
    avg_query_time = query_time_100 / len(sample_users)
    
    # Save to CSV
    csv_file = os.path.join(results_dir, 'performance_results.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Index Build Time', f"{build_time:.4f}"])
        writer.writerow(['Total Query Time', f"{query_time_100:.4f}"])
        writer.writerow(['Average Query Time', f"{avg_query_time:.4f}"])
        
    print(f"Results saved to {csv_file}")
    
    # Generate simple chart
    try:
        import matplotlib.pyplot as plt
        metrics = ['Build Time', 'Avg Query']
        values = [build_time, avg_query_time * 1000]
        
        plt.figure(figsize=(8, 5))
        plt.bar(metrics, values, color=['blue', 'orange'])
        plt.title('Performance Metrics')
        plt.ylabel('Time')
        plt.savefig(os.path.join(charts_dir, 'performance_chart.png'))
        print("Chart saved.")
    except ImportError:
        print("matplotlib not installed, skipping chart generation.")

if __name__ == "__main__":
    run_performance_test()
