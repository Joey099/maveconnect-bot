import telebot
import requests
import time
import traceback

TOKEN = "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
bot = telebot.TeleBot(TOKEN)

# ========== PRICE FUNCTION ==========
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
                return float(data["price"])
    except Exception:
        print("BINANCE ERROR:")
        print(traceback.format_exc())

    return None


# ========== START COMMAND ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "👋 Send a coin symbol like:\nBTC\nETH\nSOL\nDOGE"
    )


# ========== PRICE HANDLER ==========
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        symbol = message.text.strip()
        price = get_price(symbol)

        if price:
            bot.reply_to(message, f"💰 {symbol.upper()} = ${price}")
        else:
            bot.reply_to(message, "❌ Coin not found. Try BTC, ETH, SOL, BNB, XRP, ADA, DOGE")

    except Exception:
        print(traceback.format_exc())
        bot.reply_to(message, "⚠️ Error processing request")


# ========== START BOT ==========
if __name__ == "__main__":
    try:
        print("🤖 Bot is running...")

        # IMPORTANT: prevents webhook conflicts
        bot.remove_webhook()

        # keeps bot alive on Render
        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception:
        print("FATAL ERROR:")
        print(traceback.format_exc())
        time.sleep(5)
