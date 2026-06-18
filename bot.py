from flask import Flask, request
import requests
import os

TOKEN = "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)


# =====================
# SEND MESSAGE
# =====================
def send(chat_id, text):
    try:
        requests.get(
            BASE_URL + "sendMessage",
            params={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except Exception as e:
        print("SEND ERROR:", e)


# =====================
# PRICE ENGINE (BINANCE + CRYPTOCOMPARE)
# =====================
def get_price(symbol):
    symbol = symbol.lower().strip()

    # ---------------- BINANCE MAP ----------------
    binance_map = {
        "btc": "BTCUSDT",
        "eth": "ETHUSDT",
        "sol": "SOLUSDT",
        "bnb": "BNBUSDT",
        "xrp": "XRPUSDT",
        "ada": "ADAUSDT",
        "doge": "DOGEUSDT",
        "ltc": "LTCUSDT",
        "dot": "DOTUSDT"
    }

    pair = binance_map.get(symbol)

    # ========== 1. TRY BINANCE ==========
    if pair:
        try:
            r = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={"symbol": pair},
                timeout=8
            )
            data = r.json()
            if "price" in data:
                return float(data["price"])
        except Exception as e:
            print("BINANCE ERROR:", e)

    # ========== 2. CRYPTOCOMPARE FALLBACK ==========
    try:
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price",
            params={"fsym": symbol.upper(), "tsyms": "USD"},
            timeout=8
        )

        data = r.json()
        print("CRYPTOCOMPARE:", data)

        if "USD" in data:
            return data["USD"]

    except Exception as e:
        print("CRYPTOCOMPARE ERROR:", e)

    return None


# =====================
# HOME ROUTE
# =====================
@app.route("/")
def home():
    return "🚀 Maveconnect Bot is running!"


# =====================
# WEBHOOK
# =====================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return "ok"

        message = data.get("message")
        if not message:
            return "ok"

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        print("MESSAGE:", text)

        # -------- START --------
        if text == "/start":
            send(chat_id,
                "🚀 Maveconnect Crypto Bot\n\n"
                "Commands:\n"
                "/token btc\n"
                "/token eth\n"
                "/token sol"
            )

        # -------- HELP --------
        elif text == "/help":
            send(chat_id,
                "📊 Commands:\n"
                "/token btc\n"
                "/token eth\n"
                "/token sol\n"
                "/token doge"
            )

        # -------- TOKEN PRICE --------
        elif text.lower().startswith("/token"):
            parts = text.split()

            if len(parts) < 2:
                send(chat_id, "Usage: /token btc")
                return "ok"

            symbol = parts[1]
            price = get_price(symbol)

            if price is not None:
                send(chat_id,
                    f"🪙 {symbol.upper()}\n"
                    f"💰 Price: ${price}"
                )
            else:
                send(chat_id,
                    "⚠️ Price unavailable. Try again in a moment."
                )

        # -------- DEFAULT --------
        else:
            send(chat_id, "Use /help to see commands.")

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return "ok"


# =====================
# RUN APP (RENDER)
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
