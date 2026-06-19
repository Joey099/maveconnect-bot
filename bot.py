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
# COIN API (SAFE)
# =========================
def get_price(coin: str):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin.lower(), "vs_currencies": "usd"}

        r = requests.get(url, params=params, timeout=10)
        return r.json().get(coin.lower(), {}).get("usd")
    except:
        return None


# =========================
# JOIN CHECK (SAFE)
# =========================
async def is_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_joined(context, user_id):
        await update.message.reply_text(
            "🚀 Join channel first:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join", url="https://t.me/UltimateAvian")],
                [InlineKeyboardButton("I Joined", callback_data="check")]
            ])
        )
        return

    await update.message.reply_text(
        "🔥 Crypto Bot Ready\nUse /price bitcoin",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("BTC", callback_data="bitcoin"),
                InlineKeyboardButton("ETH", callback_data="ethereum"),
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

    coin = context.args[0]
    price = get_price(coin)

    if price:
        await update.message.reply_text(f"💰 {coin.upper()} = ${price}")
    else:
        await update.message.reply_text("❌ Coin not found")


# =========================
# CALLBACK BUTTONS
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
# MAIN (3.14 SAFE MODE)
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 Running on Python 3.14 safe mode")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
