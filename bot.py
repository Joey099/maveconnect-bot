import telebot
import requests

TOKEN = "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
bot = telebot.TeleBot(TOKEN)

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

    pair = binance_map.get(symbol)

    if pair:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": pair},
            timeout=5
        )
        if r.status_code == 200:
            return r.json().get("price")

    return None


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send a coin like btc, eth, sol")

@bot.message_handler(func=lambda m: True)
def handle(message):
    price = get_price(message.text)

    if price:
        bot.reply_to(message, f"{message.text.upper()} = ${price}")
    else:
        bot.reply_to(message, "Coin not found")

print("Bot running...")
bot.infinity_polling()
