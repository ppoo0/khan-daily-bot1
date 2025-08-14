import os
import asyncio
import requests
import json
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# Load from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
APP_URL = os.environ.get("APP_URL")

CHAT_ID = 6268938019  # Owner's chat ID
bot = Bot(token=BOT_TOKEN)

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Courses with names
COURSES = {
    "696": {"name": "PSIR BY SANJAY THAKUR"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium"},
    "670": {"name": "UPSC G.S (Prelims+Mains) फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम"},
    "617": {"name": "Pocket gk batch"},
    "372": {"name": "Geography optional english medium"},
    "718": {"name": "UGC NET/JRF Paper-I December Batch 2025"},
    "716": {"name": "Math Foundation Batch By Amit Sir"},
    "749": {"name": "CSAT (UPSC + UPPCS) Prayagraj Classroom Programme"},
    "750": {"name": "UPSC G.S (Prelims+Mains) फाउंडेशन प्रोग्राम 2026"},
    "756": {"name": "UPPSC (Prelims +Mains) Foundation Batch 2026"},
    "723": {"name": "UGC NET/JRF Geography Foundation Batch December 2025"},
}

# Load authorized users from file or use default
AUTH_USERS = {}
AUTH_FILE = "auth_users.json"

def load_auth_users():
    global AUTH_USERS
    try:
        with open(AUTH_FILE, "r") as f:
            AUTH_USERS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default users if file doesn't exist
        AUTH_USERS = {
            6268938019: ["696"],  # Owner
            5400488190: ["696", "749"],
            6465713273: ["716"],
        }
        save_auth_users()

def save_auth_users():
    with open(AUTH_FILE, "w") as f:
        json.dump(AUTH_USERS, f)

# Initialize auth users
load_auth_users()

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined",
}

CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

# Helper Functions
async def telegram_send(chat_id, text, message_thread_id=None):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text[:4096],
            parse_mode="HTML",
            message_thread_id=message_thread_id,
        )
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
    message += (
        notes_links
        + ppt_links
        + "\n\n👇👇👇👇👇👇👇👇👇👇👇👇\n🔗 <a href=\"https://t.me/exams_materiel\"><b>👉MAIN CHANNEL LINK👈</b></a>"
    )
    return message

# Fetch Functions
async def fetch_and_send_to_owner_only():
    if not login():
        await telegram_send(
            CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed! Check credentials."
        )
        return

    for course_id, course_info in COURSES.items():
        try:
            url = LESSONS_URL.format(course_id=course_id)
            r = requests.get(url, headers=headers)
            data = r.json()

            if not data.get("success", True):
                print(f"[!] API error for course {course_id}: {data.get('message')}")
                continue

            today_classes = data.get("todayclasses", [])

            if not today_classes:
                print(f"[i] No classes today for {course_info['name']}")
                continue

            for cls in today_classes:
                await telegram_send(
                    CHAT_ID, format_class_message(cls, course_info["name"])
                )
        except Exception as e:
            print(f"[!] Error in course {course_id}: {e}")

# Command Handlers
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📌 उपलब्ध कमांड्स:\n\n"
        "/start - बॉट के बारे में जानकारी\n"
        "/help - सभी कमांड्स दिखाएं\n"
        "/ping - बॉट चेक करें\n"
        "/grant <user_id> <course_ids> - यूजर को कोर्स एक्सेस दें\n"
        "/revoke <user_id> <course_ids|all> - यूजर का एक्सेस हटाएं\n"
        "/access [user_id] - एक्सेस लिस्ट देखें\n"
        "/class - अपने कोर्सेस की क्लासेस पाएं\n"
        "/send - ओनर के लिए अपडेट्स\n"
        f"{CREDIT_MESSAGE}"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ बॉट चालू है!\n{CREDIT_MESSAGE}", parse_mode="HTML"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>इस बॉट के द्वारा खान ग्लोबल स्टडीज के सभी बैचेस की लाइव क्लासेस भेजी जाती हैं</b>\n\n"
        f"{CREDIT_MESSAGE}",
        parse_mode="HTML",
    )

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id == CHAT_ID:
        await update.message.reply_text("⏳ Fetching updates...")
        await fetch_and_send_to_owner_only()
        await update.message.reply_text("✅ Done!")
    else:
        await update.message.reply_text("❌ Unauthorized")

async def grant_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("❌ Only owner can use this command!")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: /grant <user_id> <course_id1,course_id2,...>"
        )
        return

    try:
        user_id = int(context.args[0])
        course_ids = context.args[1].split(",")

        invalid_courses = [cid for cid in course_ids if cid not in COURSES]
        if invalid_courses:
            await update.message.reply_text(
                f"❌ Invalid course IDs: {', '.join(invalid_courses)}"
            )
            return

        if user_id in AUTH_USERS:
            existing = set(AUTH_USERS[user_id])
            new_courses = set(course_ids)
            AUTH_USERS[user_id] = list(existing.union(new_courses))
        else:
            AUTH_USERS[user_id] = course_ids

        save_auth_users()
        await update.message.reply_text(
            f"✅ Access granted to user {user_id} for courses: {', '.join(course_ids)}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def revoke_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("❌ Only owner can use this command!")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: /revoke <user_id> <course_id1,course_id2,...> or 'all'"
        )
        return

    try:
        user_id = int(context.args[0])
        course_ids = (
            context.args[1].split(",") if context.args[1].lower() != "all" else "all"
        )

        if user_id not in AUTH_USERS:
            await update.message.reply_text(f"❌ User {user_id} has no access!")
            return

        if course_ids == "all":
            del AUTH_USERS[user_id]
            await update.message.reply_text(f"✅ Revoked ALL access for user {user_id}")
        else:
            invalid_courses = [cid for cid in course_ids if cid not in COURSES]
            if invalid_courses:
                await update.message.reply_text(
                    f"❌ Invalid course IDs: {', '.join(invalid_courses)}"
                )
                return

            remaining = [cid for cid in AUTH_USERS[user_id] if cid not in course_ids]
            if remaining:
                AUTH_USERS[user_id] = remaining
            else:
                del AUTH_USERS[user_id]

            await update.message.reply_text(
                f"✅ Revoked access for user {user_id} to courses: {', '.join(course_ids)}"
            )

        save_auth_users()
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def show_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("❌ Only owner can use this command!")
        return

    if context.args:
        try:
            user_id = int(context.args[0])
            if user_id in AUTH_USERS:
                courses = "\n".join(
                    [f"{cid}: {COURSES[cid]['name']}" for cid in AUTH_USERS[user_id]]
                )
                await update.message.reply_text(f"🔄 Access for user {user_id}:\n{courses}")
            else:
                await update.message.reply_text(f"❌ User {user_id} has no access!")
        except:
            await update.message.reply_text("⚠️ Usage: /access [user_id]")
    else:
        if not AUTH_USERS:
            await update.message.reply_text("❌ No users have access!")
            return

        message = "🔄 Current Access List:\n\n"
        for user_id, courses in AUTH_USERS.items():
            course_names = ", ".join(
                [f"{cid} ({COURSES[cid]['name'][:20]}...)" for cid in courses]
            )
            message += f"👤 User {user_id}:\n{course_names}\n\n"

        await update.message.reply_text(message)

async def class_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    args = context.args

    if user_id == CHAT_ID and args:
        course_id = args[0]
        course_info = COURSES.get(course_id)
        if not course_info:
            await update.message.reply_text(f"⚠️ Course info not found for ID {course_id}.")
            return
        if not login():
            await update.message.reply_text(
                f"{CREDIT_MESSAGE}\n❌ Login failed! Try again later.", parse_mode="HTML"
            )
            return

        url = LESSONS_URL.format(course_id=course_id)
        try:
            r = requests.get(url, headers=headers)
            data = r.json()

            if not data.get("success", True):
                await update.message.reply_text(f"⚠️ API error: {data.get('message')}")
                return

            today_classes = data.get("todayclasses", [])

            if not today_classes:
                await update.message.reply_text(
                    f"📭 No updates found today for {course_info['name']}."
                )
                return

            await update.message.reply_text(f"⏳ Fetching {len(today_classes)} classes...")
            for cls in today_classes:
                await telegram_send(
                    user_id, format_class_message(cls, course_info["name"])
                )
            await update.message.reply_text("✅ Done!")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {str(e)}")
        return

    if user_id not in AUTH_USERS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    user_courses = AUTH_USERS[user_id]
    if not login():
        await update.message.reply_text(
            f"{CREDIT_MESSAGE}\n❌ Login failed! Try again later.", parse_mode="HTML"
        )
        return

    await update.message.reply_text("⏳ Fetching your classes...")
    for course_id in user_courses:
        course_info = COURSES.get(course_id)
        if not course_info:
            await update.message.reply_text(f"⚠️ Course info not found for ID {course_id}.")
            continue

        url = LESSONS_URL.format(course_id=course_id)
        try:
            r = requests.get(url, headers=headers)
            data = r.json()

            if not data.get("success", True):
                await update.message.reply_text(
                    f"⚠️ API error for course {course_id}: {data.get('message')}"
                )
                continue

            today_classes = data.get("todayclasses", [])

            if not today_classes:
                await update.message.reply_text(
                    f"📭 No updates found today for {course_info['name']}."
                )
                continue

            for cls in today_classes:
                await telegram_send(
                    user_id, format_class_message(cls, course_info["name"])
                )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error in course {course_id}: {str(e)}")

    await update.message.reply_text("✅ Done!")

# Flask App
app = Flask(__name__)

# Initialize Application
application = Application.builder().token(BOT_TOKEN).build()

# Register all commands
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("ping", ping))
application.add_handler(CommandHandler("send", send))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("class", class_command))
application.add_handler(CommandHandler("grant", grant_access))
application.add_handler(CommandHandler("revoke", revoke_access))
application.add_handler(CommandHandler("access", show_access))

@app.route("/")
def home():
    return "Bot Active!"

@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, bot)
    
    # Process update in a new thread
    def process_update():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        loop.close()
    
    import threading
    threading.Thread(target=process_update).start()
    
    return "ok", 200

# Scheduler System
scheduler = BackgroundScheduler(timezone=timezone("Asia/Kolkata"))
scheduler.add_job(
    lambda: asyncio.run(fetch_and_send_to_owner_only()), "cron", hour=21, minute=30
)
scheduler.start()

async def set_webhook():
    if APP_URL:
        url = f"{APP_URL}/webhook"
        try:
            await bot.set_webhook(url)
            print(f"[Webhook set successfully at {url}]")
        except Exception as e:
            print(f"[!] Error setting webhook: {e}")

if __name__ == "__main__":
    # Set webhook
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())

    print("✅ शेड्यूलर स्टार्ट हो गया! रोज 9:30 PM पर ऑटोमैटिक भेजेगा।")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
