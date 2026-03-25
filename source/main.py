import asyncio
import os
import sys
#Thêm vào để bên máy Ngân chạy được không báo lỗi
# Đảm bảo đầu ra console Windows dùng UTF-8 để không lỗi UnicodeEncodeError với tiếng Việt
if os.name == 'nt':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    # Python cũ không có reconfigure; bỏ qua
    pass

from presentation.game_loop import GameLoop

async def main():
    game = GameLoop()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())