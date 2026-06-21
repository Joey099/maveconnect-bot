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
    return "Level 2 AI Trading Bot Running 🚀"

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
    "ltc": "litecoin"
}

# ================= PRICE =================

def get_price(coin):
    coin_id = COINS.get(coin.lower(), coin.lower())

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data[coin_id]["usd"]
    except:
        return None


# ================= RSI (SIMULATED REALISTIC) =================

def get_rsi_like(coin):
    prices = []

    for _ in range(5):
        p = get_price(coin)
        if p:
            prices.append(p)
        time.sleep(0.5)

    if len(prices) < 3:
        return 50

    gains = 0
    losses = 0

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        return 100

    rs = gains / losses
    rsi = 100 - (100 / (1 + rs))

    return rsi


# ================= AI SIGNAL ENGINE =================

def ai_signal(coin):
    price = get_price(coin)
    rsi = get_rsi_like(coin)

    if not price:
        return "❌ No data", 0

    strength = 50

    # RSI logic
    if rsi > 70:
        signal = "🔴 SELL"
        strength += 30
    elif rsi < 30:
        signal = "🟢 BUY"
        strength += 30
    else:
        signal = "🟡 HOLD"
        strength += 10

    # Trend logic
    if price > get_price(coin):
        strength += 10
    else:
        strength -= 5

    return f"{signal} | RSI: {int(rsi)} | Strength: {strength}/100", strength


# ================= VIP SENDER =================

def send_vip_signal(coin, signal, strength):
    if strength >= 70:
        bot.send_message(
            VIP_CHANNEL,
            f"🔥 VIP SIGNAL\n\n"
            f"{coin.upper()}\n"
            f"{signal}\n\n"
            f"📊 Auto-generated AI signal"
        )


# ================= COMMANDS =================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 LEVEL 2 AI TRADING BOT\n\n"
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
            bot.reply_to(message, "❌ Not found")

    except:
        bot.reply_to(message, "Usage: /price BTC")


@bot.message_handler(commands=['signal'])
def signal(message):
    try:
        coin = message.text.split()[1]

        sig, strength = ai_signal(coin)

        bot.reply_to(
            message,
            f"🤖 {coin.upper()} SIGNAL\n\n{sig}"
        )

        # Send VIP if strong
        send_vip_signal(coin, sig, strength)

    except:
        bot.reply_to(message, "Usage: /signal BTC")


# ================= MARKET SCAN =================

@bot.message_handler(commands=['scan'])
def scan(message):
    msg = "📊 AI SCAN RESULTS\n\n"

    for coin in COINS.keys():
        sig, strength = ai_signal(coin)
        msg += f"{coin.upper()}: {sig}\n"

        send_vip_signal(coin, sig, strength)
        time.sleep(0.5)

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
