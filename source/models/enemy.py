import pygame
import math
import random
class BulletEnemy(pygame.sprite.Sprite):
    """
    Kẻ thù hình viên đạn gây sát thương khi chạm vào người chơi.
    Tầng Models: Chỉ chứa dữ liệu, trạng thái (tọa độ, vận tốc, hình dạng) của kẻ thù.
    """
    
    def __init__(self, x, y, direction_x, direction_y, speed=3, radius=6,damage=10):
        """
        Args:
            x: Tọa độ X ban đầu
            y: Tọa độ Y ban đầu
            direction_x: Hướng chuyển động theo trục X (-1, 0, hoặc 1)
            direction_y: Hướng chuyển động theo trục Y (-1, 0, hoặc 1)
            speed: Tốc độ di chuyển (pixel/frame)
            radius: Bán kính của viên đạn (pixel)
            damage: Lượng sát thương gây ra (HP)
        """
        super().__init__()
        
        # Vị trí và vận tốc
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.damage = damage
        
        # Normalize hướng di chuyển
        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        if magnitude > 0:
            self.velocity_x = (direction_x / magnitude) * self.speed
            self.velocity_y = (direction_y / magnitude) * self.speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        
        # Tạo hình tròn cho viên đạn
        self._create_bullet_sprite()
        
        # Collision manager (sẽ được set từ GameLoop)
        self.collision_manager = None
    
    def _create_bullet_sprite(self):
        """Tạo hình ảnh viên đạn hình tròn với màu đỏ"""
        # Tạo surface hình vuông để vẽ hình tròn
        size = self.radius * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Vẽ viên đạn hình tròn màu đỏ
        pygame.draw.circle(self.image, (255, 50, 50), (self.radius, self.radius), self.radius)
        
        # Tạo rect cho collision detection
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def update(self):
        """Cập nhật vị trí của viên đạn theo mỗi frame"""
        # Tính toán vị trí mới
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        # Cập nhật tạm hitbox để check va chạm tổng thể (cả X và Y)
        collision_rect = self.get_collision_rect()
        collision_rect.center = (new_x, new_y)
        
        if self.collision_manager and self.collision_manager.is_colliding(collision_rect):
            # Nếu viên đạn chạm tường -> tự hủy luôn!
            self.kill()
            return # Cực kỳ quan trọng: Thoát hàm ngay để không chạy các dòng dưới
            
        # Nếu không chạm tường thì cập nhật vị trí mới
        self.x = new_x
        self.y = new_y
        self.rect.center = (self.x, self.y)
    
    def get_collision_rect(self):
        """Trả về hitbox của viên đạn để kiểm tra va chạm"""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
    
    def check_collision_with_player(self, player_rect):
        """
        Kiểm tra xem viên đạn có va chạm với người chơi không
        
        Args:
            player_rect: pygame.Rect của người chơi
            
        Returns:
            True nếu va chạm, False nếu không
        """
        bullet_rect = self.get_collision_rect()
        return bullet_rect.colliderect(player_rect)
    
    def set_collision_manager(self, collision_manager):
        """Nhận hệ thống quản lý va chạm từ bên ngoài truyền vào"""
        self.collision_manager = collision_manager
    
    def is_out_of_bounds(self, screen_width, screen_height):
        """Kiểm tra xem viên đạn có ra ngoài màn hình không"""
        return (self.x < -self.radius or 
                self.x > screen_width + self.radius or
                self.y < -self.radius or 
                self.y > screen_height + self.radius)


#Tạm thời không dùng tới
class BulletEnemySpawner:
    """
    Quản lý việc tạo ra các viên đạn theo thời gian.
    Có thể tạo ra các pattern khác nhau như tia, vòng tròn, v.v.
    """
    
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 30  # Tạo viên đạn mỗi 30 frame

    def create_bullet(self, x, y, dir_x, dir_y, speed=3, radius=8, damage=10):
        bullet = BulletEnemy(x, y, dir_x, dir_y, speed=speed, radius=radius, damage=damage)
        self.enemies.add(bullet)
        return bullet
    
    def update(self, spawn_positions=None):
        """
        Cập nhật spawner và các viên đạn
        
        Args:
            spawn_positions: Danh sách tuple (x, y, direction_x, direction_y) để tạo viên đạn
        """
        # Cập nhật các viên đạn hiện có
        for enemy in self.enemies:
            enemy.update()
        
        # Xóa các viên đạn ra ngoài màn hình
        for enemy in list(self.enemies):
            if enemy.is_out_of_bounds(800, 600):  # Giả sử màn hình 800x600
                enemy.kill()
        
        # Tạo viên đạn mới từ spawn_positions nếu có
        if spawn_positions:
            for pos in spawn_positions:
                x, y, dir_x, dir_y = pos
                enemy = BulletEnemy(x, y, dir_x, dir_y)
                self.enemies.add(enemy)
    
    def get_enemies(self):
        """Trả về sprite group chứa tất cả viên đạn"""
        return self.enemies
    
    def clear_all(self):
        """Xóa tất cả viên đạn"""
        self.enemies.empty()


class PathfindingEnemy(BulletEnemy):
    def __init__(self, x, y, pathfinder, speed=2):
        super().__init__(x, y, 0, 0, speed)
        self.pathfinder = pathfinder
        self.path = []
        self.target_node_index = 0
        self.current_destination = None

    def set_random_target(self, max_width, max_height, tile_size=32):
        """Chọn đích đến là một ô ngẫu nhiên Ở TRONG MÀN HÌNH VÀ MÊ CUNG"""
        while True:
            # Chọn tọa độ tx, ty cách mép ngoài 1 chút (tránh lỗi mép viền)
            tx = random.randint(1, (max_width // tile_size) - 2) * tile_size
            ty = random.randint(1, (max_height // tile_size) - 2) * tile_size
            
            # Tạo hitbox ảo để check xem ô này có bị kẹt trong tường không
            test_rect = pygame.Rect(tx, ty, tile_size, tile_size)
            
            # Nếu KHÔNG va chạm tường -> ô trống hợp lệ -> Thoát vòng lặp
            if not self.pathfinder.collision_manager.is_colliding(test_rect):
                break 
                
        # Bắt đầu tìm đường từ vị trí hiện tại đến đích hợp lệ vừa tìm được
        self.path = self.pathfinder.get_path((self.x, self.y), (tx, ty))
        self.target_node_index = 0
        
        if self.path:
            self.current_destination = self.path[0]
        else:
            self.current_destination = None

    def update(self):
        """Cập nhật logic và Xóa Enemy (biến mất) khi chạm đích"""
        if not self.current_destination:
            self.kill() # Lệnh này của pygame sẽ xóa obj khỏi Sprite Group
            return

        # Tính toán di chuyển về đích hiện tại
        dx = self.current_destination[0] - self.x
        dy = self.current_destination[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.speed:
            self.target_node_index += 1
            if self.target_node_index < len(self.path):
                self.current_destination = self.path[self.target_node_index]
            else:
                self.current_destination = None # Đã chạm đích cuối
                self.kill() # Biến mất
        else:
            # Di chuyển từng frame
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            self.rect.center = (self.x, self.y)