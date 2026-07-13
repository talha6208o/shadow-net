import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')
ADMIN_ID = 6641244885
bot = telebot.TeleBot(TOKEN)
admin_states = {}

# DATABASE FUNCTIONS
def db_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    try:
        c.execute(query, params)
        if fetch: result = c.fetchone()
        elif fetchall: result = c.fetchall()
        else: conn.commit(); result = True
    except: result = None
    finally: conn.close()
    return result

# CALLBACK HANDLER
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    user_id = call.from_user.id
    data = call.data

    if data == "admin_view_giveaway":
        if user_id != ADMIN_ID: return
        participants = db_query("SELECT user_id FROM giveaway_participants", fetchall=True)
        if not participants:
            return bot.answer_callback_query(call.id, "⚠️ List khali hai!", show_alert=True)
        
        text = "🎁 **Giveaway Participants List:**\n\n"
        for p in participants:
            text += f"👤 `ID: {p[0]}`\n"
        bot.send_message(user_id, text, parse_mode="Markdown")

    elif data.startswith("admin_"):
        if user_id != ADMIN_ID: return
        action = data.replace("admin_", "")
        
        if action == "reset_giveaway":
            db_query("DELETE FROM giveaway_participants")
            bot.answer_callback_query(call.id, "✅ List Reset!")

    # Yahan apne baki purane elif conditions add kar lena...

print("🔥 BOT IS RUNNING!")
bot.infinity_polling()
