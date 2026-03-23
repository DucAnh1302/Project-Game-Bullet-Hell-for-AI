import pygame
import os
from data.map_loader import MapLoader

pygame.init()

# Setup
MAP_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'Map', 'level1.tmx')
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullet Hell")
clock = pygame.time.Clock()

# Load map
map_loader = MapLoader()
map_loader.load_map(MAP_PATH)

# Game loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw
    screen.fill((0, 0, 0))  # Clear screen
    map_loader.draw(screen)
    pygame.display.flip()

pygame.quit()