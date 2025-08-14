import os
import requests
import threading
import time
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# ✅ Load from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
APP_URL = os.environ.get("APP_URL")

CHAT_ID = 6268938019
bot = Bot(token=BOT_TOKEN)

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Courses with names and group chat IDs
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar"},
    "617": {"name": "Pocket gk batch"},
    "372": {"name": "Geography optional english medium7"},
    "718": {"name": "UGC NET/JRF Paper-I December Batch 2025"},
    "716": {"name": "Math Foundation Batch By Amit Sir"},
    "592": {"name": " Class 11th VISION BATCH JEE 2027 BILINGUAL | Price: ₹1999"},
    "749": {"name": "CSAT (UPSC + UPPCS) Prayagraj Classroom Programme | Price: ₹3499 "},
    "750": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar | Price: ₹69500 |"},
    "756": {"name": "UPPSC (Prelims +Mains) Foundation Batch 2026 | Price: ₹4999"},
    "723": {"name": "UGC NET/JRF Geography Foundation Batch December 2025"}
}

# Authorized Users (initial setup)
AUTH_USERS = {
    6268938019: ["696"],  # Owner has access to PSIR by default
    5400488190: ["696","749"],
    6465713273: ["716"]
}

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

def save_auth_users():
    """Save the current AUTH_USERS to a file for persistence"""
    with open("auth_users.txt", "w") as f:
        for user_id, courses in AUTH_USERS.items():
            f.write(f"{user_id}:{','.join(courses)}\n")

def load_auth_users():
    """Load AUTH_USERS from file if it exists"""
    try:
        with open("auth_users.txt", "r") as f:
            for line in f.readlines():
                user_id, courses = line.strip().split(":")
                AUTH_USERS[int(user_id)] = courses.split(",")
    except FileNotFoundError:
        # If file doesn't exist, keep the initial AUTH_USERS
        pass

# Load saved users on startup
load_auth_users()

# --- Helper Functions ---
def telegram_send(chat_id, text, message_thread_id=None):
    try:
        bot.send_message(chat_id=chat_id, text=text[:4096], parse_mode="HTML", message_thread_id=message_thread_id)
    except Exception as e:
        print(f"[!] Error sending to {chat_id}: {e}")

def login():
    try:
        payload = {"phone": USERNAME, "password": PASSWORD}
        r = requests.post(LOGIN_URL, headers=headers, json=payload)
        if r.status_code == 200 and r.json().get("token"):
            headers["Authorization"] = f"Bearer {r.json()['token']}"
            return True
    except Exception as e:
        print(f"[!] Login failed: {e}")
    return False

def format_class_message(cls, course_name):
    name = cls.get("name", "No Name")
    video_url = cls.get("video_url")
    hd_url = cls.get("hd_video_url")
    pdfs = cls.get("pdfs", [])

    notes_links = ""
    ppt_links = ""
    for pdf in pdfs or []:
        title = pdf.get("title", "").lower()
        url = pdf.get("url", "")
        if "ppt" in title:
            ppt_links += f"📄 <a href=\"{url}\">PPT</a>\n"
        else:
            notes_links += f"📝 <a href=\"{url}\">Notes</a>\n"

    message = (
        f"{CREDIT_MESSAGE}\n"
        f"📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n"
        f"📘 Course: {course_name}\n"
        f"🎥 Lesson: {name}\n"
    )
    if video_url:
        message += f"🔗 <a href=\"{video_url}\">Server Link</a>\n"
    if hd_url:
        message += f"🔗 <a href=\"{hd_url}\">YouTube Link</a>\n"
    message += notes_links + ppt_links + "\n\n👇👇👇👇👇👇👇👇👇👇👇👇\n🔗 <a href=\"https://t.me/exams_materiel\"><b>👉MAIN CHANNEL LINK👈</b></a>"
    return message

# --- New Access Management Commands ---
def grant_access(update: Update, context: CallbackContext):
    """Grant access to courses for a user"""
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Only owner can use this command!")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /grant <user_id> <course_id1,course_id2,...>")
        return

    try:
        user_id = int(context.args[0])
        course_ids = context.args[1].split(",")
        
        # Validate course IDs
        invalid_courses = [cid for cid in course_ids if cid not in COURSES]
        if invalid_courses:
            update.message.reply_text(f"❌ Invalid course IDs: {', '.join(invalid_courses)}")
            return

        # Add or update user access
        if user_id in AUTH_USERS:
            existing = set(AUTH_USERS[user_id])
            new_courses = set(course_ids)
            AUTH_USERS[user_id] = list(existing.union(new_courses))
        else:
            AUTH_USERS[user_id] = course_ids

        save_auth_users()
        update.message.reply_text(f"✅ Access granted to user {user_id} for courses: {', '.join(course_ids)}")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def revoke_access(update: Update, context: CallbackContext):
    """Revoke access to courses for a user"""
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Only owner can use this command!")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /revoke <user_id> <course_id1,course_id2,...> or 'all'")
        return

    try:
        user_id = int(context.args[0])
        course_ids = context.args[1].split(",") if context.args[1].lower() != "all" else "all"
        
        if user_id not in AUTH_USERS:
            update.message.reply_text(f"❌ User {user_id} has no access!")
            return

        if course_ids == "all":
            del AUTH_USERS[user_id]
            update.message.reply_text(f"✅ Revoked ALL access for user {user_id}")
        else:
            # Validate course IDs
            invalid_courses = [cid for cid in course_ids if cid not in COURSES]
            if invalid_courses:
                update.message.reply_text(f"❌ Invalid course IDs: {', '.join(invalid_courses)}")
                return

            # Remove specified courses
            remaining = [cid for cid in AUTH_USERS[user_id] if cid not in course_ids]
            if remaining:
                AUTH_USERS[user_id] = remaining
            else:
                del AUTH_USERS[user_id]

            update.message.reply_text(f"✅ Revoked access for user {user_id} to courses: {', '.join(course_ids)}")

        save_auth_users()
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def show_access(update: Update, context: CallbackContext):
    """Show current access for a user or all users"""
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Only owner can use this command!")
        return

    if context.args:
        try:
            user_id = int(context.args[0])
            if user_id in AUTH_USERS:
                courses = "\n".join([f"{cid}: {COURSES[cid]['name']}" for cid in AUTH_USERS[user_id]])
                update.message.reply_text(f"🔄 Access for user {user_id}:\n{courses}")
            else:
                update.message.reply_text(f"❌ User {user_id} has no access!")
        except:
            update.message.reply_text("⚠️ Usage: /access [user_id]")
    else:
        if not AUTH_USERS:
            update.message.reply_text("❌ No users have access!")
            return

        message = "🔄 Current Access List:\n\n"
        for user_id, courses in AUTH_USERS.items():
            course_names = ", ".join([f"{cid} ({COURSES[cid]['name'][:20]}...)" for cid in courses])
            message += f"👤 User {user_id}:\n{course_names}\n\n"

        update.message.reply_text(message)

# --- Existing Fetch Functions and Commands ---
# [Keep all your existing fetch functions and commands here...]

# --- Flask App ---
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# Register all commands in dispatcher
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("class", class_command))
dispatcher.add_handler(CommandHandler("grant", grant_access))
dispatcher.add_handler(CommandHandler("revoke", revoke_access))
dispatcher.add_handler(CommandHandler("access", show_access))

@app.route("/")
def home():
    return "Bot Active!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "", 200

# --- Scheduler System ---
scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata'))
scheduler.add_job(fetch_and_send, 'cron', hour=21, minute=30)
scheduler.start()

def set_webhook():
    if APP_URL:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={APP_URL}/webhook"
        try:
            r = requests.get(url)
            print("[Webhook set response]:", r.text)
        except Exception as e:
            print(f"[!] Error setting webhook: {e}")
    else:
        print("[!] APP_URL not set, webhook not configured")

if __name__ == "__main__":
    set_webhook()
    print("✅ शेड्यूलर स्टार्ट हो गया! रोज 9:30 PM पर ऑटोमैटिक भेजेगा।")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
