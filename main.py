from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from googletrans import Translator
import asyncio

# --- [ Configuration / تنظیمات ] ---
API_ID = 1234567 
API_HASH = 'your_api_hash'
BOT_TOKEN = '8790363458:AAFRIqgm_E-0bdIKment7fbEtPqQfknieME' # حتماً توکن را ریست کنید

CHANNELS = ['old_love2024', 'tab_ib']
ADMINS = ['sahar143', 'OYB1234']

client = TelegramClient('viva_v7', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
translator = Translator()

# --- [ Helper Functions / توابع کمکی ] ---
async def check_join(user_id):
    for channel in CHANNELS:
        try:
            await client(GetParticipantRequest(channel, user_id))
        except UserNotParticipantError: return False
        except: continue
    return True

def main_menu(lang):
    c_link = f"https://t.me{CHANNELS[0]}"
    if lang == 'fa':
        return [
            [Button.inline("🔍 جستجوی آهنگ", data="search_music")],
            [Button.inline("🎥 دانلودر (TikTok/Snap)", data="how_to_dl")],
            [Button.inline("🌐 تغییر زبان", data="change_lang"), Button.inline("👑 خرید VIP", data="buy_vip")],
            [Button.url("📢 کانال رسمی", c_link)]
        ]
    else:
        return [
            [Button.inline("🔍 Music Search", data="search_music")],
            [Button.inline("🎥 Video Downloader", data="how_to_dl")],
            [Button.inline("🌐 Change Language", data="change_lang"), Button.inline("👑 Buy VIP", data="buy_vip")],
            [Button.url("📢 Official Channel", c_link)]
        ]

# --- [ Event Handlers ] ---

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_join(event.sender_id):
        join_btns = [[Button.url(f"Join {ch}", f"https://t.me{ch}")] for ch in CHANNELS]
        join_btns.append([Button.url("✅ عضو شدم / Joined", f"https://t.me{(await client.get_me()).username}?start=true")])
        return await event.reply("❌ **لطفاً ابتدا عضو کانال‌های ما شوید:**", buttons=join_btns)

    welcome_text = (
        "🔥 **𝙑𝙄𝙑𝘼 𝙂𝙇𝙊𝘽𝘼𝙇 𝘽𝙊𝙏** 🔥\n"
        "━━━━━━━━━━━━━━\n"
        "👋 سلام! به پیشرفته‌ترین دستیار هوشمند خوش‌آمدی\n"
        "**Welcome to the most powerful media assistant!**\n\n"
        "👇 **Select language / زبان را انتخاب کنید:**"
    )
    await event.reply(welcome_text, buttons=[[Button.inline("🇮🇷 فارسی", data="lang_fa"), Button.inline("🇺🇸 English", data="lang_en")]])

@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        text = "🏠 **منوی اصلی فعال شد**" if lang == 'fa' else "🏠 **Main Menu Activated**"
        await event.edit(text, buttons=main_menu(lang))
        
    elif data == "search_music":
        await event.answer("🔍 نام آهنگ را بفرستید!", alert=True)

    # --- بخش جدید: دریافت متن آهنگ ---
    elif data.startswith("get_lyrics|"):
        song_name = data.split("|")[1]
        # اینجا بعداً کد استخراج واقعی رو می‌ذاری، فعلاً دمو:
        lyrics = f"📜 Lyrics for: {song_name}\n\n[متن آهنگ به زودی از دیتابیس فراخوانی می‌شود...]"
        await event.reply(lyrics, buttons=[[Button.inline("🌐 ترجمه متن (Translate)", data="translate_lyrics")]])

    # --- بخش جدید: ترجمه هوشمند ---
    elif data == "translate_lyrics":
        current_text = (await event.get_message()).text
        try:
            detected = translator.detect(current_text).lang
            target = 'en' if detected == 'fa' else 'fa'
            translated = translator.translate(current_text, dest=target)
            await event.edit(f"**🌏 Translation ({target}):**\n\n{translated.text}")
        except:
            await event.answer("❌ خطا در ترجمه!", alert=True)

@client.on(events.NewMessage)
async def message_handler(event):
    if event.text.startswith('/') or event.is_reply: return
    
    if "http" in event.text:
        await event.reply("📥 لینک شناسایی شد! در حال آماده‌سازی...", buttons=[[Button.inline("🎬 Video", data="dl_vid"), Button.inline("🎵 Audio", data="dl_aud")]])
    else:
        # شبیه‌سازی پیدا شدن آهنگ
        song_name = event.text
        btns = [
            [Button.inline("🎵 دریافت آهنگ (MP3)", data="dl_mp3")],
            [Button.inline("📜 دریافت متن آهنگ (Lyrics)", data=f"get_lyrics|{song_name}")]
        ]
        await event.reply(f"🎧 آهنگ **{song_name}** پیدا شد! انتخاب کنید:", buttons=btns)

print("✅ Viva Bot is LIVE!")
client.run_until_disconnected()
