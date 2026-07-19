import discord
import os
import json
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from typing import Literal
import json
import io

load_dotenv()

from gemini_ocr import extract_vocab
from util_functions import extract_images_from_zip, process_images, export_to_csv, 

class Client(commands.Bot):
    async def on_ready(self):
        print(f' Logged on as {self.user}!')
        try:
            guild = discord.Object(id=int(os.environ.get("GUILD_ID")))
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD = discord.Object(id=int(os.environ.get("GUILD_ID")))

@client.tree.command(name="scan", description="Scan zip file and export", guild=GUILD)
async def exportFile(interaction: discord.Interaction, export: Literal["apkg", "csv", "sheet"], file: discord.Attachment, sheet_url: str = None):
    if export == "sheet" and not sheet_url:
        await interaction.response.send_message("Please provide a sheet_url for sheet export.")
        return

    valid_image_exts = (".png", ".jpg", ".jpeg", ".webp")

    if not (file.filename.lower().endswith(".zip") or file.filename.lower().endswith(valid_image_exts)):
        await interaction.response.send_message("Please attach a .zip file or an image (png/jpg/jpeg/webp).")
        return

    await interaction.response.defer()

    if file.filename.lower().endswith(".zip"):
        zip_bytes = await file.read()
        images = extract_images_from_zip(zip_bytes)

        if not images:
            await interaction.followup.send("No valid images found in that zip.")
            return

        all_vocab = await process_images(images)

    else:  # single image
        image_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"
        raw_result = extract_vocab([(file.filename, image_bytes, mime_type)])
        all_vocab = json.loads(raw_result)["vocab"]

    if export == "apkg":
        apkg_bytes = export_to_anki(all_vocab)
        await interaction.followup.send(
            f"Processed {len(all_vocab)} words from {file.filename}:",
            file=discord.File(io.BytesIO(apkg_bytes), filename="vocab_deck.apkg")
        )

    elif export == "csv":
        csv_bytes = export_to_csv(all_vocab)
        await interaction.followup.send(
            f"Processed {len(all_vocab)} words from {file.filename}:",
            file=discord.File(io.BytesIO(csv_bytes), filename="vocab_sheet.csv")
        )

    elif export == "sheet":
        await interaction.followup.send("Sheet export coming soon!")


client.run(os.environ.get("DISCORD_TOKEN"))