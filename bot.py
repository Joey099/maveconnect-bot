import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

#================= CONFIG =================

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

#================= COINS =================

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

#================= SMART CACHE =================

price_cache = {}

def get_price(coin):
    coin = coin.lower().strip()

coin_id = COINS.get(coin)  
if not coin_id:  
    return None  

# CACHE (5 sec)  
now = time.time()  
if coin in price_cache and now - price_cache[coin]["time"] < 1:  
    return price_cache[coin]["price"]  

url = "https://api.coingecko.com/api/v3/simple/price"  

try:  
    r = requests.get(url, params={  
        "ids": coin_id,  
        "vs_currencies": "usd"  
    }, timeout=10)  

    data = r.json()  

    price = data.get(coin_id, {}).get("usd")  

    if price:  
        price_cache[coin] = {"price": price, "time": now}  

    return price  

except:  
    return None

#================= RSI (REAL VERSION) =================

def rsi(coin, period=7):
prices = []

for _ in range(period + 1):  
    p = get_price(coin)  
    if p:  
        prices.append(p)  
    time.sleep(0.5)  

if len(prices) < period:  
    return 50  

gains = 0  
losses = 0  

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

#================= MACD STYLE TREND =================

def macd_trend(coin):
    p1 = get_price(coin)
    time.sleep(1)
    p2 = get_price(coin)

if not p1 or not p2:  
    return 0  

return ((p2 - p1) / p1) * 100

================= LEVEL 4 AI ENGINE =================

def ai_signal(coin):
    price = get_price(coin)
if not price:
    return "❌ No data", 0

r = rsi(coin)  
m = macd_trend(coin)  

score = 50  

signal = "⚪ HOLD"  

# RSI logic  
if r < 30:  
    signal = "🟢 STRONG BUY"  
    score += 30  
elif r > 70:  
    signal = "🔴 STRONG SELL"  
    score += 30  
else:  
    score += 10  

# MACD trend confirmation  
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

#================= VIP SYSTEM =================

def send_vip(coin, sig, score):
if score >= 80:
bot.send_message(
VIP_CHANNEL,
f"🔥 LEVEL 4 VIP SIGNAL\n\n"
f"{coin.upper()}\n\n"
f"{sig}\n\n"
f"🤖 AI Confidence: {score}/100"
)

#================= COMMANDS =================

@bot.message_handler(commands=['price'])
def price_cmd(msg):
try:
parts = msg.text.split()

if len(parts) < 2:  
        bot.reply_to(msg, "Usage: /price BTC")  
        return  

    coin = parts[1].lower()  
    p = get_price(coin)  

    if p:  
        bot.reply_to(msg, f"💰 {coin.upper()} = ${p}")  
    else:  
        bot.reply_to(  
            msg,  
            f"❌ Coin not found.\nSupported: {', '.join(COINS.keys()).upper()}"  
        )  

except Exception as e:  
    print(f"Price error: {e}")  
    bot.reply_to(msg, "⚠️ Error checking price")
@bot.message_handler(commands=['signal'])
def signal_cmd(msg):
    try:
        parts = msg.text.split()

        if len(parts) < 2:
            bot.reply_to(msg, "Usage: /signal BTC")
            return

        coin = parts[1].lower()

        sig, score = ai_signal(coin)

        bot.reply_to(
            msg,
            f"🤖 {coin.upper()} SIGNAL\n\n{sig}"
        )

        send_vip(coin, sig, score)

    except Exception as e:
        print(f"Signal error: {e}")
        bot.reply_to(msg, "⚠️ Error generating signal")

@bot.message_handler(commands=['scan'])
def scan(msg):
    out = "📊 LEVEL 4 SCAN\n\n"

for c in COINS.keys():  
    sig, score = ai_signal(c)  

    out += f"{c.upper()}: {score}/100\n"  

    send_vip(c, sig, score)  
    time.sleep(0.8)  

bot.send_message(msg.chat.id, out)

#================= MAIN =================
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
if __name__ == "__main__":
    print("Starting application...")

try:  
    bot.remove_webhook()  
    print("Webhook removed")  
except Exception as e:  
    print(f"Webhook error: {e}")  

     time.sleep(2)  

    polling_thread = Thread(target=run, daemon=True)  
    polling_thread.start()  

print("Polling thread started")  

app.run(  
    host="0.0.0.0",  
    port=int(os.environ.get("PORT", 5000))  
)
