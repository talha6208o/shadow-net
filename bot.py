# [Zaroori Imports aur Settings pehle jaisi hi rahengi]

# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect('hybrid_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, pending_referrer INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_user_id INTEGER UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT, item_value TEXT, is_used INTEGER DEFAULT 0)''')
    # Naya Table
    c.execute('''CREATE TABLE IF NOT EXISTS giveaway_participants (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

# ================= GIVEAWAY LOGIC =================
@bot.callback_query_handler(func=lambda call: call.data == "join_giveaway")
def join_giveaway(call):
    user_id = call.from_user.id
    if not is_subscribed(user_id):
        return bot.answer_callback_query(call.id, "⚠️ Join channel/group first!", show_alert=True)
    
    try:
        db_query("INSERT INTO giveaway_participants (user_id) VALUES (?)", (user_id,))
        bot.answer_callback_query(call.id, "🎉 Successfully joined the giveaway!", show_alert=True)
    except:
        bot.answer_callback_query(call.id, "✅ You are already in the giveaway!", show_alert=True)

# ================= ADMIN DASHBOARD (UPDATED) =================
def show_admin_panel(chat_id):
    # ... (purane stats)
    markup = InlineKeyboardMarkup(row_width=2)
    # Giveaway wale buttons
    markup.add(
        InlineKeyboardButton("🎁 Reset Giveaway", callback_data="admin_reset_giveaway"),
        InlineKeyboardButton("📢 Giveaway Broadcast", callback_data="admin_giveaway_broadcast")
    )
    # ... (baki buttons)
    bot.send_message(chat_id, "👑 Admin Panel", reply_markup=markup)

# ================= CALLBACK HANDLERS =================
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    # ... (purane handlers)
    
    if call.data == "admin_reset_giveaway":
        db_query("DELETE FROM giveaway_participants")
        bot.answer_callback_query(call.id, "✅ Giveaway list reset! Fresh start.", show_alert=True)
    
    elif call.data == "admin_giveaway_broadcast":
        admin_states[call.from_user.id] = "giveaway_broadcast"
        bot.send_message(call.message.chat.id, "📢 Send the content for Giveaway Broadcast:")
        bot.register_next_step_handler(call.message, process_giveaway_broadcast)

# ================= GIVEAWAY BROADCAST =================
def process_giveaway_broadcast(message):
    participants = db_query("SELECT user_id FROM giveaway_participants", fetchall=True)
    if not participants:
        return bot.reply_to(message, "⚠️ Giveaway list khali hai!")
        
    bot.reply_to(message, f"⏳ Broadcasting to {len(participants)} participants...")
    
    success, fail = 0, 0
    for user in participants:
        try:
            bot.copy_message(user[0], message.chat.id, message.message_id)
            success += 1
            time.sleep(0.05)
        except: fail += 1
            
    bot.send_message(message.chat.id, f"✅ Done!\nSent: {success}\nFailed: {fail}")
