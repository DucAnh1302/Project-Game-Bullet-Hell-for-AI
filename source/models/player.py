import pygame
import os

class Player(pygame.sprite.Sprite):
    """
    Tầng Models: Chỉ chứa dữ liệu, trạng thái (tọa độ, ảnh, tốc độ) của nhân vật.
    Các tính toán logic phức tạp sẽ nhờ BLL làm giúp.
    """
    
    def __init__(self, x, y, assets_path, tile_size=16):
        super().__init__()
        # Đức Anh: Tọa độ thực tế của người chơi trên màn hình
        self.x = x
        self.y = y
        # Đức Anh: Vận tốc di chuyển theo trục X và Y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5 # tốc độ di chuyển (pixel/frame)
        self.tile_size = tile_size
        
        # Sprites with scaling
        # Đức Anh: Quản lý hình ảnh thấy đúng hơn á
        self.sprites = {}
        self.current_direction = 'down'
        self.scale = 1  # Kích thước thỏ chuẩn # đại khái là chuẩn 1:1 nhé
        self.load_sprites(assets_path)
        
        # Thiết lập down khi mới vào game
        self.image = self.sprites['down']
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
        # BLL Collision Manager # đại khái là cái biến gọi bll ra á
        self.collision_manager = None
    
    def load_sprites(self, assets_path):
        """Load and scale player sprites from assets directory."""
        # Đức Anh ghi cho dễ hiểu là:
        # Hệ thống tải hình ảnh nhân vật theo 4 hướng
        player_path = os.path.join(assets_path, 'Player')
        sprite_files = {
            'up': 'playerUp.png',
            'down': 'playerDown.png',
            'left': 'playerLeft.png',
            'right': 'playerRight.png'
        }
        
        # Quét và load từng ảnh vào bộ nhớ
        for direction, filename in sprite_files.items():
            file_path = os.path.join(player_path, filename)
            if os.path.exists(file_path):
                original = pygame.image.load(file_path).convert_alpha()
                new_size = (original.get_width() * self.scale, original.get_height() * self.scale)
                self.sprites[direction] = pygame.transform.scale(original, new_size)
            else:
                # Nếu mất file ảnh thì hiện cục màu xanh lá cây để báo lỗi
                self.sprites[direction] = pygame.Surface((32 * self.scale, 32 * self.scale))
                self.sprites[direction].fill((0, 255, 0))
    
    def set_collision_manager(self, collision_manager):
        """Nhận hệ thống quản lý va chạm từ bên ngoài truyền vào"""
        # Đúng hơn là: Bơm (Inject) hệ thống quản lý va chạm BLL vào Model
        self.collision_manager = collision_manager
        
    def _check_move(self, new_x, new_y):
        """Tạo Hitbox nhỏ ở chân và hỏi CollisionManager xem đi được không"""
        if not self.collision_manager:
            return True # đổi False là đi xuyên tường á
            
        # Hitbox siêu nhỏ (25%) ở tâm gót chân (tối thiểu 4px nha)
        hitbox_w = max(int(self.rect.width * 0.25), 4)  
        hitbox_h = max(int(self.rect.height * 0.25), 4) 

        # Căn giữa hitbox theo chiều ngang, và ép nó xuống sát gót chân thỏ
        hitbox_x = new_x + (self.rect.width - hitbox_w) // 2
        hitbox_y = new_y + self.rect.height - hitbox_h - 2 # Trừ đi 2 pixel để mượt hơn
        
        # Tạo khung ảo và ném sang cho BLL check xem có đụng tường không
        future_rect = pygame.Rect(hitbox_x, hitbox_y, hitbox_w, hitbox_h)
        return not self.collision_manager.is_colliding(future_rect)

    def handle_input(self):
        """Handle keyboard input for movement."""
        # hiểu đơn giản là các nút WASD và các phím mũi tên á
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        self.velocity_y = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -self.speed
            self.current_direction = 'up'
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = self.speed
            self.current_direction = 'down'
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
            self.current_direction = 'left'
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
            self.current_direction = 'right'

    def update(self, screen_width, screen_height):
        """Cập nhật vị trí mượt mà"""
        # đại khái là 60 lần trong 1 giây
        self.handle_input()
        
        # Trượt theo trục X
        # Tách riêng việc check va chạm trục X và trục Y
        # Mục đích: Nếu bạn đâm xéo vào tường, 
        # nhân vật sẽ trượt dọc theo bức tường chứ không bị khựng lại
        if self._check_move(self.x + self.velocity_x, self.y):
            self.x += self.velocity_x
            
        # Trượt theo trục Y
        if self._check_move(self.x, self.y + self.velocity_y):
            self.y += self.velocity_y
            
        # Chặn biên màn hình
        self.x = max(0, min(self.x, screen_width - self.rect.width))
        self.y = max(0, min(self.y, screen_height - self.rect.height))
        
        # Cập nhật lại ảnh quay mặt theo hướng di chuyển
        self.image = self.sprites.get(self.current_direction, self.sprites['down'])
        self.rect.topleft = (self.x, self.y)
    
    def draw(self, surface):
        # In hình nhân vật lên màn hình thôi
        surface.blit(self.image, self.rect)