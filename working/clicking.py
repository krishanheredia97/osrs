import asyncio
import time
import random
import pyautogui
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import Button, View

load_dotenv()

SERVER_ID = 1271171467287068693  # Replace with your server ID
BOT_TOKEN = os.getenv('TUSK_TOKEN')  # Make sure to set this in your .env file

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class AutoClickerBot:
    def __init__(self):
        self.clicking = False
        self.click_task = None

    async def start_clicking(self):
        self.clicking = True
        while self.clicking:
            pyautogui.click(pyautogui.position())
            await asyncio.sleep(random.uniform(0.2, 0.4))

    def stop_clicking(self):
        self.clicking = False
        if self.click_task:
            self.click_task.cancel()

clicker_bot = AutoClickerBot()

class ClickerButtons(View):
    def __init__(self, bot_instance):
        super().__init__(timeout=None)
        self.bot_instance = bot_instance

    @discord.ui.button(label="Run", style=ButtonStyle.green)
    async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.bot_instance.clicking:
            self.bot_instance.clicking = True
            self.bot_instance.click_task = asyncio.create_task(self.bot_instance.start_clicking())
            await interaction.response.send_message("Auto-Clicker started!", ephemeral=True)
        else:
            await interaction.response.send_message("Auto-Clicker is already running!", ephemeral=True)
        await self.refresh_buttons(interaction)

    @discord.ui.button(label="Stop", style=ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot_instance.clicking:
            self.bot_instance.stop_clicking()
            await interaction.response.send_message("Auto-Clicker stopped!", ephemeral=True)
        else:
            await interaction.response.send_message("Auto-Clicker is not running!", ephemeral=True)
        await self.refresh_buttons(interaction)

    async def refresh_buttons(self, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.channel.send("Auto-Clicker Controls:", view=self)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='click')
async def click_command(ctx):
    if ctx.guild.id != SERVER_ID:
        return

    view = ClickerButtons(clicker_bot)
    await ctx.send("Auto-Clicker Controls:", view=view)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)