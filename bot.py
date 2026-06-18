import requests

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

    # ========== 1. BINANCE ==========
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

    except Exception as e:
        print("BINANCE FAIL:", e)

    # ========== 2. COINGECKO ==========
    try:
        mapping = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "bnb": "binancecoin",
            "xrp": "ripple",
            "ada": "cardano",
            "doge": "dogecoin"
        }

        coin = mapping.get(symbol)

        if coin:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": coin, "vs_currencies": "usd"},
                timeout=5
            )

            if r.status_code == 200:
                data = r.json()
                return data.get(coin, {}).get("usd")

    except Exception as e:
        print("COINGECKO FAIL:", e)

    # ========== 3. CRYPTOCOMPARE ==========
    try:
        r = requests.get(
            "https://min-api.cryptocompare.com/data/price",
            params={"fsym": symbol.upper(), "tsyms": "USD"},
            timeout=5
        )

        if r.status_code == 200:
            data = r.json()
            return data.get("USD")

    except Exception as e:
        print("CRYPTOCOMPARE FAIL:", e)

    return None
