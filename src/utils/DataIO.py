import csv
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.User import User
from models.Item import Item

class DataIO:
    """
    Class để load và save data
    """
    def __init__(self, review_file_path, meta_file_path=None):
        self.review_file_path = review_file_path
        self.meta_file_path = meta_file_path
        self.user_index = {}  # HashMap {user_id: User object}
        self.item_index = {}  # HashMap {asin: Item object}
    
    def load_data(self, min_interactions=3):
        """
        Load data từ CSV files
        Args:
            min_interactions: Số tương tác tối thiểu để giữ user/item
        """
        print(f"Đang tải dữ liệu từ {self.review_file_path}...")
        
        # Load review data
        with open(self.review_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                user_id = row['user_id']
                # SỬA LỖI: Sử dụng parent_asin để gộp các phiên bản game với nhau
                # và để khớp chính xác với metadata!
                asin = row.get('parent_asin') or row.get('asin', '')
                if not asin: continue
                
                rating = float(row.get('rating', 0.0))
                
                # Tạo User object nếu chưa tồn tại
                if user_id not in self.user_index:
                    self.user_index[user_id] = User(user_id)
                
                # Tạo Item object nếu chưa tồn tại
                if asin not in self.item_index:
                    self.item_index[asin] = Item(asin)
                
                # Thêm interaction
                self.user_index[user_id].add_item(asin, rating)
                self.item_index[asin].add_user(user_id, rating)
                
                count += 1
                if count % 10000 == 0:
                    print(f"Đã tải {count} interactions...")
        
        print(f"Đã tải {count} interactions")
        print(f"Tổng số users: {len(self.user_index)}")
        print(f"Tổng số items: {len(self.item_index)}")
        
        # Filter users/items với ít tương tác
        self._filter_sparse_data(min_interactions)
        
        # Load metadata nếu có
        if self.meta_file_path:
            self._load_metadata()
    
    def _filter_sparse_data(self, min_interactions):
        """
        Lọc bỏ users và items có ít tương tác
        """
        print(f"Đang lọc các users/items có < {min_interactions} interactions...")
        
        # Filter users
        users_to_remove = [uid for uid, user in self.user_index.items() 
                          if user.get_interaction_count() < min_interactions]
        for uid in users_to_remove:
            del self.user_index[uid]
        
        # Filter items
        items_to_remove = [asin for asin, item in self.item_index.items() 
                          if item.get_interaction_count() < min_interactions]
        for asin in items_to_remove:
            del self.item_index[asin]
        
        print(f"Sau khi lọc: {len(self.user_index)} users, {len(self.item_index)} items")
    
    def _load_metadata(self):
        """
        Load metadata cho items (title, avg_rating, etc.)
        """
        print(f"Đang tải metadata từ {self.meta_file_path}...")
        
        try:
            with open(self.meta_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                
                for row in reader:
                    # Khớp đúng ID đã lấy ở phần load reviews
                    parent_asin = row.get('parent_asin') or row.get('asin', '')
                    title = row.get('title', 'Không rõ')
                    avg_rating = float(row.get('average_rating', 0.0) or 0.0)
                    
                    # Update item nếu tồn tại trong item_index
                    if parent_asin in self.item_index:
                        self.item_index[parent_asin].set_metadata(title, avg_rating)
                        count += 1
                
                print(f"Đã tải metadata cho {count} items")
        except Exception as e:
            print(f"Cảnh báo: Không thể tải metadata: {e}")
    
    def get_user_index(self):
        """Lấy user index"""
        return self.user_index
    
    def get_item_index(self):
        """Lấy item index"""
        return self.item_index
    
    def save_data(self, output_path):
        """
        Save processed data (optional - để sau)
        """
        pass