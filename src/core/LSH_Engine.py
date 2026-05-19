class LSH_Engine:
    """
    LSH (Locality Sensitive Hashing) Engine
    Dùng để tìm similar users nhanh bằng cách nhóm users có signatures tương tự
    """
    def __init__(self, num_bands=20, rows_per_band=5, minhash=None):
        self.num_bands = num_bands  # Số bands
        self.rows_per_band = rows_per_band  # Số rows mỗi band
        self.buckets = {}  # HashMap lưu buckets: {(band_id, hash): [user_ids]}
        self.minhash = minhash  # MinHash object
    
    def _hash_band(self, band_signature):
        """
        Hash một band signature thành bucket key
        """
        return hash(tuple(band_signature))
    
    def build_index(self, user_index):
        """
        Build LSH index cho tất cả users
        Args:
            user_index: HashMap {user_id: User object}
        """
        print(f"Đang xây dựng LSH index với {self.num_bands} bands, {self.rows_per_band} rows mỗi band...")
        
        for user_id, user in user_index.items():
            signature = self.minhash.get_signature(user_id)
            if signature is None:
                continue
            
            # Chia signature thành bands
            for band_id in range(self.num_bands):
                start = band_id * self.rows_per_band
                end = start + self.rows_per_band
                
                if end > len(signature):
                    break
                
                band_signature = signature[start:end]
                bucket_key = (band_id, self._hash_band(band_signature))
                
                # Thêm user vào bucket
                if bucket_key not in self.buckets:
                    self.buckets[bucket_key] = set()
                self.buckets[bucket_key].add(user_id)
        
        print(f"Đã xây dựng được {len(self.buckets)} buckets")
    
    def get_candidates(self, user_id):
        """
        Lấy tập candidate users (similar users) cho một user
        Returns: set of user_ids
        """
        candidates = set()
        signature = self.minhash.get_signature(user_id)
        
        if signature is None:
            return candidates
        
        # Tìm tất cả users trong cùng buckets
        for band_id in range(self.num_bands):
            start = band_id * self.rows_per_band
            end = start + self.rows_per_band
            
            if end > len(signature):
                break
            
            band_signature = signature[start:end]
            bucket_key = (band_id, self._hash_band(band_signature))
            
            if bucket_key in self.buckets:
                candidates.update(self.buckets[bucket_key])
        
        # Loại bỏ chính user đó
        candidates.discard(user_id)
        
        return candidates