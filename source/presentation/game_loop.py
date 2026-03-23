import pygame
import os
import sys

# Import các Layer đúng chuẩn Kiến trúc 3 Lớp (3-Tier)
from data.map_loader import MapLoader # Tầng data: load file TMX á
from models.player import Player # tầng bll: Logic của game mình á
from bll.collision_manager import CollisionManager # tầng models: Nhân vật của mình á

class GameLoop:
    def __init__(self):
        """
        Tầng Presentation: Nơi khởi tạo môi trường Pygame, vòng lặp game, 
        và là nơi các Layer (Data, BLL, Models) liên kết với nhau.
        """
        pygame.init()
        
        # thiết lập cửa sổ nè
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Bullet Hell - 3-Tier Architecture")
        self.clock = pygame.time.Clock()
        self.is_running = True

        # để máy ai cũng chạy được nên lưu keieur đường dẫn này cho linh hoạt á
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.assets_path = os.path.join(self.base_dir, 'assets')
        self.map_path = os.path.join(self.assets_path, 'Map', 'level1.tmx')

        # tầng data nè, tải dữ liệu cho Map và tự động phóng to
        self.map_loader = MapLoader(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.map_loader.load_map(self.map_path, scale_to_fit=True)

        # LIÊN KẾT BLL VÀ MODELS
        # Khởi tạo BLL Quản lý va chạm trước
        scale_factor = self.map_loader.scale_x # biết được map phóng to nhiều lần để scale_x lên á
        self.collision_manager = CollisionManager(self.map_loader.tmx_data, scale_factor)
        
        # Tầng models: Khởi tạo Player và bơm BLL vào cho nó
        self.player = Player(120, 120, self.assets_path) # Spawn ở tọa độ (120, 120) cho an toàn
        self.player.set_collision_manager(self.collision_manager)

        # zoom camera chắc em biết rồi á
        self.zoom = 1.0
        self.zoom_step = 0.1

    def handle_events(self):
        """Xử lý các sự kiện click, gõ phím của người dùng"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        keys = pygame.key.get_pressed()
        old_zoom = self.zoom
        
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            self.zoom = min(self.zoom + self.zoom_step, 3.0)
        if keys[pygame.K_MINUS]:
            self.zoom = max(self.zoom - self.zoom_step, 0.3)
        
        if self.zoom != old_zoom:
            self.map_loader.set_zoom(self.zoom)

    def update(self):
        """Gọi hàm update của tất cả các thực thể (Thỏ, Quái vật, Đạn...)"""
        # tạm thời thì chưa có gì thôi
        self.player.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def draw(self):
        """Hàm render (vẽ) mọi thứ ra màn hình theo thứ tự Lớp (Layer)"""
        self.screen.fill((0, 0, 0)) # B1: quét màn hình đen ( xóa frame cũ)    
        self.map_loader.draw(self.screen) # B2: vẽ map (làm nền á)
        self.player.draw(self.screen) # B3 vẽ nhân vật lên map
        pygame.display.flip() # đẩy lên màn hình hoi

    # vòng lặp vĩnh cữu cho game á
    def run(self):
        while self.is_running:
            self.handle_events() # xử lý nhập WASD hay mũi tên nè
            self.update() # Tính toán logic
            self.draw() # cập nhật hình ảnh
            self.clock.tick(60) # 60 pfs nè
            
        pygame.quit()
        sys.exit()