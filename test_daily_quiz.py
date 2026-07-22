import discord
from discord.ext import tasks
from zoneinfo import ZoneInfo
import datetime
import asyncio

now = datetime.datetime.now(ZoneInfo("America/New_York"))
test_minute = (now.minute + 2) % 60
test_hour = now.hour if now.minute + 2 < 60 else (now.hour + 1) % 24

print(f"Current NY time: {now}")
print(f"Scheduling test for {test_hour}:{test_minute:02d} NY time")

@tasks.loop(time=datetime.time(hour=test_hour, minute=test_minute, tzinfo=ZoneInfo("America/New_York")))
async def test_task():
    print(f"[{datetime.datetime.now()}] TASK FIRED")

@test_task.before_loop
async def before():
    print("Waiting for loop to be ready...")

async def main():
    test_task.start()
    await asyncio.sleep(180)  # run for 3 minutes then stop

asyncio.run(main())