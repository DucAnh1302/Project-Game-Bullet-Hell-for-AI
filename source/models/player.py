import pygame
import os


class Player(pygame.sprite.Sprite):
    """Player character with movement, sprite handling, and collision detection."""
    
    def __init__(self, x, y, assets_path, tile_size=16):
        """Initialize player.
        
        Args:
            x: Starting X position
            y: Starting Y position
            assets_path: Path to assets directory
            tile_size: Size of tiles on map for collision (default 16)
        """
        super().__init__()
        
        # Position and velocity
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.tile_size = tile_size
        
        # Sprites with scaling
        self.sprites = {}
        self.current_direction = 'down'
        self.scale = 2  # Scale factor for player sprite (2x larger)
        self.load_sprites(assets_path)
        
        # Set initial sprite
        self.image = self.sprites['down']
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
        # Collision data
        self.collision_map = None
        self.collision_rects = []
    
    def load_sprites(self, assets_path):
        """Load and scale player sprites from assets directory."""
        player_path = os.path.join(assets_path, 'Player')
        sprite_files = {
            'up': 'playerUp.png',
            'down': 'playerDown.png',
            'left': 'playerLeft.png',
            'right': 'playerRight.png'
        }
        
        for direction, filename in sprite_files.items():
            file_path = os.path.join(player_path, filename)
            if os.path.exists(file_path):
                original = pygame.image.load(file_path).convert_alpha()
                # Scale the sprite
                new_size = (original.get_width() * self.scale, original.get_height() * self.scale)
                self.sprites[direction] = pygame.transform.scale(original, new_size)
            else:
                # Create a placeholder surface if file doesn't exist
                self.sprites[direction] = pygame.Surface((32 * self.scale, 32 * self.scale))
                self.sprites[direction].fill((0, 255, 0))  # Green placeholder
    
    def set_collision_map(self, tmx_data):
        """Set collision map data from TMX file.
        
        Args:
            tmx_data: pytmx object containing map data
        """
        self.collision_map = tmx_data
        self.collision_rects = self._extract_collision_rects()
    
    def _extract_collision_rects(self):
        """Extract collision rectangles from walls object layer and nearby maze tiles.
        
        Returns:
            List of pygame.Rect objects representing collision boundaries
        """
        collision_rects = []
        
        if not self.collision_map:
            return collision_rects
        
        # Get collision rects from walls object layer
        for layer in self.collision_map.objectgroups:
            if layer.name == 'walls':
                for obj in layer:
                    if hasattr(obj, 'width') and hasattr(obj, 'height'):
                        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        collision_rects.append(rect)
        
        return collision_rects
    
    def _get_nearby_maze_collision_rects(self, x, y):
        """Get collision rects from maze tiles near the player.
        
        Args:
            x: Player X position
            y: Player Y position
            
        Returns:
            List of collision rects from nearby maze tiles
        """
        collision_rects = []
        
        maze_layer = None
        for layer in self.collision_map.visible_layers:
            if hasattr(layer, 'name') and layer.name == 'maze':
                maze_layer = layer
                break
        
        if not maze_layer:
            return collision_rects
        
        # Check tiles in a radius around the player (3x3 tile area)
        player_tile_x = x // self.tile_size
        player_tile_y = y // self.tile_size
        
        try:
            for ty in range(max(0, player_tile_y - 2), min(self.collision_map.height, player_tile_y + 3)):
                for tx in range(max(0, player_tile_x - 2), min(self.collision_map.width, player_tile_x + 3)):
                    tile_gid = maze_layer.data[ty][tx]
                    if tile_gid != 0:
                        rect = pygame.Rect(
                            tx * self.tile_size,
                            ty * self.tile_size,
                            self.tile_size,
                            self.tile_size
                        )
                        collision_rects.append(rect)
        except (IndexError, TypeError, AttributeError):
            pass
        
        return collision_rects
    
    def is_colliding(self, x, y):
        """Check if position collides with walls or maze tiles.
        
        Args:
            x: X position to check
            y: Y position to check
            
        Returns:
            True if collision detected, False otherwise
        """
        # Collision disabled - player moves freely
        return False
    
    def handle_input(self):
        """Handle keyboard input for movement (WASD + Arrow keys)."""
        keys = pygame.key.get_pressed()
        
        # Reset velocity
        self.velocity_x = 0
        self.velocity_y = 0
        
        # WASD controls
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
        """Update player position with collision detection."""
        self.handle_input()
        
        # Try to move in X direction
        new_x = self.x + self.velocity_x
        if not self.is_colliding(new_x, self.y):
            self.x = new_x
        
        # Try to move in Y direction
        new_y = self.y + self.velocity_y
        if not self.is_colliding(self.x, new_y):
            self.y = new_y
        
        # Keep player within screen bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.rect.width > screen_width:
            self.x = screen_width - self.rect.width
        if self.y < 0:
            self.y = 0
        if self.y + self.rect.height > screen_height:
            self.y = screen_height - self.rect.height
        
        # Update sprite based on direction
        self.image = self.sprites.get(self.current_direction, self.sprites['down'])
        self.rect.topleft = (self.x, self.y)
    
    def draw(self, surface):
        """Draw player on surface."""
        surface.blit(self.image, self.rect)
