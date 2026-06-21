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
print("Telegram bot initialized")

app = Flask(__name__)

@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

# IMPORTANT FIX (prevents 409 webhook conflict)
try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass


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

# ================= CACHE =================

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


# ================= INDICATORS =================

def rsi(coin):
    prices = []

    for _ in range(7):
        p = get_price(coin)
        if p:
            prices.append(p)
        time.sleep(0.3)

    if len(prices) < 3:
        return 50

    gains, losses = 0, 0

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        return 100

    rs = gains / losses
    return 100 - (100 / (1 + rs))


def macd_trend(coin):
    p1 = get_price(coin)
    time.sleep(0.8)
    p2 = get_price(coin)

    if not p1 or not p2:
        return 0

    return ((p2 - p1) / p1) * 100


# ================= AI ENGINE =================

def ai_signal(coin):
    price = get_price(coin)

    if not price:
        return "❌ No data", 0

    r = rsi(coin)
    m = macd_trend(coin)

    score = 50
    signal = "⚪ HOLD"

    if r < 30:
        signal = "🟢 STRONG BUY"
        score += 30
    elif r > 70:
        signal = "🔴 STRONG SELL"
        score += 30
    else:
        score += 10

    if m > 1:
        score += 15
    elif m < -1:
        score -= 15

    return (
        f"{signal}\n"
        f"📊 RSI: {int(r)}\n"
        f"📉 Trend: {m:.2f}%\n"
        f"🔥 Strength: {score}/100",
        score
    )


# ================= COMMANDS =================

@bot.message_handler(commands=['price'])
def price_cmd(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /price BTC")
        return

    coin = parts[1].lower()
    price = get_price(coin)

    if price:
        bot.reply_to(msg, f"💰 {coin.upper()} = ${price}")
    else:
        bot.reply_to(msg, f"❌ Coin not found: {', '.join(COINS.keys()).upper()}")


@bot.message_handler(commands=['signal'])
def signal_cmd(msg):
    parts = msg.text.split()

    if len(parts) < 2:
        bot.reply_to(msg, "Usage: /signal BTC")
        return

    coin = parts[1].lower()

    sig, score = ai_signal(coin)

    bot.reply_to(msg, f"🤖 {coin.upper()} SIGNAL\n\n{sig}")

    if score >= 80:
        bot.send_message(
            VIP_CHANNEL,
            f"🔥 VIP SIGNAL\n\n{coin.upper()}\n\n{sig}"
        )


@bot.message_handler(commands=['scan'])
def scan(msg):
    out = "📊 LEVEL 4 SCAN\n\n"

    for c in COINS.keys():
        sig, score = ai_signal(c)
        out += f"{c.upper()}: {score}/100\n"

        if score >= 80:
            bot.send_message(VIP_CHANNEL, f"🔥 VIP {c.upper()}\n\n{sig}")

        time.sleep(0.5)

    bot.send_message(msg.chat.id, out)


# ================= RUN FUNCTION (THIS IS WHAT YOU WERE MISSING) =================

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
            print(f"Polling error: {e}")
            time.sleep(5)


# ================= MAIN =================

if __name__ == "__main__":
    print("Starting application...")

    Thread(target=run, daemon=True).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
