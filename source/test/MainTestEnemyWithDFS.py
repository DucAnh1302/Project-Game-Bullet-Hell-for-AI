import pygame
import os
import sys

# --- CẤU HÌNH ĐƯỜNG DẪN (Chỉ dùng cho file test) ---
# Lùi lại 1 cấp để Python nhận diện được các thư mục hệ thống
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

from data.map_loader import MapLoader
from bll.collision_manager import CollisionManager
from bll.pathfinding import DFSPathfinder
from models.enemy import PathfindingEnemy

def test_enemy_dfs_standalone():
    """Hàm test độc lập bộ não DFS của Enemy trong môi trường 'X-quang'"""
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Isolated Module: Enemy DFS Pathfinding (X-Ray Mode)")
    clock = pygame.time.Clock()

    assets_path = os.path.join(base_dir, 'assets')
    map_path = os.path.join(assets_path, 'Map', 'level1.tmx')

    print("Đang tải dữ liệu va chạm (Chỉ lấy Logic, không lấy Hình ảnh)...")
    
    # 1. TẦNG DATA: Chỉ dùng MapLoader để đọc mảng số, KHÔNG render hình ảnh
    map_loader = MapLoader(SCREEN_WIDTH, SCREEN_HEIGHT)
    map_loader.load_map(map_path, scale_to_fit=True)

    # 2. TẦNG BLL: Khởi tạo hệ thống va chạm và Thuật toán tìm đường
    scale_factor = map_loader.scale_x
    collision_manager = CollisionManager(map_loader.tmx_data, scale_factor)
    
    # Đồng bộ Scale: Tính kích thước ô lưới thực tế trên màn hình (Sửa lỗi 32px)
    scaled_tile_size = int(16 * scale_factor)
    pathfinder = DFSPathfinder(collision_manager, tile_size=scaled_tile_size)

    # 3. TẦNG MODELS: Khởi tạo Quái vật
    enemy_group = pygame.sprite.Group()
    
    def spawn_test_enemy():
        """Hàm sinh quái vật tại tọa độ cố định và tìm đường ngẫu nhiên"""
        spawn_x, spawn_y = 120, 120 # Gắn cứng điểm xuất phát cho dễ nhìn
        
        enemy = PathfindingEnemy(spawn_x, spawn_y, pathfinder, speed=4)
        enemy.set_collision_manager(collision_manager)
        enemy.set_random_target(SCREEN_WIDTH, SCREEN_HEIGHT, scaled_tile_size)
        enemy_group.add(enemy)

    # Sinh con quái vật đầu tiên
    spawn_test_enemy()

    is_running = True
    print("Test Enemy DFS đang chạy.")
    print("- Các khối Xanh Dương: Tường (Walls)")
    print("- Các khối Xanh Lá: Vật trang trí (Decorations)")
    print("- Nhấn phím SPACE để bắt quái vật tìm đường mới ngay lập tức!")
    
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            # Nhấn Space để test tạo đường mới
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    enemy_group.empty()
                    spawn_test_enemy()

        # Tính toán logic của quái vật
        enemy_group.update()
        
        # Nếu quái đi tới đích và biến mất, tự động sinh con mới
        if len(enemy_group) == 0:
            spawn_test_enemy()

        # --- KHÂU RENDER (GÓC NHÌN X-QUANG CỦA MÁY TÍNH) ---
        screen.fill((20, 20, 20)) # Nền xám đen cực ngầu
        
        # Vẽ các bức tường vô hình (Layer 'walls') thành các khối màu Xanh Dương
        for wall in collision_manager.walls:
            pygame.draw.rect(screen, (0, 70, 120), wall)
            
        # Vẽ các vật cản vô hình (Layer 'decorations') thành các khối màu Xanh Lá
        for deco in collision_manager.decorations:
            pygame.draw.rect(screen, (0, 100, 50), deco)

        # Vẽ đường đi của thuật toán DFS
        for enemy in enemy_group:
            if hasattr(enemy, 'path') and enemy.path and enemy.current_destination:
                points = [(enemy.x, enemy.y)] + enemy.path[enemy.target_node_index:]
                if len(points) > 1:
                    # Đường gấp khúc màu trắng
                    pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
                
                # Vẽ cờ đích đến bằng một chấm tròn màu Đỏ
                target_point = enemy.path[-1]
                pygame.draw.circle(screen, (255, 50, 50), target_point, 8)

        # In hình viên đạn (Quái vật) lên
        enemy_group.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_enemy_dfs_standalone()