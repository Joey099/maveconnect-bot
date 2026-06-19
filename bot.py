import os
import asyncio
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
# COIN API
# =========================
def get_price(coin: str):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        r = requests.get(url, params={"ids": coin.lower(), "vs_currencies": "usd"}, timeout=10)
        return r.json().get(coin.lower(), {}).get("usd")
    except:
        return None


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

    await update.message.reply_text("🔥 Bot running on Python 3.14")


# =========================
# PRICE
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
        await update.message.reply_text("❌ Not found")


# =========================
# BUTTON
# =========================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    coin = query.data
    price = get_price(coin)

    if price:
        await query.edit_message_text(f"💰 {coin.upper()} = ${price}")
    else:
        await query.edit_message_text("❌ Error")


# =========================
# BUILD APP
# =========================
def build_app():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CallbackQueryHandler(button))

    return app


# =========================
# PYTHON 3.14 FIX LOOP RUNNER
# =========================
async def run():
    app = build_app()

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("🚀 Bot running on Python 3.14 (fixed loop mode)")

    await asyncio.Event().wait()  # keep alive


if __name__ == "__main__":
    asyncio.run(run())
