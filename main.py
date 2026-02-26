import os
import telebot
from flask import Flask, request
from telebot import types

# --- [ Settings ] ---
# ⚠️ حتماً توکن جدید بگیر و اینجا بذار
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

ADMIN_USERNAMES = ['OYB1234', 'sahar143']
CHANNELS = ['old_love2024', 'tab_ib']
ALL_TYPES = ['text', 'audio', 'video', 'document', 'photo', 'sticker', 'video_note', 'voice', 'location', 'story', 'contact']

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

# --- [ Helper Functions ] ---
def is_admin(user):
    return user.username in ADMIN_USERNAMES

def check_join(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{ch}", user_id).status
            if status in ['left', 'kicked']: return False
        except: continue
    return True

def get_join_keyboard():
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(text=f"📢 عضویت در {ch}", url=f"https://t.me{ch}"))
    markup.add(types.InlineKeyboardButton(text="✅ تایید عضویت", callback_data="check_membership"))
    return markup

# --- [ Handlers ] ---

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_callback(call):
    if check_join(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ مرسی! حالا می‌تونی استفاده کنی.")
        bot.edit_message_text("🔓 دسترسی آزاد شد. لینک خود را بفرستید:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی دوست من!", show_alert=True)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not check_join(message.from_user.id):
        bot.send_message(message.chat.id, "👋 خوش آمدید! برای استفاده باید ابتدا عضو کانال‌ها شوید:", reply_markup=get_join_keyboard())
    else:
        bot.send_message(message.chat.id, "🚀 آماده‌ام! لینک ویدیو یا آهنگ رو بفرست برات اوکی کنم.")

@bot.message_handler(content_types=ALL_TYPES)
def main_handler(message):
    # ری‌اکشن کبوتر روی همه پیام‌ها
    try:
        bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji('🕊')], is_big=False)
    except: pass

    # چک کردن عضویت
    if not check_join(message.from_user.id):
        return bot.send_message(message.chat.id, "⚠️ دسترسی محدود شده. ابتدا عضو شوید:", reply_markup=get_join_keyboard())

    if message.text and "http" in message.text:
        sent_msg = bot.reply_to(message, "📥 لینک شناسایی شد! در حال آماده‌سازی...")
        bot.send_chat_action(message.chat.id, 'upload_video')
        
        try:
            # ارسال مستقیم فایل (لینک باید مستقیم باشد)
            bot.send_video(message.chat.id, video=message.text, caption="✅ فایل شما آماده شد! 🕊️")
            bot.delete_message(message.chat.id, sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ خطا: یا لینک مستقیم نیست یا سرور تلگرام فایل رو قبول نمی‌کنه.", message.chat.id, sent_msg.message_id)

# --- [ Server Logic ] ---
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
    # تنظیم مجدد وب‌هوک برای اتصال به رندر
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
