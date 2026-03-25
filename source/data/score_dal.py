# source/data/score_dal.py
import os

class ScoreDAL:
    """
    Tầng Data Access Layer (DAL): Chuyên trách tương tác với hệ thống lưu trữ (File/Database).
    Chỉ làm nhiệm vụ Đọc và Ghi dữ liệu, không chứa logic game.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def load_best_time(self):
        """Đọc thời gian kỷ lục từ file. Trả về dương vô cùng nếu chưa có kỷ lục."""
        if not os.path.exists(self.file_path):
            return float('inf') # Chưa có ai chơi thì kỷ lục là vô cực
        
        try:
            with open(self.file_path, 'r') as file:
                return float(file.read().strip())
        except Exception as e:
            print(f"Lỗi đọc file kỷ lục: {e}")
            return float('inf')

    def save_best_time(self, time_in_seconds):
        """Ghi đè kỷ lục mới xuống file txt."""
        try:
            with open(self.file_path, 'w') as file:
                file.write(f"{time_in_seconds:.2f}")
        except Exception as e:
            print(f"Lỗi ghi file kỷ lục: {e}")