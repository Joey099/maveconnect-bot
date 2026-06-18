from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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
                if "price" in data:
                    return float(data["price"])
    except:
        pass

    return None


@app.route("/price")
def price():
    symbol = request.args.get("symbol")
    result = get_price(symbol)

    if result:
        return jsonify({"symbol": symbol, "price": result})
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
