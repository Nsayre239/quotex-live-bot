import asyncio
import random
from datetime import datetime, timedelta
from telegram import Bot

TOKEN = "8926681279:AAEa-0EQpSoCMTbldp0GE03LNAs5wBNwKqY"
CHANNEL_ID = "8241640506"

bot = Bot(token=TOKEN)

wins = 0
loss = 0
total = 0

pairs = [
    "GBPJPY-OTC",
    "EURUSD-OTC",
    "USDJPY-OTC",
    "EURJPY-OTC"
]

async def send_signal():

    global wins, loss, total

    pair = random.choice(pairs)

    timeframe = random.choice(["M1", "M2", "M5"])

    signal = random.choice(["PUT 🔴", "CALL 🟢"])

    now = datetime.now()

    entry = now.strftime("%H:%M")

    if timeframe == "M1":
        exit_time = (now + timedelta(minutes=1)).strftime("%H:%M")

    elif timeframe == "M2":
        exit_time = (now + timedelta(minutes=2)).strftime("%H:%M")

    else:
        exit_time = (now + timedelta(minutes=5)).strftime("%H:%M")

    msg = f"""
🚧 LIVE SIGNAL

💷 {pair}

Entry⏳ {entry}
Exit ⏰ {exit_time}

⌚️ {timeframe}

{signal}
"""

    await bot.send_message(chat_id=CHANNEL_ID, text=msg)

    await asyncio.sleep(10)

    result = random.choice(["WIN ✅", "LOSS ❌"])

    total += 1

    if result == "WIN ✅":
        wins += 1
    else:
        loss += 1

    result_msg = f"""
{result}

{pair}
⏰ {entry}
"""

    await bot.send_message(chat_id=CHANNEL_ID, text=result_msg)

    summary = f"""
📊 SUMMARY

Date: {datetime.now().strftime('%d/%m/%Y')}

Total Signal: {total}

Total Win: {wins}

Total Loss: {loss}
"""

    await bot.send_message(chat_id=CHANNEL_ID, text=summary)


async def main():

    while True:

        await send_signal()

        await asyncio.sleep(60)


asyncio.run(main())