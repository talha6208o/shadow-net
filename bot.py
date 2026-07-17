elif call.data.startswith("redeem_"):

    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "⚠️ Access Denied! You left the group/channel.", show_alert=True)
        return

    item_type = call.data.replace("redeem_", "")
    points = get_user_points(user_id)

    if points < 30:
        bot.answer_callback_query(call.id, f"⚠️ You need 25 points to redeem! (Current: {points})", show_alert=True)
        return

    stock_data = db_query("SELECT id, item_value FROM stock WHERE item_type=? AND is_used=0 LIMIT 1", (item_type,), fetch=True)

    if stock_data:
        item_id, item_val = stock_data
        db_query("UPDATE stock SET is_used=1 WHERE id=?", (item_id,))

        referred_users = db_query("SELECT referred_user_id FROM referrals WHERE referrer_id=? LIMIT 5", (user_id,), fetchall=True)

        for ref in referred_users:
            db_query("DELETE FROM referrals WHERE referred_user_id=?", (ref[0],))

        bot.send_message(
            user_id,
            f"🎉 **REDEEM SUCCESSFUL!** 🎉\n\n🎁 **Your {item_type.capitalize()} Reward:**\n`{item_val}`\n\nThank you for inviting real members! ❤️",
            parse_mode="Markdown"
        )

        bot.answer_callback_query(call.id, "Reward Claimed!", show_alert=True)

    else:
        bot.answer_callback_query(
            call.id,
            f"⚠️ {item_type.capitalize()} is currently out of stock! Admin will restock soon.",
            show_alert=True
        )
