import os
import telebot
import requests
import time
import traceback
import threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN", "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4")

bot = telebot.TeleBot(TOKEN)

================= WEB SERVER FOR RENDER =================

app = Flask(name)

@app.route("/")
def home():
return "Maveconnect Bot is running!"

def run_web():
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)

================= PRICE FUNCTION =================

def get_price(symbol):
symbol = symbol.lower().strip()

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

            if "price" in data:
                return float(data["price"])

except Exception:
    print(traceback.format_exc())

return None

================= START COMMAND =================

@bot.message_handler(commands=['start'])
def start(message):
bot.reply_to(
message,
"👋 Send a coin symbol like:\nBTC\nETH\nSOL\nDOGE"
)

================= PRICE HANDLER =================

@bot.message_handler(func=lambda m: True)
def handle_message(message):
try:
symbol = message.text.strip()

    price = get_price(symbol)

    if price:
        bot.reply_to(
            message,
            f"💰 {symbol.upper()} = ${price}"
        )
    else:
        bot.reply_to(
            message,
            "❌ Coin not found. Try BTC, ETH, SOL, BNB, XRP, ADA or DOGE"
        )

except Exception:
    print(traceback.format_exc())
    bot.reply_to(message, "⚠️ Error processing request")

================= BOT LOOP =================

def run_bot():
while True:
try:
print("🤖 Bot started")

        bot.remove_webhook()
        time.sleep(1)

        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=30,
            skip_pending=True
        )

    except Exception:
        print(traceback.format_exc())
        time.sleep(10)

================= START APP =================

if name == "main":
threading.Thread(target=run_web).start()
run_bot()
