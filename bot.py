import discord

# checks bot is connected
class Client(discord.Client):
    async def on_ready(self):
        print(f' Logged on as {self.user}!')

# allowing bot access to specific discord functions
intents = discord.Intents.default()
intents.message_content = True

# run the bot

client = Client(intents=intents)
client.run(DISCORD_TOKEN)
