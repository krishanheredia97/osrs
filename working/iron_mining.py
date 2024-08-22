import asyncio
import random
import time
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View
from utils.hull_coords import get_color_coordinates
from utils.clicks import ClickHelper
from utils.capture import capture_window_info
from utils.multi import get_iron_ore_coordinates

load_dotenv()

SERVER_ID = 1271171467287068693
TUSK_TOKEN = os.getenv('TUSK_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class IronMiningBot:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.red_hex = "FF0000FF"
        self.template_path = r"C:\Users\danie\Downloads\Iron_ore.webp"

    async def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            print("Starting Iron Mining Bot...")
            await asyncio.sleep(3)
            return await self.iron_mining_automation()

    def stop(self):
        self.running = False
        print("No pasaréis")

    async def click_color_area(self, color_name, color_hex):
        window_info = capture_window_info()
        window_left, window_top = window_info['rect'][0], window_info['rect'][1]

        color_coords = get_color_coordinates({color_name: color_hex})
        if color_name in color_coords and color_coords[color_name]:
            x1, y1, x2, y2 = color_coords[color_name]
            screen_x = window_left + (x1 + x2) // 2
            screen_y = window_top + (y1 + y2) // 2

            ClickHelper.move_mouse(screen_x, screen_y)
            await asyncio.sleep(0.1)
            await ClickHelper.left_click()

    async def click_iron_ore_instances(self, template_path, min_delay=0.3, max_delay=0.6):
        window_info = capture_window_info()
        window_left, window_top = window_info['rect'][0], window_info['rect'][1]

        coords = get_iron_ore_coordinates(template_path)

        for coord in coords:
            if not self.running:
                break

            screen_x1 = window_left + coord[0]
            screen_y1 = window_top + coord[1]
            screen_x2 = window_left + coord[2]
            screen_y2 = window_top + coord[3]

            click_x = random.randint(screen_x1, screen_x2)
            click_y = random.randint(screen_y1, screen_y2)

            ClickHelper.move_mouse(click_x, click_y)
            await asyncio.sleep(0.1)
            await ClickHelper.shift_left_click()

            await ClickHelper.random_delay(min_delay, max_delay)

        print(f"Clicked on {len(coords)} iron ore instances.")

    async def iron_mining_automation(self):
        start_time = time.time()
        end_time = start_time + 60 * 180  # 180 minutes in seconds

        while time.time() < end_time and self.running:
            # Loop 27 times
            for _ in range(27):
                if not self.running:
                    break
                await self.click_color_area("red", self.red_hex)
                await ClickHelper.random_delay(1.5, 1.8)

            # Click iron ore instances
            await self.click_iron_ore_instances(self.template_path, 0.1, 0.15)

            # Optional: Add a short delay between cycles
            await asyncio.sleep(random.uniform(1, 3))

            elapsed_time = time.time() - start_time
            print(f"Elapsed time: {elapsed_time / 60:.2f} minutes")

        if not self.running:
            return "Iron Mining Bot has been stopped."
        else:
            return "180-minute automation completed."

iron_bot = IronMiningBot()

class StopButton(Button):
    def __init__(self, bot_instance):
        super().__init__(label="Stop", style=ButtonStyle.danger)
        self.bot_instance = bot_instance

    async def callback(self, interaction: discord.Interaction):
        if self.bot_instance.running:
            self.bot_instance.stop()
            await interaction.response.send_message("Iron Mining Bot has been stopped.")
        else:
            await interaction.response.send_message("Bot is not currently running!")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='iron')
async def iron_command(ctx):
    if ctx.guild.id != SERVER_ID:
        return

    if iron_bot.running:
        await ctx.send("Bot is already running!")
        return

    view = View()
    stop_button = StopButton(iron_bot)
    view.add_item(stop_button)

    await ctx.send("Starting Iron Mining Bot", view=view)
    result = await iron_bot.start()
    await ctx.send(result)

if __name__ == "__main__":
    bot.run(TUSK_TOKEN)