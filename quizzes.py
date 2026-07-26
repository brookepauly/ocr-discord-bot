import discord
from discord import ui
from discord.ext import tasks
from dataclasses import dataclass
from zoneinfo import ZoneInfo
import datetime
from database import get_words_due_for_review

@dataclass
class RecapSession:
    words: list
    index: int = 0
    revealed: bool = False


active_recaps: dict[int, RecapSession] = {}


def build_recap_embed(session: RecapSession):
    word = session.words[session.index]
    embed = discord.Embed(
        title=f"Word {session.index + 1}/{len(session.words)}",
        description=f"# {word['vocab_name']}"
    )
    if session.revealed:
        embed.add_field(name="Reading", value=word["reading"], inline=True)
        embed.add_field(name="Meaning", value=word["meaning"], inline=True)
    return embed


class RecapView(ui.View):
    def __init__(self, client_id, message):
        super().__init__(timeout=1800)
        self.client_id = client_id
        self.message = message
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        session = active_recaps[self.client_id]

        if not session.revealed:
            self.add_item(self.RevealButton())
        else:
            self.add_item(self.NextButton())

    class RevealButton(ui.Button):
        def __init__(self):
            super().__init__(label="Show Answer", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            view: RecapView = self.view
            session = active_recaps[view.client_id]
            session.revealed = True
            view.update_buttons()
            await interaction.response.edit_message(embed=build_recap_embed(session), view=view)

    class NextButton(ui.Button):
        def __init__(self):
            super().__init__(label="Next ➡️", style=discord.ButtonStyle.secondary)

        async def callback(self, interaction: discord.Interaction):
            view: RecapView = self.view
            session = active_recaps[view.client_id]

            session.index += 1
            session.revealed = False

            if session.index >= len(session.words):
                final_embed = discord.Embed(title="Recap complete ✅")
                await interaction.response.edit_message(embed=final_embed, view=None)
                del active_recaps[view.client_id]
            else:
                view.update_buttons()
                await interaction.response.edit_message(embed=build_recap_embed(session), view=view)


def setup_daily_quiz(client, channel_id, target_user_id, hour=9, minute=0):
    @tasks.loop(time=datetime.time(hour=hour, minute=minute, tzinfo=ZoneInfo("America/New_York")))
    async def daily_quiz_post():
        print(f"[{datetime.datetime.now()}] Daily recap task fired")
        channel = client.get_channel(channel_id)
        if channel is None:
            print("Couldn't find channel for daily recap")
            return

        words = get_words_due_for_review(target_user_id, limit=10)
        if not words:
            return

        active_recaps[target_user_id] = RecapSession(words=words)
        view = RecapView(target_user_id, None)
        embed = build_recap_embed(active_recaps[target_user_id])

        message = await channel.send(embed=embed, view=view)
        view.message = message

    @daily_quiz_post.before_loop
    async def before_daily_quiz():
        await client.wait_until_ready()

    return daily_quiz_post