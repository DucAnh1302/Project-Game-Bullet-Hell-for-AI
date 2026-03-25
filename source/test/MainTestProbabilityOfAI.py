import pygame
import sys
import os
import math
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.dirname(current_dir)
sys.path.append(source_dir)

from data.map_loader import MapLoader
from models.player import Player
from models.enemy import PathfindingEnemy
from bll.collision_manager import CollisionManager
from bll.pathfinding import DFSPathfinder

class AIPOVTest:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1000 # 800 game + 200 UI
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("AI POV: Góc nhìn của Đạn Ma Thuật")
        self.clock = pygame.time.Clock()

        self.base_dir = source_dir
        self.assets_path = os.path.join(self.base_dir, 'assets')
        self.map_path = os.path.join(self.assets_path, 'Map', 'level1.tmx')

        # Bản đồ phóng to như lúc chơi thật
        self.map_loader = MapLoader(800, 600)
        self.zoom = 2.0
        self.map_loader.load_map(self.map_path, scale_to_fit=False)
        self.map_loader.set_zoom(self.zoom)

        scale_factor = self.map_loader.scale_x * self.map_loader.zoom_level
        self.collision_manager = CollisionManager(self.map_loader.tmx_data, scale_factor)
        self.scaled_tile_size = int(16 * scale_factor)
        self.pathfinder = DFSPathfinder(self.collision_manager, tile_size=self.scaled_tile_size)

        self.player = Player(120, 120, self.assets_path, scale=scale_factor)
        self.player.set_collision_manager(self.collision_manager)

        self.font = pygame.font.SysFont('Times New Roman', 16, bold=True)
        self.small_font = pygame.font.SysFont('Times New Roman', 14)

        # Chỉ tạo 1 con AI làm nhân vật chính
        map_w = self.map_loader.tmx_data.width * self.scaled_tile_size
        map_h = self.map_loader.tmx_data.height * self.scaled_tile_size
        speed, radius = int(2 * scale_factor), int(8 * scale_factor)
        
        # --- BỐC THĂM MÀU CHO AI CHÍNH ---
        available_colors = ['red', 'blue', 'green', 'purple']
        chosen_color = random.choice(available_colors)

        # --- KHỞI TẠO VỚI MÀU VÀ ASSETS_PATH ---
        self.main_ai = PathfindingEnemy(
            400, 400, 
            self.pathfinder, 
            self.assets_path, # Dùng self.assets_path
            speed, 
            radius, 
            color=chosen_color
        )

        self.main_ai.set_collision_manager(self.collision_manager)
        self.main_ai.set_random_target(map_w, map_h, self.scaled_tile_size)

        self.camera_x = 0
        self.camera_y = 0

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Vẫn cho phép người chơi điều khiển Thỏ
            self.player.update(800, 600)
            self.main_ai.update()

            # Nếu AI tới đích, cho nó tìm đích mới
            if not self.main_ai.current_destination:
                map_w = self.map_loader.tmx_data.width * self.scaled_tile_size
                map_h = self.map_loader.tmx_data.height * self.scaled_tile_size
                self.main_ai.set_random_target(map_w, map_h, self.scaled_tile_size)

            # CAMERA ÉP THEO AI (Khóa mục tiêu vào đạn)
            self.camera_x = self.main_ai.rect.centerx - (800 // 2)
            self.camera_y = self.main_ai.rect.centery - (600 // 2)

            self.screen.fill((0, 0, 0))

            # Tạo khung vẽ 800x600 để không lẹm sang bảng UI
            game_surface = pygame.Surface((800, 600))
            game_surface.fill((0, 0, 0))

            # Vẽ mọi thứ lên game_surface, trừ đi camera_x, camera_y
            for tile in self.map_loader.sprite_group:
                game_surface.blit(tile.image, (tile.rect.x - self.camera_x, tile.rect.y - self.camera_y))

            # Vẽ Thỏ
            game_surface.blit(self.player.image, (self.player.rect.x - self.camera_x, self.player.rect.y - self.camera_y))
            
            # Vẽ đường DFS của AI cùng màu với viên đạn
            if len(self.main_ai.path) > 1:
                adjusted_path = [(px - self.camera_x, py - self.camera_y) for px, py in self.main_ai.path]
                
                color_map = {'red': (255, 50, 50), 'blue': (50, 150, 255), 'green': (50, 255, 50), 'purple': (180, 50, 255)}
                line_color = color_map.get(self.main_ai.color, (255, 255, 255))
                
                pygame.draw.lines(game_surface, line_color, False, adjusted_path, 3)

            # Vẽ AI chính
            game_surface.blit(self.main_ai.image, (self.main_ai.rect.x - self.camera_x, self.main_ai.rect.y - self.camera_y))

            # In game_surface lên màn hình chính
            self.screen.blit(game_surface, (0, 0))

            # Vẽ Bảng Phân Tích AI bên phải (Từ pixel 800 đến 1000)
            pygame.draw.rect(self.screen, (20, 20, 30), (800, 0, 200, 600))
            pygame.draw.line(self.screen, (0, 255, 0), (800, 0), (800, 600), 2)
            
            title = self.font.render("AI POV (GÓC NHÌN AI)", True, (50, 255, 50))
            self.screen.blit(title, (810, 20))

            # Lấy thông tin nội bộ của AI
            current_node = self.main_ai.target_node_index
            total_nodes = len(self.main_ai.path)
            progress = (current_node / total_nodes * 100) if total_nodes > 0 else 0

            texts = [
                f"Trạng thái: Đang truy vết",
                f"Tọa độ X: {int(self.main_ai.x)}",
                f"Tọa độ Y: {int(self.main_ai.y)}",
                f"Tổng số node đường: {total_nodes}",
                f"Node hiện tại: {current_node}",
                f"Tiến độ hoàn thành: {int(progress)}%",
                f"Backtracking: Hoạt động"
            ]

            for j, text in enumerate(texts):
                surface = self.small_font.render(text, True, (200, 255, 200))
                self.screen.blit(surface, (810, 80 + (j * 30)))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    test = AIPOVTest()
    test.run()