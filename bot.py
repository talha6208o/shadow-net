import telebot
import os
import pymongo
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8629212279:AAF7rgLbU7SLYG64Mli2hupmGZENxbmNg24')
ADMIN_ID = 6641244885
BOT_USERNAME = 'ShadowNetflix_bot'

# MONGODB CONNECTION (Data permanent rahega)
MONGO_URI = os.getenv('MONGO_DB_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client['shadow_bot_db']
users_col = db['users']
referrals_col = db['referrals']
stock_col = db['stock']
giveaway_col = db['giveaway_participants']

bot = telebot.TeleBot(TOKEN)
admin_states = {}

# --- HELPER FUNCTIONS ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        m1 = bot.get_chat_member('@Shadow_cipher0', user_id)
        m2 = bot.get_chat_member('@Shadow_cipher00', user_id)
        return m1.status in ['member', 'administrator', 'creator'] and m2.status in ['member', 'administrator', 'creator']
    except: return False

def get_user_points(user_id):
    refs = list(referrals_col.find({'referrer_id': user_id}))
    valid_count = sum(1 for r in refs if is_subscribed(r['referred_user_id']))
    return valid_count * 5

# --- ADMIN PANEL ---
def show_admin_panel(chat_id):
    net_stock = stock_col.count_documents({'item_type': 'netflix', 'is_used': 0})
    prime_stock = stock_col.count_documents({'item_type': 'prime', 'is_used': 0})
    spot_stock = stock_col.count_documents({'item_type': 'spotify', 'is_used': 0})
    total_users = users_col.count_documents({})
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Netflix", callback_data="admin_add_netflix"),
        InlineKeyboardButton("🗑 Clear Netflix", callback_data="admin_clear_netflix"),
        InlineKeyboardButton("🎁 View Giveaway List", callback_data="admin_view_giveaway"),
        InlineKeyboardButton("🎁 Reset Giveaway", callback_data="admin_reset_giveaway")
    )
    markup.add(InlineKeyboardButton("🏆 Leaderboard Stats", callback_data="admin_stats"))
    
    text = f"👑 **ADMIN DASHBOARD**\n👥 Users: {total_users}\n🎬 Netflix: {net_stock}\n🍿 Prime: {prime_stock}"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    user_id = call.from_user.id
    
    if call.data == "admin_view_giveaway":
        if user_id != ADMIN_ID: return
        participants = list(giveaway_col.find({}))
        if not participants: return bot.answer_callback_query(call.id, "List khali hai!")
        text = "🎁 **Giveaway Participants:**\n" + "\n".join([f"`ID: {p['user_id']}`" for p in participants])
        bot.send_message(user_id, text, parse_mode="Markdown")

    elif call.data == "admin_reset_giveaway":
        if user_id != ADMIN_ID: return
        giveaway_col.delete_many({})
        bot.answer_callback_query(call.id, "✅ Reset!")
        
    elif call.data == "join_giveaway":
        if not is_subscribed(user_id): return bot.answer_callback_query(call.id, "Join channel first!")
        giveaway_col.update_one({'user_id': user_id}, {'$set': {'user_id': user_id}}, upsert=True)
        bot.answer_callback_query(call.id, "🎉 Joined!")

    # Baki buttons ka logic yahan append karte jao...

@bot.message_handler(commands=['start', 'admin'])
def commands(message):
    if message.text == '/start':
        # Yahan apna purana /start ka logic daal do
        bot.reply_to(message, "Welcome!")
    elif message.text == '/admin' and message.from_user.id == ADMIN_ID:
        show_admin_panel(message.chat.id)

print("🔥 BOT RUNNING WITH MONGODB!")
bot.infinity_polling()
