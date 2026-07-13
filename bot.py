import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= SECURE SETTINGS =================
TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')  
ADMIN_ID = 6641244885          
BOT_USERNAME = 'ShadowNetflix_bot'

bot = telebot.TeleBot(TOKEN)
admin_states = {}

# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, pending_referrer INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_user_id INTEGER UNIQUE)''')
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
        else: conn.commit(); result = True
    except: result = None
    finally: conn.close()
    return result

# ================= FUNCTIONS =================
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        m1 = bot.get_chat_member('@Shadow_cipher0', user_id)
        m2 = bot.get_chat_member('@Shadow_cipher00', user_id)
        return m1.status in ['member', 'administrator', 'creator'] and m2.status in ['member', 'administrator', 'creator']
    except: return False

def get_user_points(user_id):
    refs = db_query("SELECT referred_user_id FROM referrals WHERE referrer_id=?", (user_id,), fetchall=True)
    if not refs: return 0
    return sum(1 for r in refs if is_subscribed(r[0])) * 5

# ================= START & DASHBOARD =================
@bot.message_handler(commands=['start'])
def start_menu(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Channel", url='https://t.me/Shadow_cipher0'))
        markup.add(InlineKeyboardButton("💬 Join Group", url='https://t.me/Shadow_cipher00'))
        markup.add(InlineKeyboardButton("✅ I Have Joined", callback_data="check_sub"))
        bot.send_message(user_id, "🛑 Access Denied! Join both first.", reply_markup=markup)
        return
    show_main_dashboard(user_id, message.from_user.first_name)

def show_main_dashboard(user_id, first_name):
    points = get_user_points(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎬 Netflix (25 pts)", callback_data="redeem_netflix"), InlineKeyboardButton("🍿 Prime (25 pts)", callback_data="redeem_prime"))
    markup.add(InlineKeyboardButton("🎁 Join Giveaway", callback_data="join_giveaway"), InlineKeyboardButton("🔄 Refresh", callback_data="refresh"))
    text = f"👋 Welcome {first_name}!\n💰 Balance: {points} Points\n🔗 Link: {ref_link}"
    bot.send_message(user_id, text, reply_markup=markup)

# ================= CALLBACKS & GIVEAWAY =================
@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    user_id = call.from_user.id
    if call.data == "join_giveaway":
        db_query("INSERT OR IGNORE INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
        bot.answer_callback_query(call.id, "🎉 Joined Giveaway!")
    
    elif call.data == "admin_reset_giveaway" and user_id == ADMIN_ID:
        db_query("DELETE FROM giveaway_participants")
        bot.answer_callback_query(call.id, "✅ Reset!")
        
    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        count = db_query("SELECT COUNT(*) FROM giveaway_participants", fetch=True)[0]
        bot.send_message(user_id, f"🎁 Total Giveaway Participants: {count}")
    
    # Baki aapke purane redeem handlers yahan aa jayenge...

print("🔥 BOT IS RUNNING! 🔥")
bot.infinity_polling()
