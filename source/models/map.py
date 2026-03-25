# source/models/map.py
import pygame

class Tile(pygame.sprite.Sprite):
    """
    Tầng Models: Đại diện cho một viên gạch (thực thể) trên bản đồ.
    Chỉ lưu trữ hình ảnh và tọa độ hiển thị.
    """
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)