import pygame
import os
import sys
from data.map_loader import MapLoader
from models.player import Player 

class GameLoop:
    def __init__(self):
        pygame.init()
        
        # Cấu hình cơ bản
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Bullet Hell - 3-Tier Architecture")
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Xử lý đường dẫn linh hoạt (tự tìm lùi lại 1 thư mục để vào assets)
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.assets_path = os.path.join(self.base_dir, 'assets')
        self.map_path = os.path.join(self.assets_path, 'Map', 'level1.tmx')

        # Khởi tạo Map (Data Layer)
        self.map_loader = MapLoader(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.map_loader.load_map(self.map_path, scale_to_fit=True)

        # Khởi tạo Player (Models)
        self.player = Player(200, 220, self.assets_path)
        self.player.set_collision_map(self.map_loader.tmx_data)

        # Tính năng Zoom của đồng đội
        self.zoom = 1.0
        self.zoom_step = 0.1

    def handle_events(self):
        """Xử lý nhập liệu từ người chơi"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        # Xử lý phím tắt Zoom
        keys = pygame.key.get_pressed()
        old_zoom = self.zoom
        
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            self.zoom = min(self.zoom + self.zoom_step, 3.0)
        if keys[pygame.K_MINUS]:
            self.zoom = max(self.zoom - self.zoom_step, 0.3)
        
        if self.zoom != old_zoom:
            self.map_loader.set_zoom(self.zoom)

    def update(self):
        """Cập nhật trạng thái các thực thể"""
        self.player.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def draw(self):
        """Render hình ảnh ra màn hình"""
        self.screen.fill((0, 0, 0))
        self.map_loader.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Vòng lặp chính"""
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()