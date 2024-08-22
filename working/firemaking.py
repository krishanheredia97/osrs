import asyncio
import win32con
from utils.clicks import ClickHelper
from utils.color_coords import get_color_coordinates
from utils.hull_coords import get_color_coordinates as get_hull_coordinates
from utils.capture import capture_window_info

async def get_color_center_coords(color, color_dict, window_handle, use_hull=False):
    coords_func = get_hull_coordinates if use_hull else get_color_coordinates
    coords = coords_func(color_dict)
    if color not in coords or coords[color] is None:
        print(f"Error: Could not find coordinates for {color}")
        return None

    coord = coords[color]
    center_x = (coord[0] + coord[2]) // 2
    center_y = (coord[1] + coord[3]) // 2
    return ClickHelper.window_to_screen_coords(window_handle, center_x, center_y)

async def click_color(color, color_dict, window_handle, use_hull=False):
    coords = await get_color_center_coords(color, color_dict, window_handle, use_hull)
    if coords:
        await ClickHelper.click_at_coords(*coords)
    else:
        print(f"Failed to click on {color}: coordinates not found")

async def run_workflow():
    window_info = capture_window_info()
    window_handle = window_info['handle']

    hull_color_dict = {
        "blue": "FF0000FF",
        "green": "FF26FF00"
    }

    square_color_dict = {
        "pink": "FFFF00CA"
    }

    start_time = asyncio.get_event_loop().time()
    duration = 60 * 60  # 60 minutes

    while asyncio.get_event_loop().time() - start_time < duration:
        try:
            # 1. Click on blue (open bank)
            print("Opening bank")
            await click_color("blue", hull_color_dict, window_handle, use_hull=True)

            # 2. Wait 1 second
            await asyncio.sleep(1)

            # 3. Click on pink (withdraw logs)
            print("Withdrawing logs")
            await click_color("pink", square_color_dict, window_handle)

            # 4. Wait 1 second
            await asyncio.sleep(1)

            # 5. Press 'escape' key (exit bank)
            print("Exiting bank")
            await ClickHelper.press_key(win32con.VK_ESCAPE)

            # 6. Click on green (click on fire)
            print("Clicking on fire")
            await click_color("green", hull_color_dict, window_handle, use_hull=True)
            await asyncio.sleep(1)

            # 7. Press 'space' key (burn logs)
            print("Burning logs")
            await ClickHelper.press_key(win32con.VK_SPACE)

            # 8. Wait 60 seconds
            await asyncio.sleep(60)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

async def main():
    try:
        await run_workflow()
    except KeyboardInterrupt:
        print("Script terminated by user")

if __name__ == "__main__":
    asyncio.run(main())