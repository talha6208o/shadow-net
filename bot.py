import telebot
import sqlite3
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ... (Upar ka saara code waisa hi hai, bas niche wale handlers change kiye hain) ...
# [Yahan wahi sab code hai jo aapne bheja tha, main sirf 'show_admin_panel' aur 'handle_clicks' update kar raha hoon]

def show_admin_panel(chat_id):
    net_stock = db_query("SELECT COUNT(*) FROM stock WHERE item_type='netflix' AND is_used=0", fetch=True)[0]
    prime_stock = db_query("SELECT COUNT(*) FROM stock WHERE item_type='prime' AND is_used=0", fetch=True)[0]
    spot_stock = db_query("SELECT COUNT(*) FROM stock WHERE item_type='spotify' AND is_used=0", fetch=True)[0]
    total_users = db_query("SELECT COUNT(*) FROM users", fetch=True)[0]
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Netflix", callback_data="admin_add_netflix"),
        InlineKeyboardButton("🗑 Clear Netflix", callback_data="admin_clear_netflix"),
        InlineKeyboardButton("➕ Add Prime", callback_data="admin_add_prime"),
        InlineKeyboardButton("🗑 Clear Prime", callback_data="admin_clear_prime"),
        InlineKeyboardButton("➕ Add Spotify", callback_data="admin_add_spotify"),
        InlineKeyboardButton("🗑 Clear Spotify", callback_data="admin_clear_spotify")
    )
    markup.add(
        InlineKeyboardButton("🎁 Reset Giveaway", callback_data="admin_reset_giveaway"),
        InlineKeyboardButton("📢 Giveaway Broadcast", callback_data="admin_giveaway_broadcast")
    )
    markup.add(InlineKeyboardButton("🎁 View Giveaway List", callback_data="admin_view_giveaway")) # NAYA BUTTON
    markup.add(InlineKeyboardButton("📢 Custom Broadcast", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("🏆 Leaderboard Stats", callback_data="admin_stats"))
    
    text = (
        "👑 **ADMIN CONTROL DASHBOARD** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Total Joined Users:** `{total_users}` Users\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎬 **Netflix:** `{net_stock}` | 🍿 **Prime:** `{prime_stock}` | 🎵 **Spotify:** `{spot_stock}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 **Admin options:**"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# Callback Handler mein ye naya part add karo:
    elif action == "view_giveaway_list":
        participants = db_query("SELECT user_id FROM giveaway_participants", fetchall=True)
        if not participants:
            return bot.answer_callback_query(call.id, "⚠️ List khali hai!", show_alert=True)
        
        text = "🎁 **Giveaway Participants (IDs):**\n\n"
        for p in participants:
            text += f"👤 `ID: {p[0]}`\n"
        bot.send_message(user_id, text, parse_mode="Markdown")

# ... (Baki ka code same rahega) ...
