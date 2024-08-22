import asyncio
import random
import time
from utils.hull_coords import get_color_coordinates as get_hull_coords
from utils.color_coords import get_color_coordinates as get_color_coords
from utils.capture import capture_window_info
from utils.clicks import ClickHelper

class ColorClickingBot:
    def __init__(self):
        self.running = False
        self.click_helper = ClickHelper()
        self.window_info = None
        self.hull_color_dict = {"cyan": "FF00FFFF"}
        self.color_dict = {
            "green": "FF26FF00",
            "orange": "FFFF7300",
            "pink": "FFFF00CA",
            "blue": "FF0000FF",
            "red": "FFFF0000",
            "cyan": "FF00FFFF"
        }

    async def start(self, duration=7200):  # 7200 seconds = 2 hours
        if not self.running:
            self.running = True
            print(f"Starting bot for {duration} seconds")
            await asyncio.sleep(3)
            return await self.run_bot(duration)

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def window_to_screen_coords(self, x, y):
        if self.window_info:
            win_x, win_y, _, _ = self.window_info['rect']
            return x + win_x, y + win_y
        return x, y

    async def click_color(self, color_coords, color_name):
        if color_coords and color_name in color_coords:
            coords = color_coords[color_name]
            if coords:
                x = random.randint(coords[0], coords[2])
                y = random.randint(coords[1], coords[3])
                screen_x, screen_y = self.window_to_screen_coords(x, y)
                await self.click_helper.click_at_coords(screen_x, screen_y)
                print(f"Clicked on {color_name}")
            else:
                print(f"Could not find coordinates for {color_name}")
        else:
            print(f"Color coordinates not available for {color_name}")

    async def random_sleep(self, base_time):
        sleep_time = random.uniform(base_time, base_time * 2)
        await asyncio.sleep(sleep_time)

    async def run_bot(self, duration):
        try:
            self.window_info = capture_window_info()
            start_time = time.time()
            iteration = 0

            while self.running and (time.time() - start_time) < duration:
                iteration += 1
                print(f"Starting iteration {iteration}")

                # 1. Click on cyan (hull coords)
                hull_coords = get_hull_coords(self.hull_color_dict)
                await self.click_color(hull_coords, "cyan")
                await self.random_sleep(1)

                # Get color coordinates for the rest of the actions
                color_coords = get_color_coords(self.color_dict)

                # 3-4. Click on green and wait
                await self.click_color(color_coords, "green")
                await self.random_sleep(0.5)

                # 5-6. Click on orange and wait
                await self.click_color(color_coords, "orange")
                await self.random_sleep(0.2)

                # 7-8. Click on pink and wait
                await self.click_color(color_coords, "pink")
                await self.random_sleep(0.2)

                # 9. Press ESC key
                await self.click_helper.press_key(0x1B)  # 0x1B is the virtual key code for ESC
                print("Pressed ESC key")
                await self.random_sleep(0.1)

                # 10-11. Click on blue and wait
                await self.click_color(color_coords, "blue")
                await self.random_sleep(0.2)

                # 12-13. Click on red and wait
                await self.click_color(color_coords, "red")
                await self.random_sleep(0.8)

                # 14. Press SPACE key
                await self.click_helper.press_key(0x20)  # 0x20 is the virtual key code for SPACE
                print("Pressed SPACE key")

                # 15. Wait 17 seconds (randomized)
                await self.random_sleep(17)

            elapsed_time = time.time() - start_time
            print(f"Bot finished after {elapsed_time:.2f} seconds. Total iterations: {iteration}")
            self.stop()
            return f"Bot completed its run. Total iterations: {iteration}, Elapsed time: {elapsed_time:.2f} seconds"

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            self.stop()
            return f"An error occurred: {str(e)}"

# Example usage
async def main():
    bot = ColorClickingBot()
    result = await bot.start(duration=7200)  # Run for 2 hours (7200 seconds)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())