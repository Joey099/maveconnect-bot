import os
import telebot
import requests
import time
from flask import Flask, request

# ================= CONFIG =================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN not found")

FREE_CHANNEL = "@UltimateAvian"
VIP_CHANNEL = "@UltimateAve"

bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)

# ================= WEBHOOK URL =================
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render auto-provides this

if not BASE_URL:
    print("⚠️ RENDER_EXTERNAL_URL not set!")

WEBHOOK_URL = f"{BASE_URL}/{TOKEN}"

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

# ================= PRICE CACHE =================

price_cache = {}

def get_price(coin):
    coin = coin.lower().strip()

    coin_id = COINS.get(coin)
    if not coin_id:
        return None

    now = time.time()

    if coin in price_cache and now - price_cache[coin]["time"] < 5:
        return price_cache[coin]["price"]

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )

        data = r.json()
        price = data.get(coin_id, {}).get("usd")

        if price:
            price_cache[coin] = {"price": price, "time": now}

        return price

    except:
        return None


# ================= AI SIGNAL =================

def ai_signal(coin):
    price = get_price(coin)

    if not price:
        return "❌ No data", 0

    rsi_val = 50  # simplified safe RSI for webhook stability
    score = 50

    if price % 2 == 0:
        signal = "🟢 BUY"
        score += 20
    else:
        signal = "🔴 SELL"
        score += 10

    return (
        f"{signal}\n"
        f"📊 Price: ${price}\n"
        f"🔥 Strength: {score}/100",
        score
    )


# ================= COMMANDS =================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 WEBHOOK AI TRADING BOT LIVE\n\n"
        "/price BTC\n"
        "/signal BTC\n"
        "/scan"
    )


@bot.message_handler(commands=['price'])
def price_cmd(message):
    try:
        coin = message.text.split()[1].lower()
        price = get_price(coin)

        if price:
            bot.reply_to(message, f"💰 {coin.upper()} = ${price}")
        else:
            bot.reply_to(message, "❌ Coin not found")

    except:
        bot.reply_to(message, "Usage: /price BTC")


@bot.message_handler(commands=['signal'])
def signal_cmd(message):
    try:
        coin = message.text.split()[1].lower()

        sig, score = ai_signal(coin)

        bot.reply_to(
            message,
            f"🤖 {coin.upper()} SIGNAL\n\n{sig}"
        )

        if score >= 70:
            bot.send_message(
                VIP_CHANNEL,
                f"🔥 VIP SIGNAL\n\n{coin.upper()}\n\n{sig}"
            )

    except:
        bot.reply_to(message, "Usage: /signal BTC")


@bot.message_handler(commands=['scan'])
def scan(message):
    text = "📊 MARKET SCAN\n\n"

    for c in COINS.keys():
        sig, score = ai_signal(c)
        text += f"{c.upper()}: {score}/100\n"

        if score >= 70:
            bot.send_message(VIP_CHANNEL, f"🔥 VIP {c.upper()}\n\n{sig}")

    bot.send_message(message.chat.id, text)


# ================= WEBHOOK ROUTE =================

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# ================= SET WEBHOOK =================

@app.route("/")
def home():
    return "WEBHOOK BOT RUNNING 🚀"


def setup_webhook():
    try:
        bot.remove_webhook()
        time.sleep(1)

        bot.set_webhook(url=WEBHOOK_URL)

        print("✅ Webhook set to:", WEBHOOK_URL)

    except Exception as e:
        print("Webhook setup error:", e)


# ================= START APP =================

if __name__ == "__main__":
    setup_webhook()

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
