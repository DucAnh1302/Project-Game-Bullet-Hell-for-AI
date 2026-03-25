import pygame
import os
import sys
import random

# --- CẤU HÌNH ĐƯỜNG DẪN (Chỉ dùng cho file test) ---
# Lùi lại 1 cấp để Python nhận diện được các thư mục hệ thống
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

from data.map_loader import MapLoader
from bll.collision_manager import CollisionManager
from bll.pathfinding import DFSPathfinder
from models.enemy import PathfindingEnemy

def test_enemy_dfs_standalone():
    """Hàm test độc lập bộ não DFS của Enemy trong môi trường 'X-quang' có Grid và Thông số"""
    pygame.init()
    # Mở rộng màn hình lên 1000 để chứa UI bên phải
    SCREEN_WIDTH = 1000 
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Isolated Module: Enemy DFS Pathfinding (X-Ray Mode)")
    clock = pygame.time.Clock()

    assets_path = os.path.join(base_dir, 'assets')
    map_path = os.path.join(assets_path, 'Map', 'level1.tmx')

    # Font chữ cho UI và Grid
    font_title = pygame.font.SysFont('Times New Roman', 16, bold=True)
    font_ui = pygame.font.SysFont('Times New Roman', 14)
    font_grid = pygame.font.SysFont('Times New Roman', 10)

    print("Đang tải dữ liệu va chạm (Chỉ lấy Logic, không lấy Hình ảnh)...")
    
    # 1. TẦNG DATA: Ép map vào khu vực 800x600
    map_loader = MapLoader(800, 600)
    map_loader.load_map(map_path, scale_to_fit=True)

    # 2. TẦNG BLL: Khởi tạo hệ thống va chạm và Thuật toán tìm đường
    scale_factor = map_loader.scale_x
    collision_manager = CollisionManager(map_loader.tmx_data, scale_factor)
    
    # Đồng bộ Scale: Tính kích thước ô lưới thực tế trên màn hình
    scaled_tile_size = int(16 * scale_factor)
    pathfinder = DFSPathfinder(collision_manager, tile_size=scaled_tile_size)

    # 3. TẦNG MODELS: Khởi tạo Quái vật
    enemy_group = pygame.sprite.Group()
    
    def spawn_test_enemy():
        """Hàm sinh quái vật tại tọa độ cố định và tìm đường ngẫu nhiên"""
        spawn_x, spawn_y = 120, 120 # Gắn cứng điểm xuất phát cho dễ nhìn
        
        # Lọc màu không trùng
        all_colors = ['red', 'blue', 'green', 'purple']
        used_colors = [e.color for e in enemy_group]
        available_colors = [c for c in all_colors if c not in used_colors]
        if not available_colors: available_colors = all_colors
        chosen_color = random.choice(available_colors)
        
        enemy = PathfindingEnemy(
            spawn_x, spawn_y, 
            pathfinder, 
            assets_path, 
            speed=4, 
            color=chosen_color
        )
        enemy.set_collision_manager(collision_manager)
        # Ép khung target giới hạn trong 800x600 (tránh đi lọt vào bảng UI)
        enemy.set_random_target(800, 600, scaled_tile_size)
        enemy_group.add(enemy)

    # Sinh con quái vật đầu tiên
    spawn_test_enemy()

    is_running = True
    print("Test Enemy DFS đang chạy.")
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
        
        # VẼ LƯỚI GRID VÀ ĐÁNH SỐ
        for x in range(0, 800, scaled_tile_size):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, 600))
            if x < 800:
                grid_num = font_grid.render(str(x // scaled_tile_size), True, (100, 100, 100))
                screen.blit(grid_num, (x + 2, 2))

        for y in range(0, 600, scaled_tile_size):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (800, y))
            if y > 0 and y < 600:
                grid_num = font_grid.render(str(y // scaled_tile_size), True, (100, 100, 100))
                screen.blit(grid_num, (2, y + 2))

        # Vẽ các bức tường vô hình (Layer 'walls') thành các khối màu Xanh Dương đậm
        for wall in collision_manager.walls:
            pygame.draw.rect(screen, (0, 70, 120), wall)
            
        # Vẽ các vật cản vô hình (Layer 'decorations') thành các khối màu Xanh Lá đậm
        for deco in collision_manager.decorations:
            pygame.draw.rect(screen, (0, 100, 50), deco)

        # Vẽ đường đi của thuật toán DFS
        for enemy in enemy_group:
            if hasattr(enemy, 'path') and enemy.path and enemy.current_destination:
                points = [(enemy.x, enemy.y)] + enemy.path[enemy.target_node_index:]
                
                # Ánh xạ màu dây DFS theo màu đạn
                color_map = {'red': (255, 50, 50), 'blue': (50, 150, 255), 'green': (50, 255, 50), 'purple': (180, 50, 255)}
                line_color = color_map.get(enemy.color, (255, 255, 255))

                if len(points) > 1:
                    pygame.draw.lines(screen, line_color, False, points, 2)
                
                # Vẽ cờ đích đến bằng một chấm tròn cùng màu
                target_point = enemy.path[-1]
                pygame.draw.circle(screen, line_color, target_point, 8)

        # In hình viên đạn (Quái vật) lên
        enemy_group.draw(screen)

        # --- VẼ BẢNG THÔNG SỐ AI BÊN PHẢI ---
        pygame.draw.rect(screen, (30, 30, 40), (800, 0, 200, 600))
        pygame.draw.line(screen, (0, 255, 255), (800, 0), (800, 600), 2)
        
        title = font_title.render("THÔNG SỐ AI (X-RAY)", True, (0, 255, 255))
        screen.blit(title, (810, 20))

        for i, enemy in enumerate(enemy_group):
            y_offset = 60 + (i * 100)
            
            # Tính toán vị trí grid hiện tại của quái
            grid_x = int(enemy.x // scaled_tile_size)
            grid_y = int(enemy.y // scaled_tile_size)

            texts = [
                f"AI {enemy.color.upper()}:",
                f"Tọa độ lưới: ({grid_x}, {grid_y})",
                f"Node đích: {len(enemy.path)}",
                f"Tiến trình: {enemy.target_node_index}/{len(enemy.path)}"
            ]
            
            for j, text in enumerate(texts):
                color = (255, 255, 255)
                if j == 0: # Đổi màu dòng tiêu đề AI theo màu đạn
                    color = color_map.get(enemy.color, (255, 255, 255))
                surface = font_ui.render(text, True, color)
                screen.blit(surface, (810, y_offset + (j * 20)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_enemy_dfs_standalone()