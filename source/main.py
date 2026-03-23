import pygame
import os
from data.map_loader import MapLoader
from bll.player import Player

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
map_loader = MapLoader(SCREEN_WIDTH, SCREEN_HEIGHT)
map_loader.load_map(MAP_PATH, scale_to_fit=True)

# Initialize player
# Spawn at a safe position away from decorations (200, 250)
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
player = Player(200, 220, ASSETS_PATH)
# Set collision map data
player.set_collision_map(map_loader.tmx_data)

# Zoom level
zoom = 1.0
zoom_step = 0.1  # How much to increase/decrease per keystroke

# Game loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle zoom with keyboard
    keys = pygame.key.get_pressed()
    old_zoom = zoom
    
    if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:  # Zoom in
        zoom = min(zoom + zoom_step, 3.0)  # Max zoom 3x
    if keys[pygame.K_MINUS]:  # Zoom out
        zoom = max(zoom - zoom_step, 0.3)  # Min zoom 0.3x
    
    # Apply zoom if changed
    if zoom != old_zoom:
        map_loader.set_zoom(zoom)
    
    # Update player
    player.update(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Draw
    screen.fill((0, 0, 0))  # Clear screen
    map_loader.draw(screen)
    player.draw(screen)
    pygame.display.flip()

pygame.quit()