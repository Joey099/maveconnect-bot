import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found")

bot = telebot.TeleBot(TOKEN, threaded=True)

app = Flask(__name__)

@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

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

def get_price(coin):
    coin = coin.lower()

    if coin not in COINS:
        return None

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": COINS[coin],
                "vs_currencies": "usd"
            },
            timeout=10
        )

        data = r.json()
        return data.get(COINS[coin], {}).get("usd")

    except Exception as e:
        print("Price error:", e)
        return None
        
@bot.message_handler(commands=["test"])
def test(msg):
    bot.reply_to(msg, "🔥 NEW CODE IS RUNNING")
    
@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        "🚀 LEVEL 4 AI TRADING BOT\n\n"
        "📢 Free Group:\n"
        "https://t.me/UltimateAvian\n\n"
        "💎 VIP Group:\n"
        "https://t.me/UltimateAve\n\n"
        "Commands:\n"
        "/price btc\n"
        "/signal btc"
    )

@bot.message_handler(commands=["price"])
def price_cmd(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /price btc")
        return

    coin = parts[1].lower()

    price = get_price(coin)

    if price:
        bot.reply_to(msg, f"💰 {coin.upper()} = ${price}")
    else:
        bot.reply_to(msg, "❌ Coin not found")

@bot.message_handler(commands=["signal"])
def signal_cmd(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /signal btc")
        return

    coin = parts[1].lower()

    price = get_price(coin)

    if not price:
        bot.reply_to(msg, "❌ Coin not found")
        return

    bot.reply_to(
        msg,
        f"🤖 {coin.upper()} SIGNAL\n\n⚪ HOLD\n💰 Price: ${price}"
    )

def run():
    while True:
        try:
            print("Bot started polling...")

            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )

        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)

if __name__ == "__main__":
    print("Starting application...")

    try:
        bot.remove_webhook()
        print("Webhook removed")
    except Exception as e:
        print("Webhook error:", e)

    time.sleep(2)

    Thread(target=run, daemon=True).start()

    print("Polling thread started")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
)
