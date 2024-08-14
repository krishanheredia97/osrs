import os
import asyncio
import time
import random
import discord
from discord.ext import commands
import win32gui
import win32ui
import win32con
import win32process
import win32api
import numpy as np
import cv2
import io
from utils.window_handle import get_runelite_handle
from utils.color_coords import get_color_coordinates

# Discord bot setup
TOKEN = os.getenv('ARMINIO_TOKEN')
SERVER_ID = 1238187583734022246
CHANNEL_ID = 1263530192098427032

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


class GameBot:
    def __init__(self):
        self.last_activity = time.time()
        self.color_dict = {
            "green": "FF00FF00",
            "pink": "FFFF00CA"
        }
        self.color_coords = None
        self.window_info = None
        self.window_handle = None

    async def initialize(self):
        self.window_handle = get_runelite_handle()
        if not self.window_handle:
            raise Exception("Failed to get RuneLite window handle")
        self.window_info = win32gui.GetWindowRect(self.window_handle)
        self.color_coords = get_color_coordinates(self.color_dict)

    def window_to_screen_coords(self, x, y):
        win_x, win_y, _, _ = self.window_info
        return x + win_x, y + win_y

    async def perform_action(self, color):
        if color in self.color_coords:
            coords = self.color_coords[color]
            if coords:
                x = random.randint(coords[0], coords[2])
                y = random.randint(coords[1], coords[3])
                screen_x, screen_y = self.window_to_screen_coords(x, y)
                win32api.SetCursorPos((screen_x, screen_y))
                time.sleep(random.uniform(0.1, 0.155))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(random.uniform(0.01, 0.025))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print(f"Clicked {color} at window coordinates ({x}, {y}), screen coordinates ({screen_x}, {screen_y})")
                self.last_activity = time.time()
            else:
                print(f"Could not find coordinates for {color}")
        else:
            print(f"Color coordinates not available for {color}")

    async def check_activity(self):
        while True:
            current_time = time.time()
            if current_time - self.last_activity >= 600:  # 10 minutes
                await self.perform_action("green")
                await asyncio.sleep(1)
                await self.perform_action("green")
            await asyncio.sleep(1)  # Check every second


game_bot = GameBot()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    channel = bot.get_channel(CHANNEL_ID)
    await send_buttons(channel)

    try:
        await game_bot.initialize()
        bot.loop.create_task(game_bot.check_activity())
    except Exception as e:
        await channel.send(f"Error initializing game bot: {str(e)}")


async def send_buttons(channel):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Take Screenshot", custom_id="screenshot", style=discord.ButtonStyle.primary))
    view.add_item(discord.ui.Button(label="Shutdown Game", custom_id="shutdown", style=discord.ButtonStyle.danger))
    view.add_item(discord.ui.Button(label="Pink", custom_id="pink", style=discord.ButtonStyle.secondary))
    view.add_item(discord.ui.Button(label="Green", custom_id="green", style=discord.ButtonStyle.success))
    await channel.send("Runescape Bot Monitor", view=view)


@bot.tree.command(name="setup", description="Setup the monitor buttons")
async def setup(interaction: discord.Interaction):
    await send_buttons(interaction.channel)
    await interaction.response.send_message("Monitor buttons have been set up!", ephemeral=True)


def take_screenshot(handle):
    # Get the window's device context (DC)
    hwndDC = win32gui.GetWindowDC(handle)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Get the window's dimensions
    left, top, right, bot = win32gui.GetWindowRect(handle)
    width = right - left
    height = bot - top

    # Create a bitmap object
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # BitBlt (copy) the entire window's DC to the memory DC
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Create a compatible OpenCV image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    screenshot = np.frombuffer(bmpstr, dtype='uint8')
    screenshot.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

    # Remove the alpha channel (if present)
    screenshot = screenshot[..., :3]

    # Convert to PNG
    _, png_data = cv2.imencode('.png', screenshot)
    png_file = io.BytesIO(png_data.tobytes())

    # Clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(handle, hwndDC)

    return png_file


def shutdown_game(handle):
    try:
        # Get the process ID
        _, pid = win32process.GetWindowThreadProcessId(handle)

        # Open the process with termination privileges
        process_handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)

        # Terminate the process
        win32api.TerminateProcess(process_handle, 1)
        win32api.CloseHandle(process_handle)

        print(f"Game with PID {pid} has been terminated.")
        return True
    except Exception as e:
        print(f"Failed to terminate game: {e}")
        return False


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'] == 'screenshot':
            if game_bot.window_handle:
                screenshot = take_screenshot(game_bot.window_handle)
                file = discord.File(fp=screenshot, filename="screenshot.png")
                await interaction.response.send_message(file=file)
                await send_buttons(interaction.channel)
            else:
                await interaction.response.send_message("Failed to get Runescape window handle.", ephemeral=True)
        elif interaction.data['custom_id'] == 'shutdown':
            if game_bot.window_handle:
                if shutdown_game(game_bot.window_handle):
                    await interaction.response.send_message("RuneLite client has been forcefully closed.",
                                                            ephemeral=True)
                else:
                    await interaction.response.send_message("Failed to close RuneLite client.", ephemeral=True)
            else:
                await interaction.response.send_message("Failed to get Runescape window handle.", ephemeral=True)
        elif interaction.data['custom_id'] in ['pink', 'green']:
            color = interaction.data['custom_id']
            await game_bot.perform_action(color)
            await interaction.response.send_message(f"Clicked {color} button", ephemeral=True)
            await send_buttons(interaction.channel)


if __name__ == "__main__":
    bot.run(TOKEN)