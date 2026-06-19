import os
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4") or "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
CHANNEL = "@UltimateAvian"


# =========================
# COIN FUNCTIONS
# =========================
def get_price(coin: str):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin, "vs_currencies": "usd"}

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return data.get(coin, {}).get("usd")
    except:
        return None


def get_top_coins():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 5,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return []


def get_gainers():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "price_change_percentage_24h_desc",
            "per_page": 5,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return []


# =========================
# JOIN CHECK
# =========================
async def is_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_joined(context, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/UltimateAvian")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "🚀 Join our channel to use this bot:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "🔥 Crypto Bot Ready!\n\nCommands:\n/price bitcoin\n/top\n/gainers",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("BTC", callback_data="bitcoin"),
                InlineKeyboardButton("ETH", callback_data="ethereum"),
                InlineKeyboardButton("SOL", callback_data="solana"),
            ]
        ])
    )


# =========================
# PRICE COMMAND
# =========================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price bitcoin")
        return

    coin = context.args[0].lower()
    price = get_price(coin)

    if price:
        await update.message.reply_text(f"💰 {coin.upper()} = ${price}")
    else:
        await update.message.reply_text("❌ Coin not found")


# =========================
# TOP COINS
# =========================
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_top_coins()

    text = "🔥 TOP COINS:\n\n"

    for c in coins:
        text += f"{c['symbol'].upper()} = ${c['current_price']}\n"

    await update.message.reply_text(text)


# =========================
# GAINERS
# =========================
async def gainers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_gainers()

    text = "🚀 TOP GAINERS (24h):\n\n"

    for c in coins:
        text += f"{c['symbol'].upper()} +{c['price_change_percentage_24h']:.2f}%\n"

    await update.message.reply_text(text)


# =========================
# BUTTON CALLBACK
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    coin = query.data
    price = get_price(coin)

    if price:
        await query.edit_message_text(f"💰 {coin.upper()} = ${price}")
    else:
        await query.edit_message_text("❌ Error fetching price")


# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("gainers", gainers))

    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
