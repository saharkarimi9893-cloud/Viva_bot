import os
import telebot
from flask import Flask, request

# --- [ تنظیمات / Settings ] ---
# ⚠️ مهم: حتماً توکن خود را در BotFather ریست کنید (Revoke) چون قبلاً لو رفته است.
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

ADMIN_USERNAMES = ['OYB1234', 'sahar143']
CHANNELS = ['old_love2024', 'tab_ib']
# اضافه شدن story به لیست برای پوشش استوری‌های فوروارد شده
ALL_TYPES =

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

# --- [ توابع کمکی / Helpers ] ---

def is_admin(user):
    return user.username in ADMIN_USERNAMES

def check_join(user):
    if is_admin(user): return True
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{channel}", user.id).status
            if status in ['left', 'kicked']: return False
        except: continue
    return True

def get_lang_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        telebot.types.InlineKeyboardButton("فارسی 🇦🇫🇮🇷", callback_data="lang_fa"),
        telebot.types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        telebot.types.InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")
    )
    return markup

def get_join_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for ch in CHANNELS:
        markup.add(telebot.types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me{ch}"))
    markup.add(telebot.types.InlineKeyboardButton("✅ تایید عضویت / Joined", callback_data="check_membership"))
    return markup

# --- [ هندلرها / Handlers ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_membership":
        if check_join(call.from_user):
            bot.answer_callback_query(call.id, "✅ تایید شد!")
            bot.edit_message_text("🔥 خوش آمدید! نام آهنگ یا لینک را بفرستید.", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ هنوز عضو نشدید!", show_alert=True)

@bot.message_handler(content_types=ALL_TYPES)
def main_handler(message):
    # ۱. ری‌اکشن کبوتر سفید 🕊️ روی همه پیام‌ها (حتی استوری)
    try:
        bot.set_message_reaction(message.chat.id, message.message_id, [telebot.types.ReactionTypeEmoji('🕊')], is_big=False)
    except: pass

    # ۲. بررسی عضویت (با استثنا برای ادمین‌ها)
    if not check_join(message.from_user):
        return bot.send_message(message.chat.id, "🔒 لطفاً ابتدا عضو کانال‌ها شوید:", reply_markup=get_join_markup())

    # ۳. منطق استارت و محتوا
    if message.content_type == 'text':
        if message.text == "/start":
            bot.send_message(message.chat.id, "🌐 Please select your language / لطفاً زبان خود را انتخاب کنید", reply_markup=get_lang_markup())
        elif "http" in message.text:
            bot.send_chat_action(message.chat.id, 'upload_audio')
            try:
                bot.send_audio(message.chat.id, audio=message.text, caption="🎵 فایل آماده شد! 🕊️")
            except:
                bot.reply_to(message, "❌ لینک مستقیم نیست یا حجم فایل بیش از ۵۰ مگابایت است.")
    
    elif message.content_type == 'story':
        bot.reply_to(message, "📥 استوری فوروارد شده شناسایی شد! در حال پردازش... 🕊️")

# --- [ تنظیمات وب‌هوک و سرور / Webhook & Server ] ---

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Forbidden", 403

@app.route('/')
def home(): 
    return "Viva Bot is Running!", 200

if __name__ == '__main__':
    # این دو خط برای فعال کردن وب‌هوک حیاتی هستند
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
