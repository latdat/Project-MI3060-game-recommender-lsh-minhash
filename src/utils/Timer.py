import time

class Timer:
    """
    Class đo thời gian thực thi (cho QA/QC)
    """
    def __init__(self, label="Timer"):
        self.label = label
        self.start_time = None
        self.elapsed_ms = 0
    
    def start(self):
        """Bắt đầu đếm thời gian"""
        self.start_time = time.time()
        print(f"[{self.label}] Đã bắt đầu...")
    
    def stop(self):
        """Dừng đếm và tính elapsed time"""
        if self.start_time is None:
            print(f"[{self.label}] Cảnh báo: Timer chưa được bắt đầu!")
            return 0
        
        end_time = time.time()
        self.elapsed_ms = (end_time - self.start_time) * 1000  # Convert to milliseconds
        print(f"[{self.label}] Đã hoàn thành trong {self.elapsed_ms:.2f} ms")
        return self.elapsed_ms
    
    def get_elapsed_ms(self):
        """Lấy thời gian đã trôi qua (milliseconds)"""
        return self.elapsed_ms