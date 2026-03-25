import pygame
import os
import sys
import random

# --- CẤU HÌNH ĐƯỜNG DẪN (Chỉ dùng cho file test) ---
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

from data.map_loader import MapLoader
from bll.collision_manager import CollisionManager

def test_dfs_debugger():
    """Hàm chạy Debugger cho thuật toán DFS từng bước một"""
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DFS Visual Debugger - Step by Step")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 14)
    small_font = pygame.font.SysFont("consolas", 10)

    # TẢI DỮ LIỆU MAP
    assets_path = os.path.join(base_dir, 'assets')
    map_path = os.path.join(assets_path, 'Map', 'level1.tmx')
    
    map_loader = MapLoader(SCREEN_WIDTH, SCREEN_HEIGHT)
    map_loader.load_map(map_path, scale_to_fit=True)
    scale_factor = map_loader.scale_x
    collision_manager = CollisionManager(map_loader.tmx_data, scale_factor)
    
    tile_size = int(16 * scale_factor) # Chuẩn 20px
    grid_width = 30 # Map 30x30 ô
    grid_height = 30

    # CÁC BIẾN QUẢN LÝ TRẠNG THÁI DEBUGGER
    start_node = None
    target_node = None
    phase = "SELECT_START" # Các pha: SELECT_START, SELECT_TARGET, DEBUGGING, DONE
    
    # Lưu lại lịch sử các trạng thái để có thể Undo (Bấm R)
    state_history = [] 
    
    def get_initial_state():
        return {
            'stack': [(start_node, [start_node])],
            'visited': set(),
            'current': None,
            'path': [],
            'action_log': "Sẵn sàng duyệt DFS...",
            'done': False
        }

    def step_forward(current_state):
        """Hàm tính toán 1 bước duy nhất của DFS"""
        stack = list(current_state['stack'])
        visited = set(current_state['visited'])
        path = list(current_state['path'])
        
        if not stack:
            return {**current_state, 'action_log': "Không tìm thấy đường!", 'done': True}
            
        current, current_path = stack.pop()
        
        # Đã chạm đích
        if current == target_node:
            return {'stack': stack, 'visited': visited, 'current': current, 'path': current_path, 'action_log': f"ĐÃ CHẠM ĐÍCH {current}!", 'done': True}
            
        # Nút đã xét thì lùi lại (Backtrack)
        if current in visited:
            return {'stack': stack, 'visited': visited, 'current': current, 'path': current_path, 'action_log': f"Ô {current} đã đi qua. BACKTRACK!", 'done': False}
            
        visited.add(current)
        
        # Tìm hàng xóm
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(neighbors)
        
        added_count = 0
        for dx, dy in neighbors:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                rect = pygame.Rect(nx * tile_size, ny * tile_size, tile_size, tile_size)
                # Nếu không đụng tường (tường + vật trang trí)
                if not collision_manager.is_colliding(rect) and (nx, ny) not in visited:
                    stack.append(((nx, ny), current_path + [(nx, ny)]))
                    added_count += 1
                    
        if added_count > 0:
            log = f"Tới {current}. Thêm {added_count} ngã rẽ vào Stack."
        else:
            log = f"Tới {current}. NGÕ CỤT! Chờ Backtrack..."
            
        return {'stack': stack, 'visited': visited, 'current': current, 'path': current_path, 'action_log': log, 'done': False}

    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                
            # XỬ LÝ CLICK CHUỘT (Chọn Start và End)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if mx < 600 and my < 600: # Chỉ click trong vùng Map
                    tx, ty = mx // tile_size, my // tile_size
                    test_rect = pygame.Rect(tx * tile_size, ty * tile_size, tile_size, tile_size)
                    if not collision_manager.is_colliding(test_rect):
                        if phase == "SELECT_START":
                            start_node = (tx, ty)
                            phase = "SELECT_TARGET"
                        elif phase == "SELECT_TARGET":
                            target_node = (tx, ty)
                            phase = "DEBUGGING"
                            state_history.append(get_initial_state())

            # XỬ LÝ PHÍM BẤM
            if event.type == pygame.KEYDOWN:
                if phase == "DEBUGGING":
                    # BẤM C: Tới 1 bước (Continue)
                    if event.key == pygame.K_c:
                        current_state = state_history[-1]
                        if not current_state['done']:
                            next_state = step_forward(current_state)
                            state_history.append(next_state)
                    # BẤM R: Lùi 1 bước (Reverse/Undo)
                    elif event.key == pygame.K_r:
                        if len(state_history) > 1:
                            state_history.pop()

        # --- KHÂU RENDER ---
        screen.fill((30, 30, 30))
        
        # VẼ MÊ CUNG VÀ LƯỚI TỌA ĐỘ BÊN TRÁI (0 - 600px)
        # Vẽ tường và vật cản
        for wall in collision_manager.walls:
            pygame.draw.rect(screen, (0, 70, 120), wall)
        for deco in collision_manager.decorations:
            pygame.draw.rect(screen, (0, 100, 50), deco)
            
        # Vẽ lưới (Grid lines) mờ mờ và Tọa độ mép
        for i in range(grid_width + 1):
            pygame.draw.line(screen, (50, 50, 50), (i * tile_size, 0), (i * tile_size, 600))
            pygame.draw.line(screen, (50, 50, 50), (0, i * tile_size), (600, i * tile_size))
            if i < grid_width:
                # Đánh số tọa độ ở mép trên và mép trái
                num_text = small_font.render(str(i), True, (150, 150, 150))
                screen.blit(num_text, (i * tile_size + 2, 2))
                screen.blit(num_text, (2, i * tile_size + 2))

        # VẼ TRẠNG THÁI DFS LÊN LƯỚI
        if start_node:
            pygame.draw.rect(screen, (0, 255, 0), (start_node[0]*tile_size, start_node[1]*tile_size, tile_size, tile_size))
        if target_node:
            pygame.draw.rect(screen, (255, 0, 0), (target_node[0]*tile_size, target_node[1]*tile_size, tile_size, tile_size))

        if state_history:
            current_state = state_history[-1]
            
            # Vẽ các ô đã Visited (màu vàng nhạt)
            for vx, vy in current_state['visited']:
                s = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                s.fill((255, 255, 0, 60))
                screen.blit(s, (vx*tile_size, vy*tile_size))
                
            # Vẽ đường đi hiện tại (Path)
            path = current_state['path']
            if len(path) > 1:
                points = [(px*tile_size + 10, py*tile_size + 10) for px, py in path]
                pygame.draw.lines(screen, (255, 255, 255), False, points, 3)
                
            # Vẽ điểm đang đứng (Current node)
            if current_state['current']:
                cx, cy = current_state['current']
                pygame.draw.rect(screen, (255, 0, 255), (cx*tile_size+4, cy*tile_size+4, 12, 12))

        # VẼ BẢNG ĐIỀU KHIỂN BÊN PHẢI (600 - 800px)
        pygame.draw.rect(screen, (20, 20, 20), (600, 0, 200, 600))
        pygame.draw.line(screen, (255, 255, 255), (600, 0), (600, 600), 2)
        
        texts = [
            "--- DFS DEBUGGER ---",
            f"Start: {start_node if start_node else 'Chờ Click...'}",
            f"End  : {target_node if target_node else 'Chờ Click...'}",
            "--------------------",
        ]
        
        if phase == "DEBUGGING":
            state = state_history[-1]
            texts.extend([
                f"Bước thứ: {len(state_history) - 1}",
                f"Nút hiện tại: {state['current']}",
                f"Đã duyệt: {len(state['visited'])} ô",
                f"Stack còn: {len(state['stack'])} ngã rẽ",
                "--------------------",
                "Trạng thái (Status):"
            ])
            # Tự động gập dòng (Word wrap) cho Action Log để không bị tràn
            log_words = state['action_log'].split(' ')
            log_line = ""
            for word in log_words:
                if len(log_line) + len(word) > 20:
                    texts.append(log_line)
                    log_line = word + " "
                else:
                    log_line += word + " "
            texts.append(log_line)
            texts.append("--------------------")
            
            # Liệt kê các tọa độ trong Path hiện tại
            texts.append("Đường đang đi (Path):")
            path = state['path']
            # Chỉ hiển thị 8 tọa độ gần nhất để không trôi màn hình
            for p in path[-8:]: 
                texts.append(f"-> {p}")
            if len(path) > 8:
                texts.insert(-8, "... (còn nữa)")

        texts.extend([
            "",
            "--- HƯỚNG DẪN ---",
            "1. Click chọn Bắt đầu",
            "2. Click chọn Đích đến",
            "3. Bấm 'C': Tiến 1 bước",
            "4. Bấm 'R': Lùi 1 bước"
        ])

        y_offset = 10
        for text in texts:
            if "NGÕ CỤT" in text or "BACKTRACK" in text:
                color = (255, 100, 100) # Đỏ
            elif "ĐÃ CHẠM ĐÍCH" in text:
                color = (100, 255, 100) # Xanh lá
            elif "Tới" in text or "Thêm" in text:
                color = (100, 200, 255) # Xanh dương
            else:
                color = (200, 200, 200) # Trắng xám
                
            surface = font.render(text, True, color)
            screen.blit(surface, (610, y_offset))
            y_offset += 20

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_dfs_debugger()