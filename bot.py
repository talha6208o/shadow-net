import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')  
ADMIN_ID = 6641244885          
BOT_USERNAME = 'ShadowNetflix_bot'

bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT, item_value TEXT, is_used INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS giveaway_participants (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=False, fetchall=False):
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    try:
        c.execute(query, params)
        if fetch: result = c.fetchone()
        elif fetchall: result = c.fetchall()
        else:
            conn.commit()
            result = True
    except: result = None
    finally: conn.close()
    return result

def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        m1 = bot.get_chat_member('@Shadow_cipher0', user_id)
        m2 = bot.get_chat_member('@Shadow_cipher00', user_id)
        return m1.status in ['member', 'administrator', 'creator'] and m2.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Channel", url='https://t.me/Shadow_cipher0'))
        markup.add(InlineKeyboardButton("💬 Join Group", url='https://t.me/Shadow_cipher00'))
        markup.add(InlineKeyboardButton("✅ Check Subscription", callback_data="check_sub"))
        bot.send_message(user_id, "🛑 Join Channel & Group first!", reply_markup=markup)
        return
    
    # Main Menu
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 Netflix", callback_data="redeem_netflix"), InlineKeyboardButton("🍿 Prime", callback_data="redeem_prime"))
    markup.add(InlineKeyboardButton("🎁 Join Giveaway", callback_data="join_giveaway"))
    bot.send_message(user_id, "👋 Welcome back! Select an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    user_id = call.from_user.id
    if call.data == "join_giveaway":
        db_query("INSERT OR IGNORE INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
        bot.answer_callback_query(call.id, "🎉 You joined the giveaway!")
    
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        count = db_query("SELECT COUNT(*) FROM giveaway_participants", fetch=True)[0]
        bot.send_message(user_id, f"🎁 Giveaway Participants: {count}")

    elif call.data.startswith("redeem_"):
        bot.answer_callback_query(call.id, "Checking stock...", show_alert=True)
        # Baki ka redeem logic yahan wapas daal do

print("🔥 BOT RUNNING...")
bot.infinity_polling()
