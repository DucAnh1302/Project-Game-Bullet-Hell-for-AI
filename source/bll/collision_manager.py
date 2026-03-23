# nơi quản lý va đập
import pygame

class CollisionManager:
    """
    Tầng BLL (Business Logic Layer): Chuyên xử lý logic va chạm cho toàn bộ game.
    Tách biệt khỏi Models để code nhẹ và dễ quản lý hơn.
    """
    def __init__(self, tmx_data, scale_factor=1.0):
        self.tmx_data = tmx_data
        self.scale_factor = scale_factor
        self.walls = self._extract_walls()

    def _extract_walls(self):
        """Chỉ lấy các khung va chạm được vẽ tay trong layer 'walls' của Tiled"""
        walls = []
        if not self.tmx_data:
            return walls
        
        # Duyệt qua các object group trong Tiled
        for layer in self.tmx_data.objectgroups:
            if layer.name == 'walls': # Chỉ lấy layer có tên chính xác là 'walls'
                for obj in layer:
                    if hasattr(obj, 'width') and hasattr(obj, 'height'):
                        # Phóng to tọa độ và kích thước cho khớp với map đã Zoom 
                        # (đoạn này chắc không cần phóng to, nào phóng Đức Anh tính sau)
                        # Đức Anh: Tạo Rect và nhân với scale_factor để bức tường ảo to bằng bức tường trên hình
                        rect = pygame.Rect(
                            obj.x * self.scale_factor,
                            obj.y * self.scale_factor,
                            obj.width * self.scale_factor,
                            obj.height * self.scale_factor
                        )
                        walls.append(rect)
        return walls

    def is_colliding(self, future_rect):
        """Nhận vào 1 hitbox và check xem có đụng tường không"""
        # Đức Anh comment lại đoạn dưới cho dễ hiểu nè
        """Nhận vào 1 cái Hitbox (khung chữ nhật dự kiến sẽ bước tới).
        Trả về True nếu Hitbox đó đụng trúng bất kỳ bức tường nào."""
        for wall in self.walls:
            if future_rect.colliderect(wall):
                return True
        return False