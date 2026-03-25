import pygame
import os
import sys
import random
import asyncio
# Import các Layer đúng chuẩn Kiến trúc 3 Lớp (3-Tier)
from data.map_loader import MapLoader # Tầng data: load file TMX á
from data.score_dal import ScoreDAL
from presentation.ui_manager import UIManager
from models.player import Player # tầng bll: Logic của game mình á
from models.enemy import PathfindingEnemy
from models.exit_door import ExitDoor
from models.magic_eye import MagicEye
from bll.collision_manager import CollisionManager # tầng models: Nhân vật của mình á
from bll.pathfinding import AStarPathfinder, DFSPathfinder

class GameLoop:
    def __init__(self):
        """
        Tầng Presentation: Nơi khởi tạo môi trường Pygame, vòng lặp game, 
        và là nơi các Layer (Data, BLL, Models) liên kết với nhau.
        """
        pygame.init()
        
        # Thiết lập cửa sổ
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Bullet Hell - 3-Tier Architecture")
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Đường dẫn linh hoạt cho mọi máy
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.assets_path = os.path.join(self.base_dir, 'assets')

        # Danh sách các file map trong thư mục assets/Map/
        self.level_files = ['level1.tmx', 'level2.tmx', 'level3.tmx']
        self.current_level_index = 0
        self.map_path = os.path.join(self.assets_path, 'Map', self.level_files[self.current_level_index])

        # TẦNG DATA: Tải dữ liệu Map và phóng to
        self.map_loader = MapLoader(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.zoom = 2.0 
        self.map_loader.load_map(self.map_path, scale_to_fit=False)
        self.map_loader.set_zoom(self.zoom)

        # LIÊN KẾT BLL VÀ MODELS
        scale_factor = self.map_loader.scale_x * self.map_loader.zoom_level
        self.collision_manager = CollisionManager(self.map_loader.tmx_data, scale_factor)
        self.scaled_tile_size = int(16 * scale_factor)
        self.pathfinder = DFSPathfinder(self.collision_manager, tile_size=self.scaled_tile_size) 
        self.astar_pathfinder = AStarPathfinder(self.collision_manager, self.scaled_tile_size)
        # KHỞI TẠO CÁC GROUP VÀ SURFACE CỐ ĐỊNH CHO RENDER
        self.enemy_group = pygame.sprite.Group()
        self.map_width = self.map_loader.tmx_data.width * self.scaled_tile_size
        self.map_height = self.map_loader.tmx_data.height * self.scaled_tile_size
        self.virtual_surface = pygame.Surface((self.map_width, self.map_height))

        # KHỞI TẠO DAL LƯU KỶ LỤC TỐC ĐỘ (SPEEDRUN)
        score_file_path = os.path.join(self.base_dir, 'highscore.txt')
        self.score_dal = ScoreDAL(score_file_path)

        # KHỞI TẠO QUẢN LÝ GIAO DIỆN
        self.ui_manager = UIManager(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.assets_path)
            
        # GỌI HÀM RESET ĐỂ SETUP NHÂN VẬT, VẬT PHẨM VÀ ĐỒNG HỒ
        self.reset_game()

        # SỬA TRẠNG THÁI MẶC ĐỊNH THÀNH START MENU để chặn game ở menu chính
        self.state = "START" # Các trạng thái: "PLAYING", "GAME_OVER", "WIN"

    def load_current_level(self):
        """Đọc file TMX hiện tại, setup môi trường và làm mới vòng chơi"""
        self.map_path = os.path.join(self.assets_path, 'Map', self.level_files[self.current_level_index])
        
        # TẦNG DATA: Tải dữ liệu Map và phóng to
        self.map_loader = MapLoader(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.map_loader.load_map(self.map_path, scale_to_fit=False)
        self.map_loader.set_zoom(self.zoom)

        # LIÊN KẾT BLL VÀ MODELS
        scale_factor = self.map_loader.scale_x * self.map_loader.zoom_level
        self.collision_manager = CollisionManager(self.map_loader.tmx_data, scale_factor)
        self.scaled_tile_size = int(16 * scale_factor)
        
        # Cập nhật lại bộ tìm đường cho map mới
        self.pathfinder = DFSPathfinder(self.collision_manager, tile_size=self.scaled_tile_size) 
        self.astar_pathfinder = AStarPathfinder(self.collision_manager, self.scaled_tile_size)

        # KHỞI TẠO LẠI SURFACE CỐ ĐỊNH CHO RENDER
        self.map_width = self.map_loader.tmx_data.width * self.scaled_tile_size
        self.map_height = self.map_loader.tmx_data.height * self.scaled_tile_size
        self.virtual_surface = pygame.Surface((self.map_width, self.map_height))

        # Reset các biến trong game (Tạo thỏ, xóa quái, reset giờ...)
        self.reset_game()


    def reset_game(self):
        """Khôi phục lại toàn bộ trạng thái ban đầu để Chơi lại (Restart)"""
        scale_factor = self.map_loader.scale_x * self.map_loader.zoom_level
        
        # Reset Nhân vật (Máu đầy, về tọa độ gốc an toàn)
        self.player = Player(120, 120, self.assets_path, scale=scale_factor)
        self.player.set_collision_manager(self.collision_manager)
        
        # Xóa sạch đạn cũ và Camera
        self.enemy_group.empty()
        self.camera_x = 0
        self.camera_y = 0
        
        # Sinh lại Cửa và Vật phẩm ngẫu nhiên chỗ mới
        self.spawn_exit_door()
        self.spawn_magic_eye()
        self.is_eye_active = False
        
        # Reset Đồng hồ và load lại kỷ lục
        self.best_time = self.score_dal.load_best_time()
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        
        # Trạng thái chơi bình thường
        self.state = "PLAYING"

    def handle_events(self):
        """Xử lý các sự kiện click, gõ phím của người dùng"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # Xử lý CLICK CHUỘT TRÁI vào nút Play/Retry
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state in ["START", "GAME_OVER", "WIN"]:
                    # Nhờ UI Manager check xem chuột có click trúng nút không
                    if self.ui_manager.btn_rect.collidepoint(event.pos):
                        self.reset_game()

            # Xử lý phím khi đang ở màn hình GAME OVER hoặc WIN
            if event.type == pygame.KEYDOWN:
                if self.state in ["GAME_OVER", "WIN"]:
                    if event.key == pygame.K_r: # Bấm R để chơi lại
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE: # Bấm ESC để thoát
                        self.is_running = False
                    elif event.key == pygame.K_RETURN and self.state == "WIN":
                        # Nếu vẫn còn map trong danh sách
                        if self.current_level_index < len(self.level_files) - 1:
                            self.current_level_index += 1  # Tăng lên map tiếp theo
                            self.load_current_level()      # Tải map mới
                            self.state = "PLAYING"         # Mở khóa chơi tiếp
                        else:
                            # Đã chơi qua tất cả các map!
                            self.state = "GAME_CLEARED"    # Cần thêm trạng thái phá đảo vào UI

        # Chỉ cho phép điều khiển Camera (Zoom) và Thỏ khi đang PLAYING
        if self.state == "PLAYING":
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
        # Tile_size = 32
        # --- FIX BUG: Sử dụng scaled_tile_size thay vì số 32 cố định ---
        tile_size = self.scaled_tile_size
        spawn_x, spawn_y = None, None
        
        # Lấy kích thước thật của toàn bộ Map (không bị giới hạn bởi 800x600 nữa)
        map_width = self.map_loader.tmx_data.width * tile_size
        map_height = self.map_loader.tmx_data.height * tile_size

        # Giới hạn vùng tìm kiếm bằng đúng kích thước cửa sổ game (800x600)
        # Cộng trừ thêm padding để Enemy không dính mép màn hình
        max_x = (map_width // tile_size) - 2
        max_y = (map_height // tile_size) - 2

        for _ in range(500):
            # Chọn ô grid nằm trong màn hình hiển thị (từ ô số 1 để tránh sát viền)
            tx = random.randint(1, max_x)
            ty = random.randint(1, max_y)
            # Kiểm tra xem ô đó có hợp lệ (không dính tường) không
            if self.pathfinder._is_valid((tx, ty)):
                spawn_x = tx * tile_size
                spawn_y = ty * tile_size
                break
        
        # Nếu không tìm được chỗ nào thì fallback về vị trí an toàn giữa màn hình
        if spawn_x is None:
            spawn_x = 300 
            spawn_y = 300 
        
        # Tính toán độ to và tốc độ của viên đạn theo Map
        scale_factor = self.map_loader.scale_x * self.map_loader.zoom_level
        scaled_speed = int(2 * scale_factor)
        scaled_radius = int(8 * scale_factor)
        
        # --- RANDOM MÀU ĐẠN KHÔNG TRÙNG LẶP ---
        all_colors = ['red', 'blue', 'green', 'purple']
        # Lấy danh sách các màu đã được sử dụng bởi đạn trên bản đồ
        used_colors = [e.color for e in self.enemy_group] 
        # Chỉ giữ lại các màu chưa được dùng
        available_colors = [c for c in all_colors if c not in used_colors]
        
        if not available_colors: 
            available_colors = all_colors # Fallback an toàn nếu lỡ sinh > 4 viên
            
        chosen_color = random.choice(available_colors)
        
        # --- KHỞI TẠO ENEMY VỚI MÀU MỚI VÀ ASSETS_PATH ---
        # Nhớ truyền self.assets_path vào nhé
        
        DFS_enemy = PathfindingEnemy(
            spawn_x, spawn_y, 
            self.pathfinder, 
            self.assets_path, # Tham số mới
            speed=scaled_speed, 
            radius=scaled_radius, 
            #color=chosen_color # Tham số mới
            color = 'blue' # DFS thì màu xanh biển, A* thì màu đỏ để dễ phân biệt
        )
        
        Astar_enemy = PathfindingEnemy(
            spawn_x, spawn_y, 
            self.astar_pathfinder,
            self.assets_path, # Tham số mới
            speed=scaled_speed, 
            radius=scaled_radius, 
            color= 'red' # A* thì màu đỏ để dễ phân biệt
        )
        DFS_enemy.set_collision_manager(self.collision_manager)
        Astar_enemy.set_collision_manager(self.collision_manager)
        
        map_width = self.map_loader.tmx_data.width * self.scaled_tile_size
        map_height = self.map_loader.tmx_data.height * self.scaled_tile_size
        DFS_enemy.set_random_target(map_width, map_height, self.scaled_tile_size)
        Astar_enemy.set_random_target(map_width, map_height, self.scaled_tile_size)
        self.enemy_group.add(DFS_enemy)
        self.enemy_group.add(Astar_enemy)

    def update(self):
        # NẾU GAME KẾT THÚC, ĐÓNG BĂNG MỌI THỨ, KHÔNG CẬP NHẬT LOGIC NỮA
        if self.state != "PLAYING":
            return
        
        """Gọi hàm update của tất cả các thực thể (Thỏ, Quái vật, Đạn...)"""
        self.player.update(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # --- CẬP NHẬT CAMERA OFFSET ---
        # Lấy tọa độ trung tâm của Thỏ trừ đi một nửa màn hình
        self.camera_x = self.player.rect.centerx - (self.SCREEN_WIDTH // 2)
        self.camera_y = self.player.rect.centery - (self.SCREEN_HEIGHT // 2)

        # Cập nhật Enemy di chuyển theo đường đã tìm
        self.enemy_group.update()

        # Để vòng while, khi bé hơn số lượng mình muốn thì spawn ra
        while len(self.enemy_group) < 4:
            self.spawn_random_enemy()

        # Quản lý thời gian spawn đạn
        #self.bullet_spawn_timer += 1
        spawn_positions = None # Mặc định là None (không tạo đạn)
        
        # Kiểm tra đạn chạm người chơi
        for bullet in self.enemy_group:
            if bullet.check_collision_with_player(self.player.rect):
                if hasattr(self.player, 'take_damage'):
                    self.player.take_damage(bullet.damage)
                bullet.kill() # Biến mất khi trúng người  

        # KIỂM TRA ĂN MẮT THẦN
        if self.magic_eye and self.player.rect.colliderect(self.magic_eye.rect):
            self.is_eye_active = True
            self.eye_timer = pygame.time.get_ticks() # Bấm giờ
            self.magic_eye = None # Ăn xong thì xóa item đi

        # KIỂM TRA THỜI GIAN MẮT THẦN HẾT HẠN (5 giây = 5000 ms)
        if self.is_eye_active:
            if pygame.time.get_ticks() - self.eye_timer > 5000:
                self.is_eye_active = False

        # Cập nhật thời gian đã chơi (Tính bằng giây)
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000.0

        # Kiểm tra điều kiện Thắng (Thỏ chạm Cửa)
        if self.exit_door and self.player.rect.colliderect(self.exit_door.rect):
            self.exit_door.open_door()  # Mở cửa khi player chạm vào
            if self.elapsed_time < self.best_time:
                self.score_dal.save_best_time(self.elapsed_time)
            self.state = "WIN" # Đổi trạng thái thay vì thoát game

        # Kiểm tra điều kiện Thua (Thỏ hết HP)
        if self.player.health <= 0:
            self.state = "GAME_OVER" # Đổi trạng thái thay vì thoát game

    def draw(self):
        # Xóa frame cũ
        self.screen.fill((0, 0, 0))
        self.virtual_surface.fill((0, 0, 0))
        
        # Vẽ mọi thứ lên cuộn phim ảo (Tuyệt đối không trừ biến camera)
        self.map_loader.sprite_group.draw(self.virtual_surface)
        
        if self.exit_door:
            self.virtual_surface.blit(self.exit_door.image, self.exit_door.rect)
        if self.magic_eye:
            self.virtual_surface.blit(self.magic_eye.image, self.magic_eye.rect)
            
        self.virtual_surface.blit(self.player.image, self.player.rect)
        self.enemy_group.draw(self.virtual_surface)

        if self.is_eye_active:
            # Chế độ thu nhỏ toàn bản đồ
            scaled_view = pygame.transform.scale(self.virtual_surface, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.screen.blit(scaled_view, (0, 0))
            
            # Thanh thời gian đếm ngược
            time_left = max(0, 5000 - (pygame.time.get_ticks() - self.eye_timer))
            bar_width = (time_left / 5000) * 200
            pygame.draw.rect(self.screen, (0, 255, 255), (self.SCREEN_WIDTH//2 - 100, 20, bar_width, 10))
        else:
            # Chế độ thường: Kéo cuộn phim theo góc nhìn của Thỏ
            self.screen.blit(self.virtual_surface, (-self.camera_x, -self.camera_y))

        # GỌI UI_MANAGER RA VẼ GIAO DIỆN
        if self.state == "PLAYING":
            # Chỉ vẽ máu và đồng hồ khi đang chơi
            self.ui_manager.draw_hud(self.screen, self.player.health, self.elapsed_time, self.best_time)
        else:
            # Nếu đang ở Menu Start, Thua, hoặc Thắng THÌ Vẽ màn hình Overlay
            self.ui_manager.draw_overlay_screen(self.screen, self.state, self.elapsed_time)

        pygame.display.flip()

    # vòng lặp vĩnh cữu cho game á
    # để chơi online được nên thêm thư viện pybag
    async def run(self):
        while self.is_running:
            self.handle_events() # xử lý nhập WASD hay mũi tên nè
            self.update() # Tính toán logic
            self.draw() # cập nhật hình ảnh
            self.clock.tick(60) # 60 pfs nè
            await asyncio.sleep(0) # Dòng này để code chạy trên web
           
        pygame.quit()
        sys.exit()

    #def run(self):
    #    while self.is_running:
    #        self.handle_events() # xử lý nhập WASD hay mũi tên nè
    #        self.update() # Tính toán logic
    #        self.draw() # cập nhật hình ảnh
    #        self.clock.tick(60) # 60 pfs nè
    #        
    #    pygame.quit()
    #    sys.exit()

    def spawn_exit_door(self):
        """Sinh Cửa Thoát Hiểm ở một vị trí ngẫu nhiên trên toàn Map"""
        tile_size = self.scaled_tile_size
        map_width = self.map_loader.tmx_data.width * tile_size
        map_height = self.map_loader.tmx_data.height * tile_size

        max_x = (map_width // tile_size) - 2
        max_y = (map_height // tile_size) - 2

        while True:
            tx = random.randint(1, max_x)
            ty = random.randint(1, max_y)
            # Dùng logic dò tường của DFS để tìm ô trống
            if self.pathfinder._is_valid((tx, ty)):
                spawn_x = tx * tile_size
                spawn_y = ty * tile_size

                # Đảm bảo cửa không sinh ra ngay dưới chân người chơi
                dist_to_player = ((spawn_x - self.player.x)**2 + (spawn_y - self.player.y)**2)**0.5
                if dist_to_player > 300: # Cửa phải cách thỏ ít nhất 300px
                    self.exit_door = ExitDoor(spawn_x, spawn_y, tile_size, self.assets_path)
                    break

    def spawn_magic_eye(self):
        """Sinh vật phẩm Mắt Thần ngẫu nhiên trên bản đồ"""
        tile_size = self.scaled_tile_size
        max_x = (self.map_width // tile_size) - 2
        max_y = (self.map_height // tile_size) - 2

        while True:
            tx = random.randint(1, max_x)
            ty = random.randint(1, max_y)
            if self.pathfinder._is_valid((tx, ty)):
                spawn_x = tx * tile_size
                spawn_y = ty * tile_size
                self.magic_eye = MagicEye(spawn_x, spawn_y, tile_size, assets_path=self.assets_path)
                break