import pygame
import sys
import os
import random
import math

# Khai báo đường dẫn để import các module từ thư mục source
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.dirname(current_dir)
sys.path.append(source_dir)

from data.map_loader import MapLoader
from models.player import Player
from models.enemy import PathfindingEnemy
from bll.collision_manager import CollisionManager
from bll.pathfinding import DFSPathfinder

class FullScreenAITest:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1000 # 800 map + 200 UI
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("AI Test: Full Screen DFS và Probability")
        self.clock = pygame.time.Clock()

        self.base_dir = source_dir
        self.assets_path = os.path.join(self.base_dir, 'assets')
        self.map_path = os.path.join(self.assets_path, 'Map', 'level1.tmx')

        self.map_loader = MapLoader(800, 600)
        self.map_loader.load_map(self.map_path, scale_to_fit=True)
        scale_factor = self.map_loader.scale_x
        
        self.collision_manager = CollisionManager(self.map_loader.tmx_data, scale_factor)
        self.scaled_tile_size = int(16 * scale_factor)
        self.pathfinder = DFSPathfinder(self.collision_manager, tile_size=self.scaled_tile_size)

        self.player = Player(400, 300, self.assets_path, scale=scale_factor)
        self.player.set_collision_manager(self.collision_manager)

        self.enemy_group = pygame.sprite.Group()
        self.font = pygame.font.SysFont('Times New Roman', 16, bold=True)
        self.small_font = pygame.font.SysFont('Times New Roman', 14)

    def spawn_enemy(self):
        if len(self.enemy_group) >= 4: return
        map_w, map_h = 800, 600
        tx = random.randint(1, (map_w // self.scaled_tile_size) - 2)
        ty = random.randint(1, (map_h // self.scaled_tile_size) - 2)
        
        spawn_x, spawn_y = tx * self.scaled_tile_size, ty * self.scaled_tile_size
        scale_factor = self.map_loader.scale_x
        speed, radius = int(2 * scale_factor), int(8 * scale_factor)

        # --- RANDOM MÀU ĐẠN KHÔNG TRÙNG LẶP ---
        all_colors = ['red', 'blue', 'green', 'purple']
        # Lấy danh sách các màu đã được sử dụng bởi đạn trên bản đồ
        used_colors = [e.color for e in self.enemy_group] 
        # Chỉ giữ lại các màu chưa được dùng
        available_colors = [c for c in all_colors if c not in used_colors]
        
        if not available_colors: 
            available_colors = all_colors # Fallback an toàn nếu lỡ sinh > 4 viên
            
        chosen_color = random.choice(available_colors)
        
        # --- KHỞI TẠO VỚI MÀU VÀ ASSETS_PATH ---
        enemy = PathfindingEnemy(
            spawn_x, spawn_y, 
            self.pathfinder, 
            self.assets_path, # Nhớ dùng self.assets_path (đã fix đường dẫn ở turn trước)
            speed, 
            radius, 
            color=chosen_color
        )
        enemy.set_collision_manager(self.collision_manager)
        enemy.set_random_target(map_w, map_h, self.scaled_tile_size)
        self.enemy_group.add(enemy)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.player.update(800, 600)
            self.enemy_group.update()
            
            while len(self.enemy_group) < 4:
                self.spawn_enemy()

            # Vẽ Bản đồ và Nhân vật
            self.screen.fill((20, 20, 20))
            self.map_loader.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)

            # Vẽ Đạn và Đường đi DFS
            for i, enemy in enumerate(self.enemy_group):
                self.screen.blit(enemy.image, enemy.rect)
                if len(enemy.path) > 1:
                    # Bảng từ điển ánh xạ màu tên sang mã màu RGB
                    color_map = {
                        'red': (255, 50, 50), 
                        'blue': (50, 150, 255), 
                        'green': (50, 255, 50), 
                        'purple': (180, 50, 255)
                    }
                    line_color = color_map.get(enemy.color, (255, 255, 255))
                    # Vẽ dây nối DFS cùng màu với đạn
                    pygame.draw.lines(self.screen, line_color, False, enemy.path, 2)
                
                # Vẽ số thứ tự lên đầu AI
                num_text = self.font.render(str(i+1), True, (255, 255, 255))
                self.screen.blit(num_text, (enemy.x - 5, enemy.y - 20))

            # Vẽ Bảng AI Panel bên phải (Từ pixel 800 đến 1000)
            pygame.draw.rect(self.screen, (40, 40, 50), (800, 0, 200, 600))
            title = self.font.render("BẢNG PHÂN TÍCH AI", True, (0, 255, 255))
            self.screen.blit(title, (820, 20))

            for i, enemy in enumerate(self.enemy_group):
                y_offset = 70 + (i * 120)
                dist = math.hypot(enemy.x - self.player.x, enemy.y - self.player.y)
                # Tính xác suất đe dọa (Càng gần càng cao)
                prob = max(0, min(100, int(100 - (dist / 10))))

                texts = [
                    f"AI #{i+1} Status:",
                    f"- Node đích: {len(enemy.path)}",
                    f"- Khoảng cách: {int(dist)}px",
                    f"- Tỉ lệ đe dọa: {prob}%"
                ]
                
                for j, text in enumerate(texts):
                    color = (255, 100, 100) if prob > 70 and j == 3 else (255, 255, 255)
                    surface = self.small_font.render(text, True, color)
                    self.screen.blit(surface, (810, y_offset + (j * 20)))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    test = FullScreenAITest()
    test.run()