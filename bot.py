import os
import time
import requests
from flask import Flask
from threading import Thread
import telebot

# ================= BOT =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN not found")

bot = telebot.TeleBot(TOKEN, threaded=True)
app = Flask(__name__)

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

price_cache = {}
CACHE_TIME = 30

# ================= PRICE ENGINE =================
def get_price(coin):
    coin = coin.lower().strip()

    if coin not in COINS:
        return None

    now = time.time()

    # cache
    if coin in price_cache:
        price, ts = price_cache[coin]
        if now - ts < CACHE_TIME:
            return price

    coin_id = COINS[coin]

    # CoinGecko
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )

        data = r.json()
        price = data.get(coin_id, {}).get("usd")

        if price:
            price_cache[coin] = (float(price), now)
            return float(price)

    except:
        pass

    return None

# ================= FLASK =================
@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

# ================= COMMANDS =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg,
        "🚀 LEVEL 4 AI TRADING BOT\n\n"
        "📢 Free: https://t.me/UltimateAvian\n"
        "💎 VIP: https://t.me/UltimateAve\n\n"
        "/price btc\n/signal btc"
    )

@bot.message_handler(commands=["price"])
def price_cmd(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /price btc")
        return

    coin = parts[1].lower().strip()   # ✅ FIXED

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

    coin = parts[1].lower().strip()   # ✅ FIXED

    price = get_price(coin)

    if not price:
        bot.reply_to(msg, "❌ Coin not found")
        return

    bot.reply_to(
        msg,
        f"🤖 {coin.upper()} SIGNAL\n\n⚪ HOLD\n💰 Price: ${price}"
    )

# ================= BOT LOOP =================
def run_bot():
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)

# ================= START =================
if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
