import time
import requests
import pandas as pd

# =========================
# CONFIG (FILL THESE IN)
# =========================
TOKEN = "8983065895:AAFRC37xwNMezzLbSeEc0xXvfw00-Z5Rmfo"
CHAT_ID = "8772042549"

# prevents duplicate signals
last_signal = None


def send_message(message):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )


def run_bot():
    global last_signal

    # =========================
    # 1. GET MARKET DATA
    # =========================
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"

    params = {
        "granularity": 21600,  # 6H candles (swing style)
        "limit": 350
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "low", "high", "open", "close", "volume"
    ])

    df = df.sort_values("timestamp")

    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)

    # =========================
    # 2. INDICATORS
    # =========================
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    latest = df.iloc[-1]

    price = latest["close"]
    ema50 = latest["ema50"]
    ema200 = latest["ema200"]

    # =========================
    # 3. TREND + PULLBACK FILTER
    # =========================
    trend_bullish = ema50 > ema200
    trend_bearish = ema50 < ema200

    pullback_zone = abs(price - ema50) / ema50

    # =========================
    # 4. SIGNAL LOGIC
    # =========================
    if trend_bullish and pullback_zone < 0.01:
        signal = "BUY"

    elif trend_bearish and pullback_zone < 0.01:
        signal = "SELL"

    else:
        signal = "NO TRADE"

    print("Signal:", signal)

    # =========================
    # 5. STOP DUPLICATES
    # =========================
    if signal == last_signal or signal == "NO TRADE":
        return

    # =========================
    # 6. BUILD TRADE
    # =========================
    entry = price
    lookback = 10

    if signal == "BUY":
        stop_loss = df["low"].iloc[-lookback:].min()
        risk = entry - stop_loss
        take_profit = entry + (risk * 2)

        message = f"""
🚀 BTC BUY SIGNAL

Entry: {entry:.2f}
SL: {stop_loss:.2f}
TP: {take_profit:.2f}

RR: 1:2
"""

    else:
        stop_loss = df["high"].iloc[-lookback:].max()
        risk = stop_loss - entry
        take_profit = entry - (risk * 2)

        message = f"""
📉 BTC SELL SIGNAL

Entry: {entry:.2f}
SL: {stop_loss:.2f}
TP: {take_profit:.2f}

RR: 1:2
"""

    # =========================
    # 7. SEND TELEGRAM
    # =========================
    send_message(message)
    print("Sent:", signal)

    last_signal = signal


# =========================
# 8. 24/7 LOOP
# =========================
while True:
    try:
        run_bot()

    except Exception as e:
        print("Error:", e)

    time.sleep(300)  # 5 minutes
