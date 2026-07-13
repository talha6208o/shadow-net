import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')
ADMIN_ID = 6641244885
BOT_USERNAME = 'ShadowNetflix_bot'

# DATABASE PATH FIX: Railway mein /app/ data permanent hota hai
DB_PATH = '/app/hybrid_bot.db'

bot = telebot.TeleBot(TOKEN)
admin_states = {}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, pending_referrer INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_user_id INTEGER UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT, item_value TEXT, is_used INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS giveaway_participants (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(query, params)
        if fetch: result = c.fetchone()
        elif fetchall: result = c.fetchall()
        else: conn.commit(); result = True
    except Exception as e:
        print(f"DB Error: {e}"); result = None
    finally: conn.close()
    return result

# ... (Apna is_subscribed, get_user_points, aur baki handlers yahan paste kar dena) ...

# GIVEAWAY LIST VIEW FEATURE (Isse Callback handler mein add karo)
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

    elif data == "admin_reset_giveaway":
        if user_id != ADMIN_ID: return
        db_query("DELETE FROM giveaway_participants")
        bot.answer_callback_query(call.id, "✅ List Reset!")

    # Baki purane handlers yahan niche...
