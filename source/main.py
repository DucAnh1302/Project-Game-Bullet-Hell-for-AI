import asyncio
from presentation.game_loop import GameLoop

async def main():
    game = GameLoop()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())