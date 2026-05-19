import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.DataIO import DataIO
from utils.Timer import Timer
from core.Recommender import Recommender

class Main:
    def __init__(self):
        self.data_io = None
        self.recommender = None
        self.user_index = None
        self.item_index = None
    
    def show_menu(self):
        """Hiển thị menu"""
        print("\n" + "="*50)
        print("HỆ THỐNG GỢI Ý GAME - LSH + MinHash")
        print("="*50)
        print("1. Tải Dữ Liệu (Load Data)")
        print("2. Lấy Gợi Ý Cho User (Get Recommendations)")
        print("3. Hiển Thị Thống Kê (Show Statistics)")
        print("4. Thoát (Exit)")
        print("="*50)
    
    def run(self):
        """Chạy chương trình chính"""
        while True:
            self.show_menu()
            choice = input("Chọn tùy chọn (1-4): ").strip()
            
            if choice == '1':
                self._load_data()
            elif choice == '2':
                self._get_recommendations()
            elif choice == '3':
                self._show_statistics()
            elif choice == '4':
                print("Đang thoát... Tạm biệt!")
                break
            else:
                print("Lựa chọn không hợp lệ! Vui lòng thử lại.")
    
    def _load_data(self):
        """Load data và build recommendation system"""
        print("\n=== ĐANG TẢI DỮ LIỆU (LOADING DATA) ===")
        
        # Paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        review_file = os.path.join(base_dir, 'data', 'Video_Games_filtered.csv')
        meta_file = os.path.join(base_dir, 'data', 'meta_Video_Games_filtered.csv')
        cache_file = os.path.join(base_dir, 'data', 'recommender_cache.pkl')
        
        import pickle
        
        # Thử load từ cache trước
        if os.path.exists(cache_file):
            print(f"Đã tìm thấy file cache. Đang nạp hệ thống (Load Data) từ cache...")
            timer = Timer("Cache Loading")
            timer.start()
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                self.user_index = cache_data['user_index']
                self.item_index = cache_data['item_index']
                self.recommender = cache_data['recommender']
                timer.stop()
                print("\n[THÀNH CÔNG] Đã nạp hệ thống từ cache thành công! Lần sau sẽ tiếp tục nạp nhanh như vậy.")
                return
            except Exception as e:
                print(f"Lỗi khi đọc cache: {e}. Hệ thống sẽ tải lại dữ liệu từ đầu...")
        
        # Check files exist
        if not os.path.exists(review_file):
            print(f"Lỗi: Không tìm thấy file: {review_file}")
            return
        
        # Load data
        timer = Timer("Data Loading")
        timer.start()
        
        self.data_io = DataIO(review_file, meta_file)
        self.data_io.load_data(min_interactions=3)
        
        self.user_index = self.data_io.get_user_index()
        self.item_index = self.data_io.get_item_index()
        
        timer.stop()
        
        # Build recommender system
        timer2 = Timer("Recommender Building")
        timer2.start()
        
        self.recommender = Recommender(
            self.user_index, 
            self.item_index,
            num_hashes=100,
            num_bands=50,
            rows_per_band=2
        )
        
        timer2.stop()
        
        print("\n[THÀNH CÔNG] Đã tải dữ liệu và xây dựng hệ thống gợi ý thành công!")
        
        # Lưu vào cache để nạp nhanh cho các lần chạy sau
        print("Đang lưu hệ thống vào file cache để nạp cực nhanh (Load Data) cho lần chạy sau...")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'user_index': self.user_index,
                    'item_index': self.item_index,
                    'recommender': self.recommender
                }, f)
            print("[THÀNH CÔNG] Đã lưu cache xong!")
        except Exception as e:
            print(f"[CẢNH BÁO] Không thể lưu cache: {e}")
    
    def _get_recommendations(self):
        """Lấy recommendations cho một user"""
        if self.recommender is None:
            print("Lỗi: Vui lòng tải dữ liệu trước (Tùy chọn 1)")
            return
        
        print("\n=== LẤY GỢI Ý (GET RECOMMENDATIONS) ===")
        user_id = input("Nhập User ID: ").strip()
        
        if user_id not in self.user_index:
            print(f"Không tìm thấy User {user_id}!")
            print("Đang hiển thị các gợi ý cho cold start user...")
        
        timer = Timer("Recommendation")
        timer.start()
        
        recommendations = self.recommender.recommend(user_id, top_k=10)
        
        timer.stop()
        
        # Display results
        print(f"\n{'='*70}")
        print(f"TOP 10 GỢI Ý CHO USER: {user_id}")
        print(f"{'='*70}")
        print(f"{'Hạng':<6} {'ASIN':<15} {'Điểm':<10} {'Tựa Game':<40}")
        print(f"{'-'*70}")
        
        for rank, (asin, score) in enumerate(recommendations, 1):
            title = "Không rõ"
            if asin in self.item_index:
                item = self.item_index[asin]
                title = item.title if item.title else "Không rõ"
            
            # Truncate title if too long
            if len(title) > 37:
                title = title[:37] + "..."
            
            print(f"{rank:<6} {asin:<15} {score:<10.4f} {title:<40}")
        
        print(f"{'='*70}\n")
    
    def _show_statistics(self):
        """Hiển thị thống kê"""
        if self.user_index is None or self.item_index is None:
            print("Lỗi: Vui lòng tải dữ liệu trước (Tùy chọn 1)")
            return
        
        print("\n=== THỐNG KÊ HỆ THỐNG (SYSTEM STATISTICS) ===")
        print(f"Tổng số Users: {len(self.user_index)}")
        print(f"Tổng số Items: {len(self.item_index)}")
        
        # Average interactions per user
        avg_interactions = sum(u.get_interaction_count() for u in self.user_index.values()) / len(self.user_index)
        print(f"Lượt tương tác trung bình mỗi User: {avg_interactions:.2f}")
        
        # Top 5 most popular items
        popular_items = sorted(self.item_index.items(), 
                             key=lambda x: x[1].get_interaction_count(), 
                             reverse=True)[:5]
        
        print("\nTop 5 Game Phổ Biến Nhất:")
        for i, (asin, item) in enumerate(popular_items, 1):
            title = item.title if item.title else "Không rõ"
            print(f"  {i}. {title[:50]} ({item.get_interaction_count()} lượt tương tác)")

def main():
    """Entry point"""
    app = Main()
    app.run()

if __name__ == "__main__":
    main()