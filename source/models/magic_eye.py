# source/models/magic_eye.py
import pygame

class MagicEye(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        
        # Vẽ một viên ngọc màu Xanh Lục Lam (Cyan) phát sáng
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255), (self.size//2, self.size//2), self.size//2 - 2)
        pygame.draw.circle(self.image, (255, 255, 255), (self.size//2, self.size//2), self.size//4)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)