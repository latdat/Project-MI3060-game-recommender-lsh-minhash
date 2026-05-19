class Item:
    """
    Class đại diện cho một Item (Game) trong hệ thống gợi ý
    """
    def __init__(self, asin):
        self.asin = asin  # Mã định danh game (Amazon Standard Identification Number)
        self.user_set = set()  # HashSet - Danh sách users đã tương tác với game
        self.total_rating = 0.0  # Tổng rating
        self.rating_count = 0  # Số lượng rating
        
        # Thông tin metadata (optional, load sau nếu cần)
        self.title = ""
        self.avg_rating_meta = 0.0  # Rating trung bình từ metadata
    
    def get_asin(self):
        """Lấy ASIN của game"""
        return self.asin
    
    def get_user_set(self):
        """Lấy tập hợp users đã chơi game này"""
        return self.user_set
    
    def get_avg_rating(self):
        """Tính rating trung bình từ user interactions"""
        if self.rating_count == 0:
            return 0.0
        return self.total_rating / self.rating_count
    
    def add_user(self, user_id, rating=0.0):
        """Thêm một user vào lịch sử tương tác của game"""
        self.user_set.add(user_id)
        self.total_rating += rating
        self.rating_count += 1
    
    def get_interaction_count(self):
        """Lấy số lượng users đã tương tác với game"""
        return len(self.user_set)
    
    def set_metadata(self, title, avg_rating_meta):
        """Set thông tin metadata cho game"""
        self.title = title
        self.avg_rating_meta = avg_rating_meta
    
    def __repr__(self):
        return f"Item(asin={self.asin}, interactions={len(self.user_set)}, avg_rating={self.get_avg_rating():.2f})"