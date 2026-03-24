# nơi sẽ chứa logic DFS
import random
import pygame

class DFSPathfinder:
    def __init__(self, collision_manager, tile_size=32):
        self.collision_manager = collision_manager
        self.tile_size = tile_size

    def get_path(self, start_pos, target_pos):
        """
        Tìm đường từ start_pos đến target_pos bằng DFS dạng Vòng lặp (Iterative).
        Sử dụng Stack thay vì Đệ quy để tránh lỗi RecursionError.
        """
        # Chuyển đổi tọa độ pixel sang tọa độ ô lưới (grid)
        start_node = (int(start_pos[0] // self.tile_size), int(start_pos[1] // self.tile_size))
        target_node = (int(target_pos[0] // self.tile_size), int(target_pos[1] // self.tile_size))
        
        # Khởi tạo Stack. Mỗi phần tử trong stack là 1 tuple: (node_hiện_tại, lộ_trình_đã_đi)
        stack = [(start_node, [start_node])]
        visited = set()
        
        while stack:
            current, path = stack.pop()
            
            # Nếu chạm đích, chuyển đổi toàn bộ lộ trình sang pixel và trả về
            if current == target_node:
                return [(node[0] * self.tile_size + self.tile_size // 2, 
                         node[1] * self.tile_size + self.tile_size // 2) for node in path]
            
            if current not in visited:
                visited.add(current)
                
                # Lấy các hàng xóm (Lên, Xuống, Trái, Phải) và xáo trộn để tạo tính ngẫu nhiên
                neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                random.shuffle(neighbors)
                
                for dx, dy in neighbors:
                    neighbor = (current[0] + dx, current[1] + dy)
                    
                    # Nếu ô hợp lệ và chưa từng đi qua
                    if self._is_valid(neighbor) and neighbor not in visited:
                        # Thêm hàng xóm vào stack kèm theo lộ trình mới
                        stack.append((neighbor, path + [neighbor]))
                        
        # Nếu duyệt hết mà không thấy đường (bị kẹt cứng), trả về list rỗng
        return []

    def _is_valid(self, node):
        """Kiểm tra xem ô (node) có hợp lệ không (trong bounds và không dính tường)"""
        if node[0] < 0 or node[1] < 0:
            return False
        if hasattr(self.collision_manager, 'tmx_data') and self.collision_manager.tmx_data:
            w = getattr(self.collision_manager.tmx_data, 'width', 999999)
            h = getattr(self.collision_manager.tmx_data, 'height', 999999)
            if node[0] >= w or node[1] >= h:
                return False
        rect = pygame.Rect(node[0] * self.tile_size, node[1] * self.tile_size, self.tile_size, self.tile_size)
        return not self.collision_manager.is_colliding(rect)