import discord
from dataclasses import dataclass
from discord.ext import tasks
import datetime
from discord import ui
from dataclasses import dataclass
from database import get_review_words, log_reviews
from zoneinfo import ZoneInfo
import datetime


@dataclass
class QuizSession:
    words: list

active_quizzes: dict[int, QuizSession] = {}


def build_quiz_embed(session: QuizSession):
    lines = [f"{i+1}. **{w['vocab_name']}**" for i, w in enumerate(session.words)]
    embed = discord.Embed(
        title="Vocab Quiz",
        description="\n".join(lines) + "\n\nClick **Answer** and type your answers, one per line, in order."
    )
    return embed


class AnswerModal(ui.Modal, title="Your Answers"):
    answers = ui.TextInput(
        label = "One answer per line, in order",
        style=  discord.TextStyle.paragraph,
        placeholder="ほん - book\nよむ - to read\n..."
    )

    def __init__(self, client_id, message):
        super().__init__()
        self.client_id = client_id
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        session = active_quizzes[self.client_id]
        user_lines = self.answers.value.strip().split("\n")

        results = []
        review_batch = []
        correct_count = 0

        for i, word in enumerate(session.words):
            user_answer = user_lines[i].lower() if i < len(user_lines) else ""
            is_correct = (
                word["reading"].lower() in user_answer
                or word["meaning"].lower() in user_answer
            )
            review_batch.append((word["word_id"], is_correct))

            if is_correct:
                correct_count += 1
            mark = "✅" if is_correct else "❌"
            results.append(f"{mark} {word['vocab_name']} — {word['reading']} ({word['meaning']})")

        log_reviews(self.client_id, review_batch)

        final_embed = discord.Embed(
            title=f"Quiz Complete! {correct_count}/{len(session.words)} correct",
            description="\n".join(results)
        )

        await self.message.edit(embed=final_embed, view=None)
        del active_quizzes[self.client_id]
        await interaction.response.defer()


class QuizView(ui.View):
    def __init__(self, client_id, message):
        super().__init__(timeout=300)
        self.client_id = client_id
        self.message = message

    @ui.button(label="Answer", style=discord.ButtonStyle.primary)
    async def answer_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(AnswerModal(self.client_id, self.message))


def setup_quiz(client, GUILD):
    @client.tree.command(name="quiz", description = "Quiz yourself on saved vocab", guild=GUILD)
    async def quiz(interaction: discord.Interaction, num_words: int = 5):
        client_id = interaction.user.id

        if client_id in active_quizzes:
            await interaction.response.send_message("You're already in a quiz! Finish that one first.")
            return

        words = get_review_words(client_id, limit=num_words)

        if not words:
            await interaction.response.send_message("You don't have any saved words yet — try `/scan` first.")
            return

        print('Creating Quiz Session...')
        active_quizzes[client_id] = QuizSession(words=words)
        print('Quiz Session Created')
        print('Embedding quiz...')
        embed = build_quiz_embed(active_quizzes[client_id])
        print('Quiz embedded')
        view = QuizView(client_id, None)

        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

# quizzes.py
def setup_daily_quiz(client, channel_id, target_user_id, hour=3, minute=25):
    @tasks.loop(time=datetime.time(hour=hour, minute=minute, tzinfo=ZoneInfo("America/New_York")))
    async def daily_quiz_post():
        print(f"[{datetime.datetime.now()}] Daily quiz task fired")
        channel = client.get_channel(channel_id)
        if channel is None:
            print("Couldn't find channel for daily quiz")
            return

        words = get_review_words(target_user_id, limit=5)
        if not words:
            return

        session_data = QuizSession(words=words)
        active_quizzes[target_user_id] = session_data
        embed = build_quiz_embed(session_data)
        view = QuizView(target_user_id, None)

        message = await channel.send(embed=embed, view=view)
        view.message = message

    @daily_quiz_post.before_loop
    async def before_daily_quiz():
        await client.wait_until_ready()

    return daily_quiz_post 