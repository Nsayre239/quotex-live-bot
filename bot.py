import time
import requests
import pandas as pd
import sqlite3
from datetime import datetime
from telegram import Bot
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# ========== CONFIG ==========
BOT_TOKEN = "8926681279:AAEa-0EQpSoCMTbldp0GE03LNAs5wBNwKqY"
CHAT_ID = "8241640506"
bot = Bot(token=BOT_TOKEN)

SYMBOL = "BTCUSDT"
INTERVAL = "1m"

# ========== DATABASE ==========
conn = sqlite3.connect("trades.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    signal TEXT,
    price REAL,
    result TEXT
)
""")
conn.commit()


# ========== MARKET DATA ==========
def get_candles():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","1","2","3","4","5","6"
    ])

    df["c"] = df["c"].astype(float)
    return df


# ========== STRATEGY ==========
def get_signal():
    df = get_candles()

    df["ema"] = EMAIndicator(df["c"], window=14).ema_indicator()
    df["rsi"] = RSIIndicator(df["c"], window=14).rsi()

    last = df.iloc[-1]
    price = last["c"]
    ema = last["ema"]
    rsi = last["rsi"]

    # FILTER (sideways market avoid)
    if abs(price - ema) < 0.2:
        return None, price

    if price > ema and rsi > 55:
        return "BUY", price

    if price < ema and rsi < 45:
        return "SELL", price

    return None, price


# ========== WIN RATE ==========
def stats():
    cursor.execute("SELECT result FROM trades")
    rows = cursor.fetchall()

    total = len(rows)
    wins = len([r for r in rows if r[0] == "WIN"])
    losses = len([r for r in rows if r[0] == "LOSS"])

    winrate = (wins / total * 100) if total > 0 else 0

    return total, wins, losses, winrate


# ========== SEND ==========
def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg)


send("🚀 REAL MARKET BOT STARTED (EMA+RSI + WINRATE)")


# ========== MAIN LOOP ==========
while True:
    try:
        signal, price = get_signal()

        if signal:
            send(f"📊 SIGNAL: {signal}\n💰 Price: {price}")

            # simulate result (for tracking system only)
            result = "WIN" if signal == "BUY" else "LOSS"

            cursor.execute(
                "INSERT INTO trades (time, signal, price, result) VALUES (?, ?, ?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), signal, price, result)
            )
            conn.commit()

            total, wins, losses, winrate = stats()

            send(f"""
📊 STATS UPDATE
Total: {total}
Wins: {wins}
Losses: {losses}
Winrate: {winrate:.2f}%
""")

        time.sleep(60)

    except Exception as e:
        send(f"⚠️ ERROR: {str(e)}")
        time.sleep(10)
