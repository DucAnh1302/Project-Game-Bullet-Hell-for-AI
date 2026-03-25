# source/presentation/ui_manager.py
import pygame
import os

class UIManager:
    """
    Quản lý toàn bộ Giao diện Người dùng (UI).
    Tách biệt logic vẽ chữ, vẽ nút bấm, màn hình thông báo ra khỏi GameLoop.
    """
    def __init__(self, screen_width, screen_height, assets_path):
        self.width = screen_width
        self.height = screen_height
        
        # Setup sẵn các Font chữ dùng chung
        #self.font_hud = pygame.font.SysFont('Times New Roman', 36)
        #self.font_title = pygame.font.SysFont('Times New Roman', 80, bold=True)
        #self.font_info = pygame.font.SysFont('Times New Roman', 30)

        self.font_hud = pygame.font.Font(None, 36)
        self.font_title = pygame.font.Font(None, 80)
        self.font_title.set_bold(True)
        self.font_info = pygame.font.Font(None, 30)
        
        # Tải hình ảnh nút bấm
        btn_path = os.path.join(assets_path, 'Buttons', 'playButton.png')
        try:
            self.play_btn_img = pygame.image.load(btn_path).convert_alpha()
            self.play_btn_img = pygame.transform.scale(self.play_btn_img, (150, 50))
        except:
            self.play_btn_img = pygame.Surface((150, 50))
            self.play_btn_img.fill((100, 100, 100))
            
        self.btn_rect = self.play_btn_img.get_rect()

    def draw_hud(self, screen, player_health, elapsed_time, best_time):
        """Vẽ thanh máu và đồng hồ trên cùng màn hình lúc đang chơi"""
        # Vẽ Máu
        health_text = f"HP: {player_health}/100"
        text_surface = self.font_hud.render(health_text, True, (255, 50, 50))
        screen.blit(text_surface, (10, 10))
        
        # Vẽ Đồng hồ
        if best_time == float('inf'):
            time_text = f"Time: {elapsed_time:.1f}s | Best: --"
        else:
            time_text = f"Time: {elapsed_time:.1f}s | Best: {best_time:.1f}s"
            
        time_surface = self.font_hud.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, (self.width - time_surface.get_width() - 20, 10))

    def draw_overlay_screen(self, screen, state, elapsed_time=0):
        """Vẽ các màn hình chờ: START, GAME_OVER, WIN"""
        # Tấm kính mờ phủ lên game
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Xác định nội dung theo trạng thái
        if state == "START":
            title_text = self.font_title.render("BULLET HELL", True, (0, 255, 255))
            msg_text = self.font_info.render("Dung WASD de ne dan va tim Cua Thoat Hiem!", True, (200, 200, 200))
        elif state == "GAME_OVER":
            title_text = self.font_title.render("GAME OVER", True, (255, 50, 50))
            msg_text = self.font_info.render("Ban da bi dan ma thuat ban ha!", True, (200, 200, 200))
        elif state == "WIN":
            title_text = self.font_title.render("YOU WIN!", True, (50, 255, 50))
            msg_text = self.font_info.render(f"Thoi gian thoat: {elapsed_time:.2f}s", True, (200, 200, 200))

        inst_text = self.font_info.render("Hoac nhan [ESC] de thoat", True, (150, 150, 150))

        # Căn chỉnh Y
        title_y = self.height // 2 - 120
        msg_y = self.height // 2 - 40
        btn_y = self.height // 2 + 40
        inst_y = self.height // 2 + 110

        # In lên màn hình
        screen.blit(title_text, (self.width//2 - title_text.get_width()//2, title_y))
        screen.blit(msg_text, (self.width//2 - msg_text.get_width()//2, msg_y))
        
        # Cập nhật tọa độ nút và in nút
        self.btn_rect.centerx = self.width // 2
        self.btn_rect.centery = btn_y
        screen.blit(self.play_btn_img, self.btn_rect)

        screen.blit(inst_text, (self.width//2 - inst_text.get_width()//2, inst_y))