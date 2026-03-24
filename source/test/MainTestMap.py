import pygame
import os
import sys

# --- CẤU HÌNH ĐƯỜNG DẪN (Chỉ dùng cho file test) ---
# Vì file này nằm trong source/test/, ta cần lùi lại 1 cấp để Python nhận diện được thư mục 'data'
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

# [Trích từ file: source/presentation/game_loop.py]
from data.map_loader import MapLoader 

def test_map_standalone():
    """Hàm chạy độc lập để test khả năng load và zoom map của Tầng Data"""
    
    # [Trích từ file: source/presentation/game_loop.py]
    # Khởi tạo môi trường Pygame cơ bản
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Isolated Module: Map Loader")
    clock = pygame.time.Clock()

    # [Trích từ file: source/presentation/game_loop.py]
    # Thiết lập đường dẫn tới map
    map_path = os.path.join(base_dir, 'assets', 'Map', 'level1.tmx')

    # --- KHU VỰC THỂ HIỆN CODE GỐC ---
    # [Trích từ file: source/data/map_loader.py và game_loop.py]
    print(f"Đang thử nghiệm tải map từ: {map_path}")
    map_loader = MapLoader(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Cố tình sử dụng nguyên xi hàm và tham số gốc
    map_loader.load_map(map_path, scale_to_fit=True) 

    # [Trích từ file: source/presentation/game_loop.py]
    # Khởi tạo các biến dùng cho tính năng Zoom
    zoom = 1.0
    zoom_step = 0.1

    is_running = True
    print("Test Map đang chạy. Hãy thử bấm phím '+' hoặc '-' để test tính năng Zoom.")
    
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # [Trích từ file: source/presentation/game_loop.py]
        # Xử lý Logic Zoom Map y chang bản gốc
        keys = pygame.key.get_pressed()
        old_zoom = zoom
        
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            zoom = min(zoom + zoom_step, 3.0)
        if keys[pygame.K_MINUS]:
            zoom = max(zoom - zoom_step, 0.3)
        
        if zoom != old_zoom:
            map_loader.set_zoom(zoom)

        # [Trích từ file: source/presentation/game_loop.py]
        # Khâu Render
        screen.fill((0, 0, 0))
        map_loader.draw(screen) # Gọi trực tiếp hàm draw của MapLoader
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_map_standalone()