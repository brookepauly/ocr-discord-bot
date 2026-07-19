import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from typing import Literal
from google import genai
from google.genai import types

load_dotenv()

# checks bot is connected
class Client(commands.Bot):
    async def on_ready(self):
        print(f' Logged on as {self.user}!')

        try:
            guild = discord.Object(id = int(os.environ.get("GUILD_ID")))
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands: {e}')


# allowing bot access to specific discord functions
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix= "!", intents = intents)

GUILD = discord.Object(id = int(os.environ.get("GUILD_ID")))

# Send file, scan, return export
@client.tree.command(name = "scan", description = "Scan zip file and export", guild = GUILD)
async def exportFile(interaction: discord.Interaction, export: Literal["apkg", "csv", "sheet"], file: discord.Attachment, sheet_url: str = None):
    if export == "sheet" and not sheet_url:
        await interaction.response.send_message("Please provide a sheet_url for sheet export.")
        return
    
    # available image files
    valid_image_exts = (".png", ".jpg", ".jpeg", ".webp")
    
    if file.filename.lower().endswith(".zip"):
        # handle batch: unzip in memory, loop through images
        pass # change to real code later
    elif file.filename.lower().endswith(valid_image_exts):
        # handle single image directly
        pass # change to real code later
    else:
        await interaction.response.send_message("Please attach a .zip file or an image (png/jpg/jpeg/webp).")
        return 
    
    await interaction.response.send_message(f"Scanning {file.filename} and exporting as {export}")

# run the bot
client.run(os.environ.get("DISCORD_TOKEN"))