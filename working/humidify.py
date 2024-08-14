import asyncio
import time
import random
import win32gui
import win32api
import win32con
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from utils.capture import capture_window_info
from utils.color_coords import get_color_coordinates

load_dotenv()

SERVER_ID = 1271171467287068693  # Replace with your server ID
BOT_TOKEN = os.getenv('TUSK_TOKEN')  # Make sure to set this in your .env file

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class HumidifyBot:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.loop_count = 0
        self.max_loops = 0

        self.color_dict = {
            "orange": "FFFF7300",
            "red": "FFFF0000"
        }

        self.window_info = None
        self.color_coords = None

    async def start(self, loop_count):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.loop_count = 0
            self.max_loops = loop_count
            print(f"Starting bot with {self.max_loops} loops")
            await asyncio.sleep(3)
            return await self.run_bot()

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def get_random_point_in_square(self, x1, y1, x2, y2):
        return (
            random.randint(x1, x2),
            random.randint(y1, y2)
        )

    def move_mouse_to_window_coords(self, x, y):
        screen_x, screen_y = win32gui.ClientToScreen(self.window_info['handle'], (x, y))
        win32api.SetCursorPos((screen_x, screen_y))
        time.sleep(0.3)

    async def click_at_window_coords(self, x, y, action_name):
        self.move_mouse_to_window_coords(x, y)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print(f"{action_name} at window coordinates ({x}, {y})")

    async def perform_action(self, coords, action_name):
        if coords:
            x, y = self.get_random_point_in_square(*coords)
            await self.click_at_window_coords(x, y, action_name)
        else:
            print(f"Could not find coordinates for {action_name}")

    async def bot_loop(self):
        orange_coords = self.color_coords['orange']
        red_coords = self.color_coords['red']

        if not orange_coords or not red_coords:
            print("Could not find required color coordinates. Stopping bot.")
            self.stop()
            return

        original_mouse_pos = win32gui.GetCursorPos()

        # Open bank
        await self.perform_action(orange_coords, "Opening bank")
        await asyncio.sleep(2)

        # Bank items
        await self.perform_action(red_coords, "Banking items")
        await asyncio.sleep(1)

        # Get items
        await self.perform_action(orange_coords, "Getting items")
        await asyncio.sleep(0.2)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

        await asyncio.sleep(0.4)

        # Close bank
        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("Closed bank")
        await asyncio.sleep(1)

        # Cast spell
        await self.perform_action(red_coords, "Casting spell")
        await asyncio.sleep(random.uniform(3.5, 5))

        win32api.SetCursorPos(original_mouse_pos)
        print("Returned mouse to original position")

    async def run_bot(self):
        try:
            self.window_info = capture_window_info()
            self.color_coords = get_color_coordinates(self.color_dict)

            while self.running and self.loop_count < self.max_loops:
                await self.bot_loop()
                self.loop_count += 1
                print(f"Completed loop {self.loop_count}/{self.max_loops}")

                if self.loop_count >= self.max_loops:
                    break

            if not self.running:
                print("Bot stopped.")
            else:
                print(f"Completed all {self.max_loops} loops. Stopping bot.")

            self.stop()
            return f"Bot finished its run. Total loops completed: {self.loop_count}"

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            self.stop()
            return f"An error occurred: {str(e)}"

humidify_bot = HumidifyBot()

class StopButton(Button):
    def __init__(self, bot_instance):
        super().__init__(label="Stop Humidify", style=ButtonStyle.danger)
        self.bot_instance = bot_instance

    async def callback(self, interaction: discord.Interaction):
        if self.bot_instance.running:
            self.bot_instance.stop()
            await interaction.response.send_message("Humidify Bot has been stopped.")
        else:
            await interaction.response.send_message("Bot is not currently running!")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='hum')
async def humidify_command(ctx, casts: int = 200):
    if ctx.guild.id != SERVER_ID:
        return

    if humidify_bot.running:
        await ctx.send("Bot is already running!")
        return

    loops = casts // 27
    view = View()
    stop_button = StopButton(humidify_bot)
    view.add_item(stop_button)

    await ctx.send(f"Starting Humidify Bot with {loops} loops (based on {casts} casts)", view=view)
    result = await humidify_bot.start(loops)
    await ctx.send(result)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)