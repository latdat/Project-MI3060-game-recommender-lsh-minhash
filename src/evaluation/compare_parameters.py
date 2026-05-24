import sys
import os
import time
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.DataIO import DataIO
from core.Recommender import Recommender

def run_parameter_comparison():
    print("Running parameter comparison...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    review_file = os.path.join(base_dir, 'data', 'Video_Games_filtered.csv')
    meta_file = os.path.join(base_dir, 'data', 'meta_Video_Games_filtered.csv')
    results_dir = os.path.join(base_dir, 'results')
    charts_dir = os.path.join(results_dir, 'charts')
    
    os.makedirs(charts_dir, exist_ok=True)
    
    data_io = DataIO(review_file, meta_file)
    data_io.load_data(min_interactions=3)
    user_index = data_io.get_user_index()
    item_index = data_io.get_item_index()
    
    import random
    sample_users = random.sample(list(user_index.keys()), min(50, len(user_index)))
    
    configs = [
        (100, 20, 5),
        (100, 50, 2),
        (100, 10, 10),
        (50, 25, 2)
    ]
    
    results = []
    
    for (num_hashes, num_bands, rows_per_band) in configs:
        print(f"\nTesting Config: hashes={num_hashes}, bands={num_bands}, rows={rows_per_band}")
        recommender = Recommender(user_index, item_index, num_hashes=num_hashes, num_bands=num_bands, rows_per_band=rows_per_band)
        
        start = time.time()
        total_candidates = 0
        for u in sample_users:
            candidates = recommender.lsh_engine.get_candidates(u)
            total_candidates += len(candidates)
        query_time = time.time() - start
        avg_candidates = total_candidates / len(sample_users)
        
        results.append({
            'num_hashes': num_hashes,
            'num_bands': num_bands,
            'rows_per_band': rows_per_band,
            'query_time_50_users': query_time,
            'avg_candidates': avg_candidates
        })
        
    csv_file = os.path.join(results_dir, 'parameter_comparison.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['num_hashes', 'num_bands', 'rows_per_band', 'query_time_50_users', 'avg_candidates'])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nResults saved to {csv_file}")
    
    try:
        import matplotlib.pyplot as plt
        labels = [f"b={r['num_bands']},r={r['rows_per_band']}" for r in results]
        times = [r['query_time_50_users'] for r in results]
        cands = [r['avg_candidates'] for r in results]
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        ax2 = ax1.twinx()
        ax1.bar(labels, times, color='g', alpha=0.6, label='Query Time (s)')
        ax2.plot(labels, cands, color='b', marker='o', label='Avg Candidates')
        
        ax1.set_xlabel('Configuration')
        ax1.set_ylabel('Query Time (s)', color='g')
        ax2.set_ylabel('Avg Candidates', color='b')
        
        plt.title('Parameter Comparison (LSH)')
        fig.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'parameter_comparison_chart.png'))
        print("Chart saved.")
    except ImportError:
        print("matplotlib not installed, skipping chart generation.")

if __name__ == "__main__":
    run_parameter_comparison()
