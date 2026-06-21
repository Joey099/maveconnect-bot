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

bot = telebot.TeleBot(TOKEN, threaded=True)

# ================= FLASK APP =================

app = Flask(__name__)

@app.route("/")
def home():
    return "Maveconnect Bot is running"

# ================= SAFETY FIX (IMPORTANT) =================

# 🔥 THIS FIXES YOUR 409 WEBHOOK ERROR
bot.remove_webhook()
time.sleep(1)

# ================= PRICE FUNCTION =================

def get_price(symbol: str):
    symbol = symbol.lower().strip()

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
        r = requests.get(url, timeout=10)
        data = r.json()

        if coin_id in data:
            price = data[coin_id]["usd"]
            return f"💰 {coin_id.upper()} Price: ${price}"
        else:
            return "❌ Coin not found. Try BTC, ETH, SOL, etc."

    except Exception as e:
        return f"⚠️ Error fetching price: {str(e)}"


# ================= HANDLERS =================

@bot.message_handler(commands=['price'])
def price_handler(message):
    try:
        parts = message.text.split()

        if len(parts) < 2:
            bot.reply_to(message, "Usage: /price BTC")
            return

        result = get_price(parts[1])
        bot.reply_to(message, result)

    except:
        bot.reply_to(message, "⚠️ Error occurred")
        print(traceback.format_exc())


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            bot.send_message(
                message.chat.id,
                f"🚀 Join our channel first:\n{CHANNEL_LINK}"
            )
            return
    except:
        pass

    bot.send_message(
        message.chat.id,
        "👋 Welcome to Maveconnect Bot!\n\n"
        "Commands:\n"
        "/price BTC"
    )


# ================= BOT RUNNER (FIXED) =================

def run_bot():
    while True:
        try:
            print("Bot polling started...")
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print("Bot crashed, restarting:", e)
            time.sleep(5)


# ================= MAIN =================

if __name__ == "__main__":
    import threading

    # Run bot in background thread
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    # Run Flask (Render needs this)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
