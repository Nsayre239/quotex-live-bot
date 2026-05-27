import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

SYMBOL = "GBPJPY"

def get_data():
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=200"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","1","2","3","4","5","6"
    ])

    df["c"] = df["c"].astype(float)
    return df


def generate_signal():
    df = get_data()

    # ===== TREND FILTER (STRONG) =====
    df["ema50"] = EMAIndicator(df["c"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["c"], window=200).ema_indicator()

    # ===== MOMENTUM =====
    df["rsi"] = RSIIndicator(df["c"], window=14).rsi()

    last = df.iloc[-2]   # IMPORTANT: previous candle (early signal)
    price = last["c"]
    ema50 = last["ema50"]
    ema200 = last["ema200"]
    rsi = last["rsi"]

    # ===== FILTER 1: TREND =====
    uptrend = ema50 > ema200
    downtrend = ema50 < ema200

    # ===== FILTER 2: AVOID SIDEWAYS =====
    if abs(ema50 - ema200) < 0.5:
        return None

    # ===== BUY SIGNAL =====
    if uptrend and rsi > 55:
        return "BUY"

    # ===== SELL SIGNAL =====
    if downtrend and rsi < 45:
        return "SELL"

    return None
