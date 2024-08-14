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

    color_dict = {
        "blue": "FF0000FF",
        "orange": "FFFF7300",
        "green": "FF26FF00",
        "pink": "FFFF00CA",
        "red": "FFFF0000"
    }

    start_time = asyncio.get_event_loop().time()
    duration = 60 * 60  # 60 minutes

    while asyncio.get_event_loop().time() - start_time < duration:
        try:
            # 1. Click on blue (Teleport POH)
            print("Teleport POH")
            await click_color("blue", color_dict, window_handle)

            # 2. Press F2 key (Close spells)
            print("Close spells")
            await ClickHelper.press_key(win32con.VK_F2)

            # 3. Wait 4-5 seconds
            await ClickHelper.random_delay(4, 5)

            # 4. Click on orange (Restore stats)
            print("Restore stats")
            await click_color("orange", color_dict, window_handle, use_hull=True)

            # 5. Wait 4-5 seconds
            await ClickHelper.random_delay(4, 5)

            # 6. Click on green (Teleport to Lunar Isle)
            print("Teleport to Lunar Isle")
            await click_color("green", color_dict, window_handle, use_hull=True)

            # 7. Wait 4-7 seconds
            await ClickHelper.random_delay(4, 7)

            # 8. Click on green (Click on bank)
            print("Click on bank")
            await click_color("green", color_dict, window_handle, use_hull=True)

            # 9. Wait 6-8 seconds
            await ClickHelper.random_delay(6, 8)

            # 10. Click on pink (Withdraw pure essence)
            print("Withdraw pure essence")
            await click_color("pink", color_dict, window_handle)

            # 11. Wait 0.2-0.4 seconds
            await ClickHelper.random_delay(0.2, 0.4)

            # 12. Press escape key (Close bank)
            print("Close bank")
            await ClickHelper.press_key(win32con.VK_ESCAPE)

            # 13. Click on red (Go to altar)
            print("Go to altar")
            await click_color("red", color_dict, window_handle)

            # 14. Wait 15-20 seconds
            await ClickHelper.random_delay(28, 33)

            # 15. Click on green (Click on altar)
            print("Click on altar")
            await click_color("green", color_dict, window_handle, use_hull=True)

            # 16. Wait 15-20 seconds
            await ClickHelper.random_delay(5, 7)

            # 17. Press F2 key (Open spells)
            print("Open spells")
            await ClickHelper.press_key(win32con.VK_F2)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

async def main():
    try:
        await run_workflow()
    except KeyboardInterrupt:
        print("Script terminated by user")

if __name__ == "__main__":
    asyncio.run(main())