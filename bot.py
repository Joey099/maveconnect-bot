import os
import telebot
import requests
import time
import traceback
from flask import Flask

# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found in Render Environment Variables")

CHANNEL = "@UltimateAvian"
CHANNEL_LINK = "https://t.me/UltimateAvian"

bot = telebot.TeleBot(TOKEN)

# ================= FLASK APP =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Maveconnect Bot is running"

# ================= PRICE FUNCTION =================

def get_price(symbol: str):
    """
    Fetch crypto price from CoinGecko
    """

    symbol = symbol.lower().strip()

    # simple mapping (you can expand this)
    mapping = {
        "btc": "bitcoin",
        "bitcoin": "bitcoin",
        "eth": "ethereum",
        "ethereum": "ethereum",
        "bnb": "binancecoin",
        "sol": "solana",
        "xrp": "ripple",
        "doge": "dogecoin"
    }

    coin_id = mapping.get(symbol, symbol)

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if coin_id in data:
            price = data[coin_id]["usd"]
            return f"💰 {coin_id.upper()} Price: ${price}"
        else:
            return "❌ Coin not found. Try BTC, ETH, SOL, etc."

    except Exception as e:
        return f"⚠️ Error fetching price: {str(e)}"


# ================= PRICE HANDLER =================

@bot.message_handler(commands=['price'])
def price_handler(message):
    try:
        parts = message.text.split()

        if len(parts) < 2:
            bot.reply_to(message, "Usage: /price BTC")
            return

        symbol = parts[1]
        result = get_price(symbol)

        bot.reply_to(message, result)

    except Exception as e:
        bot.reply_to(message, "⚠️ Something went wrong.")
        print(traceback.format_exc())


# ================= CHANNEL CHECK (OPTIONAL) =================

def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ================= START COMMAND =================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            f"🚀 To use this bot, you must join our channel first:\n{CHANNEL_LINK}"
        )
        return

    bot.send_message(
        message.chat.id,
        "👋 Welcome to Maveconnect Bot!\n\n"
        "Use:\n"
        "/price BTC - to check crypto prices"
    )


# ================= POLLING =================

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print("Bot crashed, restarting...", e)
            time.sleep(5)


# ================= MAIN =================

if __name__ == "__main__":
    from threading import Thread

    Thread(target=run_bot).start()

    # Flask server (Render / hosting)
    app.run(host="0.0.0.0", port=5000)
