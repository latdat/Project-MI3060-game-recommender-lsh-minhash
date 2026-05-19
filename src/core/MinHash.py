import random
import hashlib

class MinHash:
    """
    MinHash algorithm để tạo signatures cho user sets
    Dùng để estimate Jaccard similarity
    """
    def __init__(self, num_hashes=100):
        self.num_hashes = num_hashes  # Số lượng hash functions
        self.hash_functions = []  # List các hash functions
        self.signatures = {}  # HashMap lưu signatures: {user_id: signature_array}
        self.prime = 2147483647  # Số nguyên tố lớn cho hash
        
        # Khởi tạo hash functions với random coefficients
        random.seed(42)  # Fix seed để reproducible
        for _ in range(num_hashes):
            a = random.randint(1, self.prime - 1)
            b = random.randint(0, self.prime - 1)
            self.hash_functions.append((a, b))
    
    def _hash_item(self, item, hash_func):
        """
        [Đã Deprecated - Do chậm] Hash một item (asin) với một hash function cụ thể
        """
        a, b = hash_func
        item_hash = int(hashlib.md5(item.encode()).hexdigest(), 16)
        return (a * item_hash + b) % self.prime
    
    def compute_signature(self, item_set):
        """
        Tính signature cho một item set
        Returns: array of integers (signature)
        """
        # TỐI ƯU HÓA: Tính toán integer hash (MD5) của items 1 lần duy nhất bên ngoài vòng lặp
        # Thay vì tính đi tính lại num_hashes lần (gây ra sự chậm trễ khổng lồ)
        item_hashes = [int(hashlib.md5(item.encode()).hexdigest()[:12], 16) for item in item_set]
        
        signature = []
        for a, b in self.hash_functions:
            min_hash = float('inf')
            for item_hash in item_hashes:
                hash_val = (a * item_hash + b) % self.prime
                if hash_val < min_hash:
                    min_hash = hash_val
            
            signature.append(min_hash if min_hash != float('inf') else 0)
        
        return signature
    
    def build_signatures(self, user_index):
        """
        Build signatures cho tất cả users
        Args:
            user_index: HashMap {user_id: User object}
        """
        total_users = len(user_index)
        print(f"Đang xây dựng MinHash signatures cho {total_users} users...")
        
        count = 0
        for user_id, user in user_index.items():
            item_set = user.get_item_set()
            if len(item_set) > 0:
                signature = self.compute_signature(item_set)
                self.signatures[user_id] = signature
                
            count += 1
            if count % 50000 == 0:
                print(f"  Tiến độ MinHash: Đã xử lý {count}/{total_users} users...")
        
        print(f"Đã xây dựng được {len(self.signatures)} signatures")
    
    def get_signature(self, user_id):
        """
        Lấy signature của một user
        Returns: signature array hoặc None nếu không tồn tại
        """
        return self.signatures.get(user_id)
    
    def estimate_jaccard(self, sig1, sig2):
        """
        Estimate Jaccard similarity từ 2 signatures
        """
        if len(sig1) != len(sig2):
            return 0.0
        
        matches = sum(1 for i in range(len(sig1)) if sig1[i] == sig2[i])
        return matches / len(sig1)