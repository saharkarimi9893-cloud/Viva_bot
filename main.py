import os
import telebot
from flask import Flask, request

# --- [ تنظیمات / Settings ] ---
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

CHANNELS = ['old_love2024', 'tab_ib']
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

@app.route('/')
def home(): 
    return "Viva Bot is High Speed & Online!", 200

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Forbidden", 403

# --- [ تابع چک کردن عضویت اجباری ] ---
def check_join(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{channel}", user_id).status
            if status == 'left':
                return False
        except:
            continue
    return True

# --- [ ہینڈلرز / Handlers ] ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_join(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(telebot.types.InlineKeyboardButton(f"Join {ch}", url=f"https://t.me{ch}"))
        markup.add(telebot.types.InlineKeyboardButton("✅ عضو شدم / Joined", url=f"https://t.me{bot.get_me().username}?start=true"))
        return bot.send_message(message.chat.id, "❌ **لطفاً ابتدا عضو کانال‌های ما شوید:**", reply_markup=markup)

    welcome_text = (
        "🔥 **𝙑𝙄𝙑𝘼 𝙂𝙇𝙊𝘽𝘼𝙇 𝘽𝙊𝙏** 🔥\n"
        "━━━━━━━━━━━━━━\n"
        "👋 سلام! به پیشرفته‌ترین دستیار هوشمند خوش‌آمدی\n"
        "نام آهنگ را بفرستید یا لینک را وارد کنید."
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if "http" in message.text:
        bot.reply_to(message, "📥 لینک شناسایی شد! در حال آماده‌سازی...")
    else:
        # شبیه‌سازی پیدا شدن آهنگ
        song_name = message.text
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎵 دریافت آهنگ (MP3)", callback_data=f"dl_{song_name}"))
        bot.send_message(message.chat.id, f"🎧 آهنگ **{song_name}** پیدا شد!", reply_markup=markup)

if __name__ == '__main__':
    # تنظیم وب‌هوک
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
