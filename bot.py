from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = "7988782705:AAFS9c5D_v-o15b5hBJZmNXW4aol4BgtUf4"
CHANNEL = "@UltimateAvian"   # your channel username

# =========================
# CHECK JOIN STATUS
# =========================
async def is_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Join check error:", e)
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
            "🚀 To use this bot, you must join our channel first:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("🔥 Welcome! Bot is now active.")

# =========================
# CALLBACK BUTTON HANDLER
# =========================
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await is_joined(context, user_id):
        await query.edit_message_text("🔥 Verified! You can now use the bot.")
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/UltimateAvian")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
        ]
        await query.edit_message_text(
            "❌ You haven't joined yet. Please join the channel first:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
