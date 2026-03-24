import pygame
import os
import sys

# --- CẤU HÌNH ĐƯỜNG DẪN (Chỉ dùng cho file test) ---
# Lùi lại 1 cấp để Python nhận diện được thư mục 'models'
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

# [Trích từ file: source/presentation/game_loop.py]
from models.player import Player

def test_player_standalone():
    """Hàm chạy độc lập để test khả năng di chuyển, animation và giới hạn màn hình của Tầng Models"""
    
    # [Trích từ file: source/presentation/game_loop.py]
    # Khởi tạo môi trường Pygame cơ bản
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Isolated Module: Player Controls và Animation")
    clock = pygame.time.Clock()

    # --- KHU VỰC THỂ HIỆN CODE GỐC ---
    # Thiết lập đường dẫn tới assets để load ảnh nhân vật
    assets_path = os.path.join(base_dir, 'assets')
    
    # [Trích từ file: source/presentation/game_loop.py]
    # Khởi tạo Player ở giữa màn hình (400, 300)
    print("Đang khởi tạo Player độc lập (Không có Map, Không có BLL va chạm)...")
    player = Player(400, 300, assets_path)
    
    # LƯU Ý: Chú ý rằng ở đây ta CỐ TÌNH KHÔNG gọi hàm player.set_collision_manager()
    # Để test xem class Player có tự sinh tồn được khi thiếu các module khác không.

    is_running = True
    print("Test Player đang chạy. Hãy dùng WASD hoặc Mũi tên để di chuyển thử.")
    
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # [Trích từ file: source/presentation/game_loop.py]
        # Gọi hàm cập nhật logic của Player (Nhận phím và tính toán tọa độ)
        player.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # [Trích từ file: source/presentation/game_loop.py]
        # Khâu Render
        # Dùng màu xám đậm (50, 50, 50) để làm nền thay vì map, giúp dễ nhìn animation của nhân vật hơn
        screen.fill((50, 50, 50)) 
        
        # Gọi hàm vẽ của riêng Player
        player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_player_standalone()