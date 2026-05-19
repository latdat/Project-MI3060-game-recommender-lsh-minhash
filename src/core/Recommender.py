import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.MinHash import MinHash
from core.LSH_Engine import LSH_Engine

class Recommender:
    """
    Core recommendation engine
    """
    def __init__(self, user_index, item_index, num_hashes=100, num_bands=20, rows_per_band=5):
        self.TOP_K = 10
        self.MIN_INTERACTION = 3
        self.user_index = user_index
        self.item_index = item_index
        
        # Build MinHash signatures
        print("\n=== Đang xây dựng MinHash ===")
        self.minhash = MinHash(num_hashes=num_hashes)
        self.minhash.build_signatures(user_index)
        
        # Build LSH index
        print("\n=== Đang xây dựng LSH Index ===")
        self.lsh_engine = LSH_Engine(num_bands=num_bands, rows_per_band=rows_per_band, minhash=self.minhash)
        self.lsh_engine.build_index(user_index)
    
    def is_cold_start(self, user_id):
        """
        Kiểm tra xem user có phải cold start không
        """
        if user_id not in self.user_index:
            return True
        user = self.user_index[user_id]
        return user.get_interaction_count() < self.MIN_INTERACTION
    
    def recommend(self, user_id, top_k=None):
        """
        Gợi ý games cho user
        Returns: List of (asin, score) tuples
        """
        if top_k is None:
            top_k = self.TOP_K
        
        # Cold start: recommend popular items
        if self.is_cold_start(user_id):
            print(f"User {user_id} là cold start, đang gợi ý các items phổ biến...")
            return self.recommend_popular(top_k)
        
        target_user = self.user_index[user_id]
        target_items = target_user.get_item_set()
        
        # Tìm similar users bằng LSH
        candidates = self.lsh_engine.get_candidates(user_id)
        print(f"Tìm thấy {len(candidates)} candidate users")
        
        if len(candidates) == 0:
            print("Không tìm thấy candidates, đang gợi ý các items phổ biến...")
            return self.recommend_popular(top_k)
        
        # Tính Jaccard similarity với từng candidate
        similar_users = []
        for candidate_id in candidates:
            jaccard = self._compute_jaccard(user_id, candidate_id)
            if jaccard > 0:
                similar_users.append((candidate_id, jaccard))
        
        # Sort theo similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        print(f"Top 5 users tương đồng: {similar_users[:5]}")
        
        # Gợi ý items từ similar users
        recommendations = self._get_top_k(target_items, similar_users, top_k)
        
        return recommendations
    
    def _compute_jaccard(self, user_id1, user_id2):
        """
        Tính Jaccard similarity giữa 2 users
        """
        user1 = self.user_index[user_id1]
        user2 = self.user_index[user_id2]
        
        set1 = user1.get_item_set()
        set2 = user2.get_item_set()
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _get_top_k(self, target_items, similar_users, top_k):
        """
        Lấy top K items để gợi ý
        """
        item_scores = {}  # {asin: weighted_score}
        
        for similar_user_id, similarity in similar_users:
            similar_user = self.user_index[similar_user_id]
            
            for asin in similar_user.get_item_set():
                # Bỏ qua items mà target user đã có
                if asin in target_items:
                    continue
                
                # Accumulate weighted score
                rating = similar_user.get_rating(asin)
                weighted_score = rating * similarity
                
                if asin not in item_scores:
                    item_scores[asin] = 0.0
                item_scores[asin] += weighted_score
        
        # Sort và lấy top K
        recommendations = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return recommendations
    
    def recommend_popular(self, top_k):
        """
        Gợi ý popular items (fallback cho cold start)
        """
        # Sort items theo số lượng interactions
        popular_items = sorted(self.item_index.items(), 
                             key=lambda x: x[1].get_interaction_count(), 
                             reverse=True)[:top_k]
        
        recommendations = [(asin, item.get_interaction_count()) for asin, item in popular_items]
        return recommendations