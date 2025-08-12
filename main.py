import requests
import schedule
import threading
import time
import json
import os
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
bot = Bot(token=BOT_TOKEN)

# Webhook setup
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if WEBHOOK_URL:
    bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"✅ Webhook set to {WEBHOOK_URL}/webhook")
else:
    print("❌ WEBHOOK_URL not set!")

# Login credentials
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# API URLs
LOGIN_URL = os.getenv("LOGIN_URL")
LESSONS_URL = os.getenv("LESSONS_URL")

# Courses
COURSES = {
    "791": {"name": "GS Crash Course By Khan Sir & Team | Price: ₹99", "chat_id": "0000000000"},
    "790": {"name": "UPSC EPFO 2025 APFC & EO/AO | Price: ₹1999", "chat_id": "0000000000"},
    "609": {"name": "UPPSC RO/ARO (Pre+Mains) Re-Exam Foundation Batch Recorded)"},
    "608": {"name": "UPPCS RO/ARO Re-Exam Revision Batch 2025"},
    "607": {"name": "BSO/SSO & BSSC CGL 4 (PT +Mains) Batch-2025"},
    "606": {"name": "UPPCS Mains Mentorship Program 2025 Online"},
    "605": {"name": "MPPSC (Prelims + Mains) Foundation Batch 2026"},
    "604": {"name": "UPPCS Mains Mentorship Program 2025 Prayagraj Offline"},
    "603": {"name": "UPPCS Paper 5 & 6 Module Batch 2025"},
    "602": {"name": "UPPSC (Prelims +Mains) Foundation Batch 2025-26"},
    "601": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium"},
    "600": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 (English Medium)"},
    "599": {"name": "NCERT Foundation English Medium"},
    "598": {"name": "NCERT Foundation Batch (Hindi Medium)"},
    "597": {"name": "Class 12th/ 12th Pass MISSION BATCH NEET 2026 Hindi"},
    "596": {"name": "Class 12th/ 12th Pass MISSION BATCH NEET 2026 ENGLISH"},
    "595": {"name": "Class 12th/ 12th Pass MISSION BATCH JEE 2026 BILINGUAL"},
    "594": {"name": "Class 11th VISION BATCH NEET 2027 Hindi"},
    "593": {"name": "Class 11th VISION BATCH NEET 2027 English"},
    "592": {"name": "Class 11th VISION BATCH JEE 2027 BILINGUAL"},
    "591": {"name": "Bihar Police Batch 2025"}
}

# ----------------- Auth Users storage file -----------------
AUTH_FILE = "auth_users.json"

def load_auth_users():
    global AUTH_USERS
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            AUTH_USERS = json.load(f)
    else:
        AUTH_USERS = {}

def save_auth_users():
    with open(AUTH_FILE, "w") as f:
        json.dump(AUTH_USERS, f)

# First load
load_auth_users()

# ----------------- Headers -----------------
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer undefined"
}

# ----------------- Credit -----------------
CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

# ----------------- Core Functions -----------------
def telegram_send(chat_id, text, message_thread_id=None):
    try:
        bot.send_message(chat_id=chat_id, text=text[:4096], parse_mode="HTML", message_thread_id=message_thread_id)
    except Exception as e:
        print(f"[!] Error sending to {chat_id}: {e}")

def login():
    try:
        payload = {"phone": username, "password": password}
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200 and r.json().get("token"):
            headers["Authorization"] = f"Bearer {r.json()['token']}"
            return True
    except Exception as e:
        print(f"[!] Login failed: {e}")
    return False

def fetch_and_send():
    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed!")
        return
    for course_id, course_info in COURSES.items():
        try:
            r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
            today_classes = r.json().get("todayclasses", [])
            if not today_classes:
                telegram_send(course_info.get("chat_id", CHAT_ID),
                              f"{CREDIT_MESSAGE}\n📘 Course: {course_info['name']}\n❌ No update found today")
                continue
            for cls in today_classes:
                message = format_class_message(cls, course_info["name"])
                telegram_send(course_info["chat_id"], message)
        except Exception as e:
            print(f"[!] Error: {e}")

def fetch_and_send_to_owner_only():
    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed!")
        return
    for course_id, course_info in COURSES.items():
        try:
            r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
            today_classes = r.json().get("todayclasses", [])
            if not today_classes:
                telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n📘 Course: {course_info['name']}\n❌ No update found today")
                continue
            for cls in today_classes:
                message = format_class_message(cls, course_info["name"])
                telegram_send(CHAT_ID, message)
        except Exception as e:
            print(f"[!] Error: {e}")

def format_class_message(cls, course_name):
    name = cls.get("name", "No Name")
    video_url = cls.get("video_url")
    hd_url = cls.get("hd_video_url")
    pdfs = cls.get("pdfs", [])
    notes_links, ppt_links = "", ""
    for pdf in pdfs:
        title = pdf.get("title", "").lower()
        url = pdf.get("url", "")
        if "ppt" in title:
            ppt_links += f"📄 <a href=\"{url}\">PPT</a>\n"
        else:
            notes_links += f"📝 <a href=\"{url}\">Notes</a>\n"
    message = (
        f"{CREDIT_MESSAGE}\n📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n"
        f"📘 Course: {course_name}\n🎥 Lesson: {name}\n"
    )
    if video_url:
        message += f"🔗 <a href=\"{video_url}\">Server Link</a>\n"
    if hd_url:
        message += f"🔗 <a href=\"{hd_url}\">YouTube Link</a>\n"
    message += notes_links + ppt_links
    return message

# ----------------- Command Handlers -----------------
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/send - Owner only\n/grpsend - All groups\n/class - Your course\n/class <course_id> - Owner check any course\n/auth <id> <course_id>\n/unauth <id>\n/authlist - List users\n/ping - Alive\n/help - Help\n/start - Info\n\n" + CREDIT_MESSAGE,
        parse_mode="HTML"
    )

def ping(update: Update, context: CallbackContext):
    update.message.reply_text(f"✅ Bot is Alive!\n{CREDIT_MESSAGE}", parse_mode="HTML")

def send(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) == str(CHAT_ID):
        fetch_and_send_to_owner_only()
    else:
        update.message.reply_text("❌ Unauthorized")

def class_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_chat.id)

    # Owner custom course check
    if str(user_id) == str(CHAT_ID) and len(context.args) == 1:
        course_id = context.args[0]
        if course_id not in COURSES:
            return update.message.reply_text("❌ Invalid course ID")

        if not login():
            return update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")

        r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
        today_classes = r.json().get("todayclasses", [])

        if not today_classes:
            return update.message.reply_text(
                f"{CREDIT_MESSAGE}\n📘 Course: {COURSES[course_id]['name']}\n❌ No update found today",
                parse_mode="HTML"
            )

        for cls in today_classes:
            message = format_class_message(cls, COURSES[course_id]["name"])
            telegram_send(user_id, message)
        return

    # Normal user check
    load_auth_users()
    if user_id not in AUTH_USERS:
        update.message.reply_text("❌ Not authorized")
        return

    course_id = AUTH_USERS[user_id]
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
        return

    r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
    today_classes = r.json().get("todayclasses", [])

    if not today_classes:
        return update.message.reply_text(
            f"{CREDIT_MESSAGE}\n📘 Course: {COURSES[course_id]['name']}\n❌ No update found today",
            parse_mode="HTML"
        )

    for cls in today_classes:
        message = format_class_message(cls, COURSES[course_id]["name"])
        telegram_send(user_id, message)

def auth_user(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != str(CHAT_ID):
        return update.message.reply_text("❌ Unauthorized")
    if len(context.args) != 2:
        return update.message.reply_text("Usage: /auth <user_id> <course_id>")
    user_id, course_id = str(context.args[0]), context.args[1]
    AUTH_USERS[user_id] = course_id
    save_auth_users()
    load_auth_users()
    update.message.reply_text(f"✅ Authorized {user_id} for course {course_id}")

def unauth_user(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != str(CHAT_ID):
        return update.message.reply_text("❌ Unauthorized")
    if len(context.args) != 1:
        return update.message.reply_text("Usage: /unauth <user_id>")
    user_id = str(context.args[0])
    if user_id in AUTH_USERS:
        del AUTH_USERS[user_id]
        save_auth_users()
        load_auth_users()
        update.message.reply_text(f"✅ UnAuthorized {user_id}")
    else:
        update.message.reply_text("❌ User not found")

def auth_list(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) != str(CHAT_ID):
        return update.message.reply_text("❌ Unauthorized")
    load_auth_users()
    if not AUTH_USERS:
        return update.message.reply_text("No authorized users")
    msg = "Authorized Users:\n\n"
    for uid, cid in AUTH_USERS.items():
        course_name = COURSES.get(cid, {}).get("name", "Unknown")
        msg += f"👤 {uid} → {cid} ({course_name})\n"
    update.message.reply_text(msg)

# ----------------- Flask App -----------------
app = Flask(__name__)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("class", class_command))
dispatcher.add_handler(CommandHandler("auth", auth_user))
dispatcher.add_handler(CommandHandler("unauth", unauth_user))
dispatcher.add_handler(CommandHandler("authlist", auth_list))

@app.route("/")
def home():
    return "Bot Active!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return '', 200

# ----------------- Scheduler -----------------
schedule.every().day.at("21:30").do(fetch_and_send)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

def send_deployment_notification():
    telegram_send(CHAT_ID, f"🚀 Bot deployed on Koyeb!\n{CREDIT_MESSAGE}")

if __name__ == "__main__":
    send_deployment_notification()
    threading.Thread(target=run_scheduler, daemon=True).start()

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        bot.delete_webhook()
        bot.set_webhook(f"{webhook_url}/webhook")
        print(f"Webhook set to {webhook_url}/webhook")

    app.run(host="0.0.0.0", port=8000)
