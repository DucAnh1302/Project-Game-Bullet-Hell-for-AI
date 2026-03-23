import pygame
import pytmx
import os


class Tile(pygame.sprite.Sprite):
    """Represents a single tile from the TMX map."""
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class MapLoader:
    """Handles loading and rendering TMX map files."""
    def __init__(self):
        self.tmx_data = None
        self.sprite_group = pygame.sprite.Group()
    
    def load_map(self, map_path):
        """Load a TMX map file and create sprite group."""
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Map file not found: {map_path}")
        
        self.tmx_data = pytmx.load_pygame(map_path)
        self.sprite_group.empty()
        
        # Load all visible tile layers
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        tile = Tile(
                            tile_image,
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight
                        )
                        self.sprite_group.add(tile)
        
        return self.sprite_group
    
    def draw(self, surface):
        """Draw all tiles to the given surface."""
        self.sprite_group.draw(surface)
    
    def get_map_dimensions(self):
        """Get the map dimensions in pixels."""
        if self.tmx_data:
            width = self.tmx_data.width * self.tmx_data.tilewidth
            height = self.tmx_data.height * self.tmx_data.tileheight
            return width, height
        return None
