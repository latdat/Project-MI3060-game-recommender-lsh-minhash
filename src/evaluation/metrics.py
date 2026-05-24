import random
from utils.Timer import Timer

def evaluate_system(recommender, user_index, item_index, num_samples=100):
    print(f"\n=== ĐANG ĐÁNH GIÁ HỆ THỐNG ({num_samples} USERS) ===")
    
    timer = Timer("Evaluation")
    timer.start()
    
    # Lọc những user có ít nhất 2 items để có thể ẩn 1 item làm test
    valid_users = [uid for uid, u in user_index.items() if u.get_interaction_count() >= 2]
    
    if len(valid_users) < num_samples:
        num_samples = len(valid_users)
        
    sampled_user_ids = random.sample(valid_users, num_samples)
    
    total_precision = 0.0
    total_candidates = 0
    unique_recommended_items = set()
    total_users_evaluated = 0
    
    for user_id in sampled_user_ids:
        user = user_index[user_id]
        items = list(user.get_item_set())
        
        # Chọn ngẫu nhiên 1 item làm holdout (ground truth)
        holdout_item = random.choice(items)
        
        # Tạm thời xóa item này khỏi set của user để hệ thống không filter nó đi
        user.item_set.remove(holdout_item)
        
        # Đếm số lượng candidate
        candidates = recommender.lsh_engine.get_candidates(user_id)
        total_candidates += len(candidates)
        
        # Lấy top 10 recommendations
        recommendations = recommender.recommend(user_id, top_k=10)
        
        # Khôi phục lại item cho user
        user.item_set.add(holdout_item)
        
        # Tính Precision@10: Nếu item holdout nằm trong top 10
        rec_asins = [asin for asin, score in recommendations]
        if holdout_item in rec_asins:
            total_precision += 1.0 # 1 out of 1 item is found -> precision=100% or we can just say hits
            
        for asin in rec_asins:
            unique_recommended_items.add(asin)
            
        total_users_evaluated += 1
        
    timer.stop()
    
    # Calculate final metrics
    avg_precision = (total_precision / total_users_evaluated) * 100 if total_users_evaluated > 0 else 0
    coverage = (len(unique_recommended_items) / len(item_index)) * 100 if len(item_index) > 0 else 0
    avg_candidates = total_candidates / total_users_evaluated if total_users_evaluated > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"KẾT QUẢ ĐÁNH GIÁ (EVALUATION RESULTS)")
    print(f"{'='*50}")
    print(f"Số lượng Users test: {total_users_evaluated}")
    print(f"Hit Rate (Precision@10): {avg_precision:.2f}%")
    print(f"Coverage (Độ phủ items): {coverage:.2f}% ({len(unique_recommended_items)}/{len(item_index)} items)")
    print(f"Avg Candidates: {avg_candidates:.2f} users/truy vấn")
    print(f"{'='*50}\n")
