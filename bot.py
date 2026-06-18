from flask import Flask, request
import requests
import os

TOKEN = "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)


def send(chat_id, text):
    try:
        requests.get(
            BASE_URL + "sendMessage",
            params={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print("SEND ERROR:", e)


def get_price(symbol):
    mapping = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "bnb": "binancecoin",
        "xrp": "ripple"
    }

    coin = mapping.get(symbol.lower())
    if not coin:
        return None

    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin, "vs_currencies": "usd"},
            timeout=10
        )

        data = r.json()
        return data.get(coin, {}).get("usd")

    except:
        return None


@app.route("/")
def home():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "ok"

    message = data.get("message")
    if not message:
        return "ok"

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text == "/start":
        send(chat_id, "🚀 Bot is live!")

    elif text.startswith("/btc"):
        parts = text.split()

        if len(parts) < 2:
            send(chat_id, "Usage: /btc BTC")
        else:
            price = get_price(parts[1])

            if price:
                send(chat_id, f"💰 Price: ${price}")
            else:
                send(chat_id, "Price unavailable")

    else:
        send(chat_id, "Use /btc BTC")

    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
