# source/models/exit_door.py
import pygame

class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        
        # Tạo hình ảnh cánh cửa (hình chữ nhật màu Vàng)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 215, 0)) # Màu Vàng Gold
        
        # Có thể thêm dòng chữ "EXIT" lên cửa cho sinh động
        font = pygame.font.SysFont(None, int(self.size * 0.5))
        text = font.render("EXIT", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.size//2, self.size//2))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)