import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

load_dotenv()

# checks bot is connected
class Client(commands.Bot):
    async def on_ready(self):
        print(f' Logged on as {self.user}!')

# allowing bot access to specific discord functions
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix= "!", intents = intents)

GUILD = discord.Object(id = os.environ.get("GUILD_ID")
@client.tree.command(name = "scan", description = "Scan zip file and export", guild = GUILD)
async def exportFile(interaction: discord.interaction):
    await interaction.response.send_message("Scan Please!")

# run the bot
client.run(os.environ.get("DISCORD_TOKEN"))