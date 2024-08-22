import asyncio
from utils.hull_coords import get_color_coordinates
from utils.capture import capture_window_info
from utils.clicks import ClickHelper
from utils.window_handle import get_runelite_handle


async def find_and_click_red_square():
    # Define color dictionary
    color_dict = {
        'red': '#FF0000'
    }

    # Capture window info
    window_info = capture_window_info()
    window_handle = window_info['handle']

    # Get color coordinates
    color_coords = get_color_coordinates(color_dict)

    # Check if red square is found
    if 'red' in color_coords and color_coords['red']:
        red_coords = color_coords['red']

        # Calculate the center of the red square
        center_x = (red_coords[0] + red_coords[2]) // 2
        center_y = (red_coords[1] + red_coords[3]) // 2

        # Convert window coordinates to screen coordinates
        screen_x, screen_y = ClickHelper.window_to_screen_coords(window_handle, center_x, center_y)

        # Move mouse and click
        ClickHelper.move_mouse(screen_x, screen_y)
        await asyncio.sleep(0.1)  # Small delay after moving mouse
        await ClickHelper.left_click()
        print(f"Clicked at screen coordinates: ({screen_x}, {screen_y})")
        return True
    else:
        print("No red square detected")

    return False


async def main():
    clicked = await find_and_click_red_square()
    if not clicked:
        print("Failed to find and click the red square")


if __name__ == "__main__":
    asyncio.run(main())