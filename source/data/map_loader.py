import pygame
import pytmx
import os


# gọi class tile bên map
from models.map import Tile


class MapLoader:
    """Handles loading and rendering TMX map files with zoom support."""
    def __init__(self, screen_width=800, screen_height=600):
        self.tmx_data = None
        self.sprite_group = pygame.sprite.Group()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.zoom_level = 1.0
        self.map_path = None
        self.scale_to_fit = True
    
    def load_map(self, map_path, scale_to_fit=True):
        """Load a TMX map file and create sprite group.
        
        Args:
            map_path: Path to the TMX file
            scale_to_fit: If True, scale map to fill screen while maintaining aspect ratio
        """
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Map file not found: {map_path}")
        
        self.map_path = map_path
        self.scale_to_fit = scale_to_fit
        self.tmx_data = pytmx.load_pygame(map_path)
        self.sprite_group.empty()
        
        # Calculate scale factors to fit map to screen
        original_width = self.tmx_data.width * self.tmx_data.tilewidth
        original_height = self.tmx_data.height * self.tmx_data.tileheight
        
        if scale_to_fit:
            self.scale_x = self.screen_width / original_width
            self.scale_y = self.screen_height / original_height
            # Use the same scale for both to maintain aspect ratio
            scale = min(self.scale_x, self.scale_y)
            self.scale_x = scale
            self.scale_y = scale
        else:
            self.scale_x = 1.0
            self.scale_y = 1.0
        
        # Apply zoom level to scale
        final_scale_x = self.scale_x * self.zoom_level
        final_scale_y = self.scale_y * self.zoom_level
        
        # Load all visible tile layers with scaling
        scaled_tilewidth = int(self.tmx_data.tilewidth * final_scale_x)
        scaled_tileheight = int(self.tmx_data.tileheight * final_scale_y)
        
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        # Scale the tile image
                        scaled_image = pygame.transform.scale(
                            tile_image,
                            (scaled_tilewidth, scaled_tileheight)
                        )
                        tile = Tile(
                            scaled_image,
                            x * scaled_tilewidth,
                            y * scaled_tileheight
                        )
                        self.sprite_group.add(tile)
        
        return self.sprite_group
    
    def set_zoom(self, zoom_level):
        """Set zoom level and reload the map.
        
        Args:
            zoom_level: Zoom factor (1.0 = default, > 1.0 = zoom in, < 1.0 = zoom out)
        """
        if zoom_level <= 0:
            return  # Prevent invalid zoom levels
        
        self.zoom_level = zoom_level
        if self.map_path:
            self.load_map(self.map_path, self.scale_to_fit)
    
    def draw(self, surface):
        """Draw all tiles to the given surface."""
        self.sprite_group.draw(surface)
    
    def get_map_dimensions(self):
        """Get the map dimensions in pixels."""
        if self.tmx_data:
            width = 1600
            height = 1200
            return width, height
        return None
