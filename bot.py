import os
import telebot
import requests
import time
import traceback
import threading
from flask import Flask

# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found in Render Environment Variables")

CHANNEL = "@UltimateAvian"
CHANNEL_LINK = "https://t.me/UltimateAvian"

bot = telebot.TeleBot(TOKEN)

# ================= WEB SERVER =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Maveconnect Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= COIN MAP =================

coin_map = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "sol": "solana",
    "solana": "solana",
    "bnb": "binancecoin",
    "binance": "binancecoin",
    "xrp": "ripple",
    "ripple": "ripple",
    "ada": "cardano",
    "cardano": "cardano",
    "doge": "dogecoin",
    "dogecoin": "dogecoin"
}

# ================= MEMBERSHIP CHECK =================

def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception:
        print(traceback.format_exc())
        return False

# ================= PRICE FETCHER =================

def get_price(symbol):
    try:
        symbol = symbol.lower().strip()

        coin = coin_map.get(symbol)

        if not coin:
            return None

        url = "https://api.coingecko.com/api/v3/simple/price"

        r = requests.get(
            url,
            params={
                "ids": coin,
                "vs_currencies": "usd"
            },
            timeout=10
        )

        if r.status_code != 200:
            return None

        data = r.json()

        return data.get(coin, {}).get("usd")

    except Exception:
        print(traceback.format_exc())
        return None

# ================= START =================

@bot.message_handler(commands=["start"])
def start(message):

    if not is_member(message.from_user.id):

        bot.reply_to(
            message,
            f"🚀 To use this bot, join our channel first:\n\n{CHANNEL_LINK}\n\nThen send /start again."
        )

        return

    bot.reply_to(
        message,
        "🔥 Welcome to Maveconnect Bot\n\n"
        "Supported Coins:\n"
        "BTC\nETH\nSOL\nBNB\nXRP\nADA\nDOGE\n\n"
        "Example:\n"
        "/price btc"
    )

# ================= PRICE COMMAND =================

@bot.message_handler(commands=["price"])
def price_command(message):

    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"🚀 Join first:\n{CHANNEL_LINK}"
        )
        return

    parts = message.text.split()

    if len(parts) < 2:
        bot.reply_to(
            message,
            "Usage:\n/price btc"
        )
        return

    symbol = parts[1]

    price = get_price(symbol)

    if price is None:
        bot.reply_to(
            message,
            "❌ Coin not supported."
        )
        return

    bot.reply_to(
        message,
        f"💰 {symbol.upper()} Price\n\n${price:,}"
    )

# ================= TEXT COINS =================

@bot.message_handler(func=lambda m: True)
def coin_lookup(message):

    if not is_member(message.from_user.id):
        bot.reply_to(
            message,
            f"🚀 Join first:\n{CHANNEL_LINK}"
        )
        return

    text = message.text.lower().strip()

    price = get_price(text)

    if price:

        bot.reply_to(
            message,
            f"💰 {text.upper()} Price\n\n${price:,}"
        )

# ================= BOT RUNNER =================

def run_bot():

    while True:

        try:

            print("🤖 Starting bot...")

            bot.remove_webhook()

            time.sleep(2)

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except Exception:

            print("⚠️ Restarting bot...")
            print(traceback.format_exc())

            time.sleep(5)

# ================= MAIN =================

if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    run_bot()
