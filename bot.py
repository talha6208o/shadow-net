import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= SECURE SETTINGS =================
TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')  
ADMIN_ID = 6641244885          
BOT_USERNAME = 'ShadowNetflix_bot'

# BOT INITIALIZATION (Sabse zaroori: Isse imports ke baad hona chahiye)
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
        else:
            conn.commit()
            result = True
    except Exception as e:
        print(f"DB Error: {e}")
        result = None
    finally:
        conn.close()
    return result

# ================= HELPERS =================
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        # Check channel and group
        m1 = bot.get_chat_member('@Shadow_cipher0', user_id)
        m2 = bot.get_chat_member('@Shadow_cipher00', user_id)
        valid = ['member', 'administrator', 'creator']
        return m1.status in valid and m2.status in valid
    except: return False

def get_giveaway_count():
    count = db_query("SELECT COUNT(*) FROM giveaway_participants", fetch=True)
    return count[0] if count else 0

# ================= COMMANDS =================
@bot.message_handler(commands=['start'])
def start_menu(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Join Channel", url='https://t.me/Shadow_cipher0'))
        markup.add(InlineKeyboardButton("💬 Join Group", url='https://t.me/Shadow_cipher00'))
        markup.add(InlineKeyboardButton("✅ Check Subscription", callback_data="check_sub"))
        bot.send_message(user_id, "🛑 **Access Denied!** Join Channel & Group first.", reply_markup=markup)
        return
    
    # Dash board logic
    bot.send_message(user_id, "👋 Welcome! Use the buttons below.", reply_markup=main_menu_markup())

def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 Join Giveaway", callback_data="join_giveaway"))
    markup.add(InlineKeyboardButton("🔄 Refresh Points", callback_data="refresh"))
    return markup

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    user_id = call.from_user.id
    
    if call.data == "join_giveaway":
        if not is_subscribed(user_id):
            bot.answer_callback_query(call.id, "⚠️ Join Channel/Group first!", show_alert=True)
            return
        try:
            db_query("INSERT INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
            bot.answer_callback_query(call.id, "🎉 Joined Giveaway!", show_alert=True)
        except:
            bot.answer_callback_query(call.id, "✅ Already Joined!", show_alert=True)

    elif call.data == "admin_reset_giveaway":
        if user_id == ADMIN_ID:
            db_query("DELETE FROM giveaway_participants")
            bot.answer_callback_query(call.id, "✅ Giveaway List Reset!", show_alert=True)

    elif call.data == "admin_stats":
        if user_id == ADMIN_ID:
            count = get_giveaway_count()
            bot.send_message(user_id, f"🎁 **Giveaway Participants:** {count}")

# ================= RUN =================
print("🔥 BOT IS RUNNING! 🔥")
bot.infinity_polling()
