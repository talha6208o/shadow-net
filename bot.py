import telebot
import sqlite3
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')
ADMIN_ID = 6641244885
bot = telebot.TeleBot(TOKEN)

# DATABASE FUNCTIONS
def db_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    try:
        c.execute(query, params)
        if fetch: result = c.fetchone()
        elif fetchall: result = c.fetchall()
        else: conn.commit(); result = True
    except Exception as e: 
        print(f"DB Error: {e}")
        result = None
    finally: conn.close()
    return result

# CALLBACK HANDLER
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    user_id = call.from_user.id
    data = call.data

    # Giveaway View Feature
    if data == "admin_view_giveaway":
        if user_id != ADMIN_ID: return
        participants = db_query("SELECT user_id FROM giveaway_participants", fetchall=True)
        if not participants:
            return bot.answer_callback_query(call.id, "⚠️ List khali hai!", show_alert=True)
        
        text = "🎁 **Giveaway Participants List:**\n\n"
        for p in participants:
            text += f"👤 `ID: {p[0]}`\n"
        bot.send_message(user_id, text, parse_mode="Markdown")

    # Admin Reset Feature
    elif data == "admin_reset_giveaway":
        if user_id != ADMIN_ID: return
        db_query("DELETE FROM giveaway_participants")
        bot.answer_callback_query(call.id, "✅ List Reset!")

    # Purane features yahan wapas daal lo
    elif data == "join_giveaway":
        db_query("INSERT OR IGNORE INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
        bot.answer_callback_query(call.id, "🎉 Joined Giveaway!")
    
    # ... (yahan apne baki redeem wale elif daal dena) ...

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "✅ Bot is working! Use buttons to proceed.")

print("🔥 BOT IS RUNNING!")
bot.infinity_polling()
