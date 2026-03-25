# source/models/magic_eye.py
import pygame
import os

class MagicEye(pygame.sprite.Sprite):
    def __init__(self, x, y, size, assets_path):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.assets_path = assets_path
        
        # Tải sprite mắt thần từ Items/map.png
        try:
            eye_path = os.path.join(self.assets_path, 'Items', 'map.png')
            if os.path.exists(eye_path):
                self.image = pygame.image.load(eye_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
            else:
                raise FileNotFoundError(f"Không tìm thấy sprite mắt thần tại: {eye_path}")
        except Exception as e:
            print(f"Lỗi tải sprite mắt thần: {e}")
            # Fallback: Tạo hình ảnh mặc định nếu không load được sprite
            self._create_fallback_image()
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
    
    def _create_fallback_image(self):
        """Vẽ mắt thần dự phòng nếu không load được sprite"""
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center_x = self.size // 2
        center_y = self.size // 2
        
        # Vòng tròn ngoài (white/light sclera)
        pygame.draw.circle(self.image, (220, 220, 255), (center_x, center_y), self.size // 2)
        
        # Viền ngoài màu tím (magic aura)
        pygame.draw.circle(self.image, (200, 0, 200), (center_x, center_y), self.size // 2, 3)
        
        # Iris (tròn màu xanh/vàng ở giữa)
        iris_radius = self.size // 4
        pygame.draw.circle(self.image, (100, 200, 255), (center_x, center_y), iris_radius)
        
        # Pupil (tròn đen ở giữa)
        pupil_radius = self.size // 8
        pygame.draw.circle(self.image, (0, 0, 0), (center_x, center_y), pupil_radius)
        
        # Highlight (ánh sáng trên mắt)
        highlight_x = center_x - pupil_radius // 2
        highlight_y = center_y - pupil_radius // 2
        pygame.draw.circle(self.image, (255, 255, 255), (highlight_x, highlight_y), pupil_radius // 3)