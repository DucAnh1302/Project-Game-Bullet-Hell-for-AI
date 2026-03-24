import pygame
import os
import sys
import random
# Import các Layer đúng chuẩn Kiến trúc 3 Lớp (3-Tier)
from data.map_loader import MapLoader # Tầng data: load file TMX á
from models.player import Player # tầng bll: Logic của game mình á
from models.enemy import PathfindingEnemy, BulletEnemySpawner
from bll.collision_manager import CollisionManager # tầng models: Nhân vật của mình á
from bll.pathfinding import DFSPathfinder
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
        self.pathfinder = DFSPathfinder(self.collision_manager, tile_size=32) # tile_size theo chuẩn map là 32x32 pixel 
        
        # Tầng models: Khởi tạo Player và bơm BLL vào cho nó
        self.player = Player(120, 120, self.assets_path) # Spawn ở tọa độ (120, 120) cho an toàn
        self.player.set_collision_manager(self.collision_manager)

        # Tầng models: Khởi tạo Enemy và bơm BLL vào cho nó
        self.enemy_group = pygame.sprite.Group() # Tạo nhóm để quản lý nhiều Enemy sau này
        self.spawn_random_enemy() # Spawn Enemy đầu tiên

        # Khởi tạo Bullet Spawner
        #self.bullet_spawner = BulletEnemySpawner()
        #self.bullet_spawn_timer = 0
        #self.bullet_spawn_interval = 300  # 5 giây ở 60 FPS

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

    def spawn_random_enemy(self):
        """Spawn enemy ở vị trí hợp lệ TRONG KHUNG MÀN HÌNH"""
        tile_size = 32
        spawn_x, spawn_y = None, None
        
        # Giới hạn vùng tìm kiếm bằng đúng kích thước cửa sổ game (800x600)
        # Cộng trừ thêm padding để Enemy không dính mép màn hình
        max_x = (self.SCREEN_WIDTH // tile_size) - 2
        max_y = (self.SCREEN_HEIGHT // tile_size) - 2
        
        for _ in range(500):
            # Chọn ô grid nằm trong màn hình hiển thị (từ ô số 1 để tránh sát viền)
            #tx = random.randint(1, max_x)
            #ty = random.randint(1, max_y)
            #Đang lấy vị trí cố định để test, sau này đổi lại random nhé
            tx=2
            ty=2
            # Kiểm tra xem ô đó có hợp lệ (không dính tường) không
            if self.pathfinder._is_valid((tx, ty)):
                spawn_x = tx * tile_size
                spawn_y = ty * tile_size
                break
        
        # Nếu không tìm được chỗ nào thì fallback về vị trí an toàn giữa màn hình
        if spawn_x is None:
            spawn_x = 300 
            spawn_y = 300 
        
        # Khởi tạo Enemy mới
        new_enemy = PathfindingEnemy(spawn_x, spawn_y, self.pathfinder, speed=2)
        new_enemy.set_collision_manager(self.collision_manager)
        
        # Truyền luôn SCREEN_WIDTH và SCREEN_HEIGHT để Enemy tìm đích đến trong màn hình
        new_enemy.set_random_target( self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 32)
        
        self.enemy_group.add(new_enemy)

    def update(self):
        """Gọi hàm update của tất cả các thực thể (Thỏ, Quái vật, Đạn...)"""
        self.player.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        # Cập nhật Enemy di chuyển theo đường đã tìm
        self.enemy_group.update()
        if len(self.enemy_group) == 0:
            self.spawn_random_enemy()

        # Quản lý thời gian spawn đạn
        #self.bullet_spawn_timer += 1
        spawn_positions = None # Mặc định là None (không tạo đạn)
        
        # Nếu đến lúc bắn đạn và có Enemy trên bản đồ
        """
        if self.bullet_spawn_timer >= self.bullet_spawn_interval:
            self.bullet_spawn_timer = 0
            if len(self.enemy_group) > 0:
                shooter = next(iter(self.enemy_group)) # Lấy Enemy đang sống làm tâm bắn
                directions = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1)]
                
                # Gom danh sách các hướng bắn vào mảng
                spawn_positions = []
                for dir_x, dir_y in directions:
                    spawn_positions.append((shooter.x, shooter.y, dir_x, dir_y))
        """
        # Gọi hàm update của Spawner (truyền mảng vị trí vào để nó tự sinh đạn nếu có)
        #self.bullet_spawner.update(spawn_positions)

        # CẤP QUYỀN VA CHẠM CHO ĐẠN TRONG MÊ CUNG
        # Để đạn nảy đập tường, từng viên đạn phải được nhận CollisionManager
        #for bullet in self.bullet_spawner.get_enemies():
        #    if bullet.collision_manager is None:
        #        bullet.set_collision_manager(self.collision_manager)

        # Xóa đạn khi bay ra ngoài màn hình (tránh nặng máy)
        # Giả sử kích thước thật của map to hơn màn hình, bạn có thể truyền map_w, map_h vào đây
        #for bullet in self.enemy_group:
        #    if bullet.is_out_of_bounds(self.SCREEN_WIDTH, self.SCREEN_HEIGHT):
        #        bullet.kill()

        # Kiểm tra đạn chạm người chơi
        for bullet in self.enemy_group:
            if bullet.check_collision_with_player(self.player.rect):
                if hasattr(self.player, 'take_damage'):
                    self.player.take_damage(bullet.damage)
                bullet.kill() # Biến mất khi trúng người

    def draw(self):
        """Hàm render (vẽ) mọi thứ ra màn hình theo thứ tự Lớp (Layer)"""
        self.screen.fill((0, 0, 0)) # B1: quét màn hình đen ( xóa frame cũ)    
        self.map_loader.draw(self.screen) # B2: vẽ map (làm nền á)
        self.player.draw(self.screen) # B3 vẽ nhân vật lên map
        #Vẽ đường đi của quái
        for enemy in self.enemy_group:
            # Kiểm tra xem đây có phải là quái vật có thuật toán tìm đường không
            if hasattr(enemy, 'path') and enemy.path and enemy.current_destination:
                
                # Tạo danh sách các điểm: Bắt đầu từ vị trí quái vật, nối với các điểm CHƯA ĐI QUA trong path
                points = [(enemy.x, enemy.y)] + enemy.path[enemy.target_node_index:]
                
                if len(points) > 1:
                    # Vẽ đường kẻ gấp khúc (screen, màu đỏ, false = không nối kín, list tọa độ, độ dày line)
                    pygame.draw.lines(self.screen, (255, 255, 255), False, points, 2)
                
                # (Tùy chọn) Vẽ một dấu chấm tròn màu Xanh Lá Cây để đánh dấu đích đến cuối cùng
                target_point = enemy.path[-1]
                pygame.draw.circle(self.screen, (50, 255, 50), target_point, 6)

        self.enemy_group.draw(self.screen) # B4 vẽ Enemy
        #for bullet in self.bullet_spawner.get_enemies():
        #    self.screen.blit(bullet.image, bullet.rect)
        self._draw_health()
        pygame.display.flip() # đẩy lên màn hình hoi

    def _draw_health(self):
        font = pygame.font.Font(None, 36)
        health_text = f"HP: {self.player.health if hasattr(self.player, 'health') else 0}/100"
        text_surface = font.render(health_text, True, (255, 0, 0))
        self.screen.blit(text_surface, (10, 10))
    # vòng lặp vĩnh cữu cho game á
    def run(self):
        while self.is_running:
            self.handle_events() # xử lý nhập WASD hay mũi tên nè
            self.update() # Tính toán logic
            self.draw() # cập nhật hình ảnh
            self.clock.tick(60) # 60 pfs nè
            
        pygame.quit()
        sys.exit()