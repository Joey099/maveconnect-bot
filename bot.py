import os
import telebot
import requests
import time
import traceback
import threading
from flask import Flask

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN", "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4")
bot = telebot.TeleBot(TOKEN)

# ================= WEB SERVER (RENDER KEEP ALIVE) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Maveconnect Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= NAME MAPPING (UPGRADE) =================
name_map = {
    "bitcoin": "btc",
    "btc": "btc",
    "ethereum": "eth",
    "eth": "eth",
    "solana": "sol",
    "sol": "sol",
    "binance": "bnb",
    "bnb": "bnb",
    "ripple": "xrp",
    "xrp": "xrp",
    "cardano": "ada",
    "ada": "ada",
    "dogecoin": "doge",
    "doge": "doge"
}

# ================= PRICE FUNCTION =================
def get_price(symbol):
    symbol = symbol.lower().strip()

    symbol = name_map.get(symbol, symbol)

    binance_map = {
        "btc": "BTCUSDT",
        "eth": "ETHUSDT",
        "sol": "SOLUSDT",
        "bnb": "BNBUSDT",
        "xrp": "XRPUSDT",
        "ada": "ADAUSDT",
        "doge": "DOGEUSDT"
    }

    try:
        pair = binance_map.get(symbol)

        if pair:
            r = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={"symbol": pair},
                timeout=5
            )

            if r.status_code == 200:
                data = r.json()
                return float(data["price"])

    except Exception:
        print(traceback.format_exc())

    return None

# ================= /START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "👋 Welcome!\n\nSend:\nBTC / ETH / SOL\nor use:\n/price btc"
    )

# ================= /PRICE COMMAND (UPGRADE) =================
@bot.message_handler(commands=['price'])
def price_cmd(message):
    try:
        parts = message.text.split()

        if len(parts) < 2:
            bot.reply_to(message, "Usage: /price btc")
            return

        symbol = parts[1]
        price = get_price(symbol)

        if price:
            bot.reply_to(message, f"💰 {symbol.upper()} = ${price}")
        else:
            bot.reply_to(message, "❌ Coin not found.")

    except Exception:
        print(traceback.format_exc())
        bot.reply_to(message, "⚠️ Error processing request")

# ================= NORMAL MESSAGE =================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        text = message.text.lower().strip().replace("/", "").split()[0]

        price = get_price(text)

        if price:
            bot.reply_to(message, f"💰 {text.upper()} = ${price}")
        else:
            bot.reply_to(
                message,
                "❌ Coin not found. Try BTC, ETH, SOL, BNB, XRP, ADA, DOGE"
            )

    except Exception:
        print(traceback.format_exc())
        bot.reply_to(message, "⚠️ Error processing request")

# ================= BOT LOOP =================
def run_bot():
    while True:
        try:
            print("🤖 Bot running...")

            bot.remove_webhook()
            time.sleep(2)

            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                skip_pending=True
            )

        except Exception:
            print("Bot crashed, restarting...")
            print(traceback.format_exc())
            time.sleep(5)

# ================= START EVERYTHING =================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
