# nơi sẽ chứa logic DFS
import random
import pygame
import heapq

class DFSPathfinder:
    def __init__(self, collision_manager, tile_size=32):
        self.collision_manager = collision_manager
        self.tile_size = tile_size

    def get_path(self, start_pos, target_pos):
        """
        Tìm đường từ start_pos đến target_pos.
        CHẾ ĐỘ BULLET HELL: Trả về TOÀN BỘ lịch sử di chuyển vật lý.
        Ép quái vật phải đi vào ngõ cụt, sau đó quay đầu đi lùi lại ngã ba để tìm đường mới.
        """
        # Chuyển đổi tọa độ pixel sang tọa độ ô lưới (grid)
        start_node = (int(start_pos[0] // self.tile_size), int(start_pos[1] // self.tile_size))
        target_node = (int(target_pos[0] // self.tile_size), int(target_pos[1] // self.tile_size))
        
        stack = [(start_node, [start_node])]
        visited = set()
        
        exploration_history = [] # Lưu toàn bộ bước đi (kể cả bước lùi)
        previous_path = [] # Đường đi của nhánh đang xét ngay trước đó
        
        while stack:
            current, current_path = stack.pop()
            
            # Nếu ô này đã xét rồi thì bỏ qua
            if current in visited:
                continue
                
            visited.add(current)
            
            # Nếu là bước đầu tiên thì cứ lưu vào lịch sử
            if not previous_path:
                exploration_history.append(current)
            else:
                # --- THUẬT TOÁN ĐI LÙI (BACKTRACKING) ---
                # Tìm Ngã Ba chung: Tìm xem nhánh cũ và nhánh mới tách ra từ điểm nào
                common_len = 0
                for i in range(min(len(previous_path), len(current_path))):
                    if previous_path[i] == current_path[i]:
                        common_len += 1
                    else:
                        break
                
                # Bước Lùi: Kéo quái vật đi lùi từ điểm ngõ cụt hiện tại về lại Ngã Ba
                # Kỹ thuật Python: Lấy mảng từ ngã ba đến ngõ cụt, rồi [::-1] để đảo ngược mảng (đi lùi)
                backtrack_nodes = previous_path[common_len-1 : -1][::-1]
                exploration_history.extend(backtrack_nodes)
                
                # Bước Tiến: Bắt đầu đi từ Ngã Ba vào nhánh đường mới
                forward_nodes = current_path[common_len:]
                exploration_history.extend(forward_nodes)
                
            # Lưu lại dấu chân để vòng lặp sau còn biết đường mà lùi
            previous_path = current_path
            
            # Chạm đích thì báo động dừng suy nghĩ
            if current == target_node:
                break
                
            # Lấy các hàng xóm (Lên, Xuống, Trái, Phải) và xáo trộn để tạo tính ngẫu nhiên
            neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(neighbors)
            
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                if self._is_valid(neighbor) and neighbor not in visited:
                    stack.append((neighbor, current_path + [neighbor]))
                    
        # Chuyển đổi toàn bộ "băng ghi hình" sang tọa độ pixel để quái vật chạy theo
        pixel_path = []
        for node in exploration_history:
            px = node[0] * self.tile_size + self.tile_size // 2
            py = node[1] * self.tile_size + self.tile_size // 2
            pixel_path.append((px, py))
            
        return pixel_path
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

class AStarPathfinder:
    def __init__(self, collision_manager, tile_size=32):
        self.collision_manager = collision_manager
        self.tile_size = tile_size

    def heuristic(self, a, b):
        """Hàm khoảng cách Manhattan để tính toán chi phí ước tính đến đích"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_path(self, start_pos, target_pos):
        """Tìm đường đi ngắn nhất từ start_pos đến target_pos bằng thuật toán A*"""
        start_node = (int(start_pos[0] // self.tile_size), int(start_pos[1] // self.tile_size))
        target_node = (int(target_pos[0] // self.tile_size), int(target_pos[1] // self.tile_size))

        # Priority queue để lưu trữ các node cần xét (f_score, (x, y))
        open_set = []
        heapq.heappush(open_set, (0, start_node))
        
        # Dùng để truy vết đường đi
        came_from = {}
        
        # Chi phí đi từ start_node tới một node hiện tại
        g_score = {start_node: 0}
        
        # Chi phí dự kiến từ start_node qua node hiện tại để tới target_node (f = g + h)
        f_score = {start_node: self.heuristic(start_node, target_node)}

        while open_set:
            # Lấy ra node có f_score thấp nhất (chi phí tổng dự kiến nhỏ nhất)
            current_f, current = heapq.heappop(open_set)

            # Nếu chạm đích, truy vết lại đường đi và thoát
            if current == target_node:
                return self.reconstruct_path(came_from, current)

            neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Kiểm tra va chạm với tường và ranh giới map
                if not self._is_valid(neighbor):
                    continue
                    
                # Khoảng cách giữa các ô lưới kề nhau mặc định là 1
                tentative_g_score = g_score[current] + 1

                # Nếu tìm được đường ngắn hơn để đến node hàng xóm này
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, target_node)
                    
                    # Đưa hàng xóm vào hàng đợi ưu tiên để duyệt tiếp
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Nếu không có đường đi (bị chặn toàn bộ), trả về list rỗng
        return []

    def reconstruct_path(self, came_from, current):
        """Hàm phụ trợ để dựng lại mảng đường đi theo đúng thứ tự (từ start -> đích)"""
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
            
        total_path.reverse() # A* truy vết từ đích ngược về nguồn nên cần đảo mảng lại
        
        # Chuyển đổi Grid sang tọa độ Pixel (tâm của ô)
        pixel_path = []
        for node in total_path:
            px = node[0] * self.tile_size + self.tile_size // 2
            py = node[1] * self.tile_size + self.tile_size // 2
            pixel_path.append((px, py))
            
        return pixel_path

    def _is_valid(self, node):
        """Sử dụng chung hàm kiểm tra va chạm giống y hệt DFSPathfinder"""
        if node[0] < 0 or node[1] < 0:
            return False
        if hasattr(self.collision_manager, 'tmx_data') and self.collision_manager.tmx_data:
            w = getattr(self.collision_manager.tmx_data, 'width', 999999)
            h = getattr(self.collision_manager.tmx_data, 'height', 999999)
            if node[0] >= w or node[1] >= h:
                return False
        rect = pygame.Rect(node[0] * self.tile_size, node[1] * self.tile_size, self.tile_size, self.tile_size)
        return not self.collision_manager.is_colliding(rect)