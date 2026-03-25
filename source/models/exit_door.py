# source/models/exit_door.py
import pygame
import os

class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, x, y, size, assets_path):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.assets_path = assets_path
        
        # Tải 2 sprites của cửa (đóng và mở)
        self.door_closed_img = None
        self.door_open_img = None
        self.is_open = False
        
        # Load sprite từ file
        try:
            door_closed_path = os.path.join(self.assets_path, 'Items', 'door_closed.png')
            door_open_path = os.path.join(self.assets_path, 'Items', 'door_open.png')
            
            if os.path.exists(door_closed_path):
                self.door_closed_img = pygame.image.load(door_closed_path).convert_alpha()
                self.door_closed_img = pygame.transform.scale(self.door_closed_img, (self.size, self.size))
            
            if os.path.exists(door_open_path):
                self.door_open_img = pygame.image.load(door_open_path).convert_alpha()
                self.door_open_img = pygame.transform.scale(self.door_open_img, (self.size, self.size))
            
            # Nếu load thành công, dùng sprite, nếu không thì fallback sang phương cách cũ
            if self.door_closed_img:
                self.image = self.door_closed_img.copy()
            else:
                self._create_fallback_image()
        except Exception as e:
            print(f"Lỗi tải sprite cửa: {e}")
            self._create_fallback_image()
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
    
    def _create_fallback_image(self):
        """Fallback: Tạo hình ảnh cánh cửa mặc định nếu không load được sprite"""
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 215, 0))  # Màu Vàng Gold
        
        font = pygame.font.Font(None, 16)
        text = font.render("EXIT", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.size//2, self.size//2))
        self.image.blit(text, text_rect)
    
    def open_door(self):
        """Mở cửa: đổi sang sprite door_open"""
        if self.door_open_img and not self.is_open:
            self.image = self.door_open_img.copy()
            self.is_open = True
    
    def close_door(self):
        """Đóng cửa: đổi sang sprite door_closed"""
        if self.door_closed_img and self.is_open:
            self.image = self.door_closed_img.copy()
            self.is_open = False