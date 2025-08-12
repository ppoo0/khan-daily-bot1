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
BOT_TOKEN = "7524865501:AAEeOuoaQATrXujou4sZlzwdiS9fMDQyqkA"
CHAT_ID = 6268938019  # Admin ID
bot = Bot(token=BOT_TOKEN)

# Login credentials
username = "7903443604"
password = "Gautam@123"

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Courses
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR", "chat_id": "-1002898647258"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025", "chat_id": "-1002565001732"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026", "chat_id": "-1002821163148"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA", "chat_id": "-1002871614152"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM", "chat_id": "-1002662799575"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium", "chat_id": "-1002810220072"},
    "670": {"name": "UPSC G.S (Prelims+Mains) फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम", "chat_id": "-1002642433551"},
    "617": {"name": "Pocket gk batch", "chat_id": "-1002887628954"},
    "372": {"name": "Geography optional english medium", "chat_id": "-1002170644891"},
    "718": {"name": "UGC NET/JRF Paper-I December Batch 2025", "chat_id": "1193912277"},
    "716": {"name": "Math Foundation Batch By Amit Sir", "chat_id": "6465713273"},
    "592": {"name": "Class 11th VISION BATCH JEE 2027", "chat_id": "8064538295"},
}

# Topic IDs
GROUP_ID = -1002810170749
TOPIC_IDS = {
    "696": 5, "686": 6, "691": 10, "704": 11,
    "700": 12, "667": 13, "670": 14, "617": 15,
    "372": 16, "718": 17, "716": 18
}

# Auth file
AUTH_FILE = "auth_data.json"

# Load authorized users
if os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, "r") as f:
        AUTH_USERS = json.load(f)
else:
    AUTH_USERS = {
        6268938019: "696",
        5400488190: "696",
        7879332317: "723",
        6465713273: "716"
    }

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer undefined"
}

# Credit
CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

# ----------------- Core Functions -----------------
def save_auth_data():
    with open(AUTH_FILE, "w") as f:
        json.dump(AUTH_USERS, f)

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
            for cls in r.json().get("todayclasses", []):
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
            for cls in r.json().get("todayclasses", []):
                message = format_class_message(cls, course_info["name"])
                telegram_send(CHAT_ID, message)
        except Exception as e:
            print(f"[!] Error: {e}")

def fetch_and_send_to_group_topics():
    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed!")
        return
    for course_id, topic_id in TOPIC_IDS.items():
        try:
            r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
            course_name = COURSES.get(course_id, {}).get("name", "Unknown Course")
            for cls in r.json().get("todayclasses", []):
                message = format_class_message(cls, course_name)
                telegram_send(GROUP_ID, message, message_thread_id=topic_id)
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
        "/send - Owner only\n/grpsend - All groups\n/allsend - One group all topics\n/class - Your course\n/auth - Give access\n/unauth - Remove access\n/ping - Alive\n/help - Help\n/start - Info\n\n" + CREDIT_MESSAGE,
        parse_mode="HTML"
    )

def ping(update: Update, context: CallbackContext):
    update.message.reply_text(f"✅ Bot is Alive!\n{CREDIT_MESSAGE}", parse_mode="HTML")

def send(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        fetch_and_send_to_owner_only()
    else:
        update.message.reply_text("❌ Unauthorized")

def grpsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        fetch_and_send()
    else:
        update.message.reply_text("❌ Unauthorized")

def allsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        fetch_and_send_to_group_topics()
    else:
        update.message.reply_text("❌ Unauthorized")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "<b>यह बॉट खान ग्लोबल स्टडीज के सभी batches की लाइव क्लास भेजता है</b>",
        parse_mode="HTML"
    )

def class_command(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if str(user_id) not in AUTH_USERS:
        update.message.reply_text("❌ Not authorized")
        return
    course_id = AUTH_USERS[str(user_id)]
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
        return
    r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
    for cls in r.json().get("todayclasses", []):
        message = format_class_message(cls, COURSES[course_id]["name"])
        telegram_send(user_id, message)

def auth_command(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Unauthorized")
        return
    if len(context.args) != 2:
        update.message.reply_text("Usage: /auth <user_id> <course_id>")
        return
    user_id, course_id = context.args
    AUTH_USERS[str(user_id)] = course_id
    save_auth_data()
    update.message.reply_text(f"✅ User {user_id} authorized for course {course_id}")

def unauth_command(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Unauthorized")
        return
    if len(context.args) != 2:
        update.message.reply_text("Usage: /unauth <user_id> <course_id>")
        return
    user_id, course_id = context.args
    if str(user_id) in AUTH_USERS and AUTH_USERS[str(user_id)] == course_id:
        del AUTH_USERS[str(user_id)]
        save_auth_data()
        update.message.reply_text(f"❌ User {user_id} unauthorized from course {course_id}")
    else:
        update.message.reply_text(f"⚠️ No such authorization found for {user_id} and course {course_id}")

# ----------------- Flask App -----------------
app = Flask(__name__)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_handler(CommandHandler("allsend", allsend))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("class", class_command))
dispatcher.add_handler(CommandHandler("auth", auth_command))
dispatcher.add_handler(CommandHandler("unauth", unauth_command))

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
    app.run(host="0.0.0.0", port=8000)
