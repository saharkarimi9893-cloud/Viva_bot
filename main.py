import os
import telebot
import time  # برای ایجاد وقفه و تایمر
from flask import Flask, request

# --- [ Settings ] ---
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

ADMIN_USERNAMES = ['OYB1234', 'sahar143']
CHANNELS = ['old_love2024', 'tab_ib']
ALL_TYPES =

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

# --- [ Helper Functions ] ---
def is_admin(user):
    return user.username in ADMIN_USERNAMES

def check_join(user):
    if is_admin(user): return True
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{ch}", user.id).status
            if status in ['left', 'kicked']: return False
        except: continue
    return True

# --- [ Handlers ] ---

@bot.message_handler(content_types=ALL_TYPES)
def main_handler(message):
    # ری‌اکشن کبوتر سفید 🕊️ روی همه پیام‌ها
    try:
        bot.set_message_reaction(message.chat.id, message.message_id, [telebot.types.ReactionTypeEmoji('🕊')], is_big=False)
    except: pass

    if not check_join(message.from_user):
        return bot.send_message(message.chat.id, "🔒 لطفاً ابتدا عضو کانال‌ها شوید.")

    if message.text and "http" in message.text:
        # ۱. ارسال پیام اولیه
        sent_msg = bot.reply_to(message, "📥 لینک شناسایی شد! در حال آماده‌سازی... ⏳")
        
        # ۲. ایجاد تایمر نمایشی (۳ ثانیه)
        for i in range(3, 0, -1):
            time.sleep(1)
            try:
                bot.edit_message_text(f"🚀 در حال استخراج محتوا... {i} ثانیه مانده", message.chat.id, sent_msg.message_id)
            except: break
        
        # ۳. ارسال محتوا (ویدیو یا صوت)
        bot.send_chat_action(message.chat.id, 'upload_video')
        try:
            # پاک کردن پیام تایمر قبل از ارسال فایل اصلی
            bot.delete_message(message.chat.id, sent_msg.message_id)
            
            # در اینجا باید منطق دانلودر واقعی باشد، فعلاً از لینک مستقیم استفاده می‌شود
            bot.send_video(message.chat.id, video=message.text, caption="✅ ویدیوی شما آماده شد! 🕊️")
        except:
            bot.send_message(message.chat.id, "❌ خطایی در بارگذاری رخ داد. مطمئن شوید لینک مستقیم ویدیو است.")

    elif message.text == "/start":
        bot.send_message(message.chat.id, "👋 خوش آمدید! لینک یا آهنگ مورد نظرتان را بفرستید.")

# --- [ Server Logic ] ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home(): return "Viva Bot Timer Active!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
