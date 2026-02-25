import os
import telebot
from flask import Flask, request

# --- [ Settings ] ---
BOT_TOKEN = "8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME"
RENDER_URL = "https://viva-bot-vuvy.onrender.com" 

CHANNELS = ['old_love2024', 'tab_ib']
ALL_TYPES =

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = Flask(__name__)

# --- [ Helper Functions ] ---

def check_join(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(f"@{channel}", user_id).status
            if status in ['left', 'kicked']: return False
        except: continue
    return True

def get_lang_markup():
    """زبان منتخب کرنے کے بٹن (تصویر کے مطابق)"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn_fa = telebot.types.InlineKeyboardButton("فارسی 🇦🇫🇮🇷", callback_data="lang_fa")
    btn_en = telebot.types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")
    btn_ar = telebot.types.InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")
    markup.add(btn_fa, btn_en, btn_ar)
    return markup

def get_join_markup():
    """جوائننگ بٹن (تصویر کے مطابق)"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btns = [telebot.types.InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me{ch}") for ch in CHANNELS]
    markup.add(*btns)
    markup.add(telebot.types.InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership"))
    return markup

# --- [ Webhook Routes ] ---

@app.route('/')
def home(): return "Viva Bot is Active!", 200

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Forbidden", 403

# --- [ Handlers ] ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_') or call.data == "check_membership")
def callback_handler(call):
    if call.data == "check_membership":
        if check_join(call.from_user.id):
            bot.answer_callback_query(call.id, "✅ خوش آمدید!")
            bot.edit_message_text("🔥 **ثبت شد!**\nحالا نام آهنگ یا لینک را بفرستید.", call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ هنوز عضو نشدید!", show_alert=True)
    
    elif call.data.startswith('lang_'):
        bot.answer_callback_query(call.id, "Language Selected!")
        bot.edit_message_text("✅ زبان انتخاب شد. اکنون می‌توانید از ربات استفاده کنید.", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=ALL_TYPES)
def main_handler(message):
    # ۱. ہر میسج پر سفید کبوتر (🕊️) کا ری ایکشن
    try:
        bot.set_message_reaction(message.chat.id, message.message_id, [telebot.types.ReactionTypeEmoji('🕊')], is_big=False)
    except: pass

    # ۲. ممبرشپ چیک کرنا
    if not check_join(message.from_user.id):
        text = "🔒 لطفاً ابتدا در کانال‌ها عضو شوید سپس تایید را بزنید"
        return bot.send_message(message.chat.id, text, reply_markup=get_join_markup())

    # ۳. اسٹارٹ کمانڈ اور زبان کا انتخاب
    if message.text == "/start":
        text = "🌐 Please select your language\n🌐 لطفاً زبان خود را انتخاب نمایید\n🌐 يرجى اختيار لغتك"
        bot.send_message(message.chat.id, text, reply_markup=get_lang_markup())
    
    # ۴. لنک اور اسٹوری پروسیسنگ
    elif message.content_type == 'story':
        bot.reply_to(message, "📥 استوری شناسایی شد! در حال پردازش...")
    
    elif message.text and "http" in message.text:
        bot.send_chat_action(message.chat.id, 'upload_audio')
        try:
            bot.send_audio(message.chat.id, audio=message.text, caption="🎵 تقدیم به شما!")
        except:
            bot.reply_to(message, "❌ لینک معتبر نیست.")

# --- [ Start ] ---
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
