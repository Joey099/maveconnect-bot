import os
import telebot
import requests
from flask import Flask, request

# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

FREE_CHANNEL = "@UltimateAvian"
VIP_CHANNEL = "@UltimateAve"

# ================= REMOVE OLD WEBHOOK =================

bot.remove_webhook()

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

# ================= PRICE =================

def get_price(coin):
    coin = coin.lower().strip()

    coin_id = COINS.get(coin)
    if not coin_id:
        return None

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )
        data = r.json()
        return data.get(coin_id, {}).get("usd")
    except:
        return None

# ================= COMMANDS =================

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🚀 Bot is live")

@bot.message_handler(commands=['price'])
def price(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /price BTC")
        return

    price = get_price(parts[1])

    if price:
        bot.reply_to(msg, f"💰 {parts[1].upper()} = ${price}")
    else:
        bot.reply_to(msg, "❌ Coin not found")

# ================= WEBHOOK =================

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK"

@app.route("/")
def home():
    return "Bot is running"

# ================= MAIN =================

if __name__ == "__main__":
    bot.set_webhook(url=f"https://maveconnect-bot-25.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
