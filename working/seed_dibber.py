import asyncio
import time
import random
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

SERVER_ID = 1271171467287068693
TUSK_TOKEN = os.getenv('TUSK_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


class SeedDibberBot:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.actions_performed = 0
        self.action_limit = 200

        self.color_dict = {
            "green": "FF00FF00",
            "pink": "FFFF00CA",
            "blue": "FF001DFF"
        }

        self.color_coords = None
        self.window_info = None

    async def start(self, action_limit=None):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.actions_performed = 0
            if action_limit is not None:
                self.action_limit = action_limit
            print(f"Starting bot with action limit: {self.action_limit}")
            await asyncio.sleep(3)
            return await self.run_bot()

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def window_to_screen_coords(self, x, y):
        if self.window_info:
            win_x, win_y, _, _ = self.window_info['rect']
            return x + win_x, y + win_y
        return x, y

    async def perform_action(self, color, action_name):
        if self.color_coords and color in self.color_coords:
            coords = self.color_coords[color]
            if coords:
                x = random.randint(coords[0], coords[2])
                y = random.randint(coords[1], coords[3])
                screen_x, screen_y = self.window_to_screen_coords(x, y)
                await self.click_at_coords(screen_x, screen_y)
                if color in ["green", "blue"]:
                    print(f"Clicked on {color}")  # Simplified print statement
            else:
                print(f"Could not find coordinates for {color}")
        else:
            print(f"Color coordinates not available for {color}")

    async def click_at_coords(self, x, y):
        win32api.SetCursorPos((x, y))
        await asyncio.sleep(random.uniform(0.1, 0.155))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(random.uniform(0.01, 0.025))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    async def press_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        await asyncio.sleep(random.uniform(0.05, 0.1))
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    async def run_bot(self):
        try:
            self.window_info = capture_window_info()
            self.color_coords = get_color_coordinates(self.color_dict)

            while self.running and self.actions_performed < self.action_limit:
                # 1. Click on pink
                await self.perform_action("pink", "Clicking on pink")
                # 2. Wait 1 second
                await asyncio.sleep(1)

                # 3. Click on blue
                await self.perform_action("blue", "Clicking on blue")
                # 4. Wait 0.6 seconds
                await asyncio.sleep(0.6)

                # 5. Click on pink
                await self.perform_action("pink", "Clicking on pink")
                # 6. Wait 0.5 seconds
                await asyncio.sleep(0.5)

                # 7. Press "esc" key
                await self.press_key(win32con.VK_ESCAPE)
                print("Pressed ESC key")

                # 8. Loop (26x)
                for _ in range(26):
                    # 1. Click on green
                    await self.perform_action("green", "Clicking on green")
                    # 2. Wait 0.3 seconds
                    await asyncio.sleep(0.3)
                    # 3. Click on blue
                    await self.perform_action("blue", "Clicking on blue")
                    # 4. Wait 0.3 seconds
                    await asyncio.sleep(0.3)
                    self.actions_performed += 1
                    print(f"Actions performed: {self.actions_performed}")

                    if self.actions_performed >= self.action_limit:
                        break

            if not self.running:
                print("Bot stopped.")
            else:
                print(f"Action limit of {self.action_limit} reached. Stopping bot.")

            self.stop()
            return f"Bot finished its run. Total actions performed: {self.actions_performed}"

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            self.stop()
            return f"An error occurred: {str(e)}"


dibber_bot = SeedDibberBot()


class StopButton(Button):
    def __init__(self, bot_instance):
        super().__init__(label="Stop Dibber", style=ButtonStyle.danger)
        self.bot_instance = bot_instance

    async def callback(self, interaction: discord.Interaction):
        if self.bot_instance.running:
            self.bot_instance.stop()
            await interaction.response.send_message("Seed Dibber Bot has been stopped.")

            # Purge all messages in the channel
            await interaction.channel.purge()
        else:
            await interaction.response.send_message("Bot is not currently running!")


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(name='dib')
async def dib_command(ctx, action_limit: int = 200):
    if ctx.guild.id != SERVER_ID:
        return

    if dibber_bot.running:
        await ctx.send("Bot is already running!")
        return

    view = View()
    stop_button = StopButton(dibber_bot)
    view.add_item(stop_button)

    await ctx.send(f"Starting Seed Dibber Bot with action limit: {action_limit}", view=view)
    result = await dibber_bot.start(action_limit)
    await ctx.send(result)


if __name__ == "__main__":
    bot.run(TUSK_TOKEN)
