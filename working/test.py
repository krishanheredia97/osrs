import asyncio
import time
from utils.clicks import ClickHelper
from utils.hull_coords import get_color_coordinates as get_hull_coordinates
from utils.color_coords import get_color_coordinates
from utils.capture import capture_window_info
import win32gui


async def get_color_center_coords(color, color_dict, window_handle, use_hull=True):
    coords_func = get_hull_coordinates if use_hull else get_color_coordinates
    coords = coords_func(color_dict)
    if color not in coords or coords[color] is None:
        print(f"Error: Could not find coordinates for {color}")
        return None

    coord = coords[color]
    center_x = (coord[0] + coord[2]) // 2
    center_y = (coord[1] + coord[3]) // 2
    return win32gui.ClientToScreen(window_handle, (center_x, center_y))


async def click_color(color, color_dict, window_handle, use_hull=True):
    coords = await get_color_center_coords(color, color_dict, window_handle, use_hull)
    if coords:
        print(f"Clicking on {color}")
        await ClickHelper.click_at_coords(*coords)
    else:
        print(f"Failed to click on {color}: coordinates not found")


async def run_sequence(window_handle, color_dict):
    # 1. Click once on orange
    await asyncio.sleep(5)
    await click_color("orange", color_dict, window_handle)

    # 2. Wait 5 seconds
    print("Waiting 5 seconds")
    await asyncio.sleep(5)

    # 3. Click on green
    await click_color("green", color_dict, window_handle)

    # 4. Wait 5 seconds
    print("Waiting 5 seconds")
    await asyncio.sleep(5)

    # 5. Click on green again
    await click_color("green", color_dict, window_handle)

    print("Reached Temple")

    # Loop to click green hull every 60 seconds for 10 minutes
    start_time = time.time()
    while time.time() - start_time < 600:  # 600 seconds = 10 minutes
        print("Waiting 60 seconds before next green hull click")
        await asyncio.sleep(60)
        await click_color("green", color_dict, window_handle)

    # After 10 minutes, click on blue
    print("10 minutes passed. Clicking on blue.")
    await click_color("blue", color_dict, window_handle, use_hull=False)


async def main():
    # Capture window info
    window_info = capture_window_info()
    window_handle = window_info['handle']

    # Define color dictionary with updated green hull color and blue color
    color_dict = {
        "green": "FF26FF00",
        "orange": "FFFF7300",
        "blue": "FF0000FF"
    }

    try:
        while True:
            await run_sequence(window_handle, color_dict)
            print("Restarting sequence")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    except KeyboardInterrupt:
        print("Script terminated by user")


if __name__ == "__main__":
    asyncio.run(main())