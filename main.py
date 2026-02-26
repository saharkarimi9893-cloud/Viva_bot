import os
import telebot
from flask import Flask, request
from telebot import types

# --- [ Settings ] ---
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

ADMIN_USERNAMES = ['OYB1234', 'sahar143']
CHANNELS = ['old_love2024', 'tab_ib']

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# تابع چک کردن عضویت (ربات باید در کانال‌ها ادمین باشد)
def check_join(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{ch}", user_id).status
            if status in ['left', 'kicked']: return False
        except:
            return False 
    return True

# دکمه‌های عضویت با لینک اصلاح شده
def get_join_keyboard():
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(text=f"📢 Join {ch}", url=f"https://t.me{ch}"))
    markup.add(types.InlineKeyboardButton(text="✅ Verify Membership", callback_data="check_membership"))
    return markup

# --- [ Handlers ] ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id, "👋 Please join our channels to use the bot:", reply_markup=get_join_keyboard())
    else:
        bot.send_message(message.chat.id, "🚀 Bot is active! Send me a direct video or audio link.")

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_callback(call):
    if check_join(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified!")
        bot.edit_message_text("🔓 Access granted. Send your link now:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined yet!", show_alert=True)

# مدیریت لینک‌ها با پیام درخواستی شما
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def link_handler(message):
    if not check_join(message.from_user.id):
        return bot.send_message(message.chat.id, "⚠️ Join first:", reply_markup=get_join_keyboard())

    # تغییر پیام به انگلیسی طبق درخواست شما
    sent_msg = bot.reply_to(message, "⏳ Just a second...")
    
    try:
        bot.send_chat_action(message.chat.id, 'upload_video')
        # ارسال مستقیم (فقط لینک‌های مستقیم فایل)
        bot.send_video(message.chat.id, video=message.text, caption="✅ Done! 🕊️")
        bot.delete_message(message.chat.id, sent_msg.message_id)
    except:
        bot.edit_message_text("❌ Error: Invalid link or file too large.", message.chat.id, sent_msg.message_id)

# --- [ Webhook & Server ] ---

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home(): return "Viva Bot is Running!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    import time
    time.sleep(1)
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
