class User:
    """
    Class đại diện cho một User trong hệ thống gợi ý
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.item_set = set()  # HashSet - Danh sách các game (asin) user đã tương tác
        self.rating_map = {}   # HashMap - {asin: rating}
    
    def get_user_id(self):
        """Lấy ID của user"""
        return self.user_id
    
    def get_item_set(self):
        """Lấy tập hợp các game user đã chơi"""
        return self.item_set
    
    def get_rating(self, asin):
        """Lấy rating của user cho một game cụ thể"""
        return self.rating_map.get(asin, 0.0)
    
    def add_item(self, asin, rating=0.0):
        """Thêm một game vào lịch sử tương tác của user"""
        self.item_set.add(asin)
        self.rating_map[asin] = rating
    
    def get_interaction_count(self):
        """Lấy số lượng game user đã tương tác"""
        return len(self.item_set)
    
    def __repr__(self):
        return f"User(id={self.user_id}, interactions={len(self.item_set)})"