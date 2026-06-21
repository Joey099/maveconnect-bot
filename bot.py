import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found")

FREE_CHANNEL = "@UltimateAvian"
VIP_CHANNEL = "@UltimateAve"

bot = telebot.TeleBot(TOKEN, threaded=True)

app = Flask(__name__)

@app.route("/")
def home():
    return "Level 3 AI Trading Bot Running 🚀"

# ================= SAFETY =================

bot.remove_webhook()
time.sleep(1)

# ================= COINS =================

COINS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "matic": "matic-network",
    "dot": "polkadot",
    "ltc": "litecoin",
    "trx": "tron",
    "avax": "avalanche-2",
    "shib": "shiba-inu",
    "link": "chainlink"
}

# ================= PRICE ENGINE (FIXED) =================

def get_price(coin):
    coin = coin.lower().strip()

    if coin not in COINS:
        return None

    coin_id = COINS[coin]

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        return data.get(coin_id, {}).get("usd", None)

    except:
        return None


# ================= MARKET HISTORY SIMULATION =================

def get_price_history(coin):
    prices = []

    for _ in range(6):
        p = get_price(coin)
        if p:
            prices.append(p)
        time.sleep(0.3)

    return prices


# ================= LEVEL 3 AI ENGINE =================

def ai_signal(coin):
    prices = get_price_history(coin)

    if len(prices) < 4:
        return "❌ No data", 0

    # trend calculation
    start = prices[0]
    end = prices[-1]

    change = ((end - start) / start) * 100

    volatility = max(prices) - min(prices)

    score = 50

    # TREND LOGIC
    if change > 2:
        score += 25
        signal = "🟢 STRONG BUY"
    elif change > 0.5:
        score += 10
        signal = "🟡 BUY"
    elif change < -2:
        score += 25
        signal = "🔴 STRONG SELL"
    elif change < -0.5:
        score += 10
        signal = "🟠 SELL"
    else:
        signal = "⚪ HOLD"

    # VOLATILITY FILTER (important upgrade)
    if volatility > start * 0.05:
        score -= 10

    return (
        f"{signal}\n"
        f"📊 Change: {change:.2f}%\n"
        f"📉 Volatility: {volatility:.2f}\n"
        f"🔥 Strength: {score}/100",
        score
    )


# ================= VIP SYSTEM =================

def send_vip_signal(coin, signal, score):
    if score >= 75:
        bot.send_message(
            VIP_CHANNEL,
            f"🔥 VIP LEVEL 3 SIGNAL\n\n"
            f"{coin.upper()}\n\n"
            f"{signal}\n\n"
            f"🤖 AI Confidence: {score}/100"
        )


# ================= COMMANDS =================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 LEVEL 3 AI TRADING BOT\n\n"
        "/price BTC\n"
        "/signal BTC\n"
        "/scan"
    )


@bot.message_handler(commands=['price'])
def price(message):
    try:
        coin = message.text.split()[1]
        p = get_price(coin)

        if p:
            bot.reply_to(message, f"💰 {coin.upper()} = ${p}")
        else:
            bot.reply_to(message, "❌ Coin not supported")

    except:
        bot.reply_to(message, "Usage: /price BTC")


@bot.message_handler(commands=['signal'])
def signal(message):
    try:
        coin = message.text.split()[1]

        sig, score = ai_signal(coin)

        bot.reply_to(
            message,
            f"🤖 {coin.upper()} AI SIGNAL\n\n{sig}"
        )

        send_vip_signal(coin, sig, score)

    except:
        bot.reply_to(message, "Usage: /signal BTC")


@bot.message_handler(commands=['scan'])
def scan(message):
    msg = "📊 LEVEL 3 MARKET SCAN\n\n"

    for coin in COINS.keys():
        sig, score = ai_signal(coin)
        msg += f"{coin.upper()}: {score}/100\n"

        send_vip_signal(coin, sig, score)
        time.sleep(0.4)

    bot.send_message(message.chat.id, msg)


# ================= BOT LOOP =================

def run_bot():
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print("Restarting:", e)
            time.sleep(5)


# ================= MAIN =================

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
