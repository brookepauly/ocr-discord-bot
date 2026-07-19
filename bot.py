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


@client.tree.command(name = "Export", description = "")



# run the bot
client.run(os.environ.get("DISCORD_TOKEN"))