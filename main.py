import os
import requests
import threading
import time
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Dispatcher

# ✅ Load from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
APP_URL = os.environ.get("APP_URL")  # e.g., https://yourapp.koyeb.app

CHAT_ID = 6268938019
bot = Bot(token=BOT_TOKEN)

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Courses with names and group chat IDs
COURSES = {
    "802": {"name": "UPSC & UPPSC Foundation 2026 English Medium"},
    "801": {"name": "UPSC & UPPSC Foundation 2026 Hindi Medium"},
    "800": {"name": "BPSC AEDO BATCH 2025"},
    "799": {"name": "LIC AAO TARGET BATCH 2025"},
    "798": {"name": "Indian Map 2025"},
    "797": {"name": "UP SI Batch 2025"},
    "372": {"name": "Geography optional english medium", "chat_id": "-1002170644891"}
}

# Multiple groups with their topic IDs
GROUPS = {
    -1002810170749: {  # Group 1 (REAL)
        "696": 5,
        "686": 6,
        "691": 10,
        "704": 11,
        "700": 12,
        "667": 13,
        "670": 14,
        "617": 15,
        "372": 16,
        "718": 17,
        "716": 18,
        "749": 37,
        "750": 38,
        "756": 41,
        "723": 117,
        "797": 446,
        "798": 467,
        "790": 540,
    },
    -1002170592198: {  # Group 2
        "797": 4616,
        "696": 4617,
        "802": 23,
    },
    -1002171722847: {  # Group 3
        "696": 315,
        "797": 314,
    },
    -1002922862014: {  # Group 4
        "696": 47,
        "797": 46,
    },
}

# Authorized Users
AUTH_USERS = {
    6268938019: ["696"],
    5400488190: ["696", "749"],
}

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "Bearer undefined"
}

CREDIT_MESSAGE = "𝗧𝗛𝗜𝗦 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗕𝗬 💞𝙼𝚁 𝚁𝙰𝙹𝙿𝚄𝚃💞"

# --- Global Stop Flag ---
stop_flag = False

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

# --- Fetch Functions ---
def fetch_and_send_to_group_topics():
    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed! Check credentials.")
        return

    for group_id, topic_map in GROUPS.items():  # loop per group
        for course_id, topic_id in topic_map.items():  # loop per topic inside that group
            try:
                url = LESSONS_URL.format(course_id=course_id)
                r = requests.get(url, headers=headers)
                data = r.json()

                if not data.get("success", True):
                    print(f"[!] API error for course {course_id}: {data.get('message')}")
                    continue

                today_classes = data.get("todayclasses", [])
                course_name = COURSES.get(course_id, {}).get("name", "Unknown Course")

                if not today_classes:
                    print(f"[i] No classes today for {course_name}")
                    continue

                for cls in today_classes:
                    telegram_send(group_id, format_class_message(cls, course_name), message_thread_id=topic_id)
            except Exception as e:
                print(f"[!] Error in allsend for course {course_id} in group {group_id}: {e}")

# --- Commands ---
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/grpsend - All groups\n/allsend - One group all topics\n/class - Your subscribed course\n/ping - Alive check\n/help - Show help\n/start - Public info\n\n" + CREDIT_MESSAGE,
        parse_mode="HTML"
    )

def ping(update: Update, context: CallbackContext):
    update.message.reply_text(f"✅ Bot is Alive!\n{CREDIT_MESSAGE}", parse_mode="HTML")

def stop_command(update: Update, context: CallbackContext):
    global stop_flag
    if update.effective_chat.id == CHAT_ID:  # sirf owner hi use kar sake
        stop_flag = True
        update.message.reply_text("⏹ All running processes stopped!")
    else:
        update.message.reply_text("❌ Unauthorized")

def grpsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text("⏳ Sending to all groups...")
        fetch_and_send_to_group_topics()
        update.message.reply_text("✅ Done!")
    else:
        update.message.reply_text("❌ Unauthorized")

def allsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text("⏳ Sending to group topics...")
        fetch_and_send_to_group_topics()
        update.message.reply_text("✅ Done!")
    else:
        update.message.reply_text("❌ Unauthorized")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("<b>इस बोट के द्वारा खान ग्लोबल स्टडीज के सभी batches की लाइव क्लास daily भेजी जाती है</b>", parse_mode="HTML")

def sendto_command(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    
    # Sirf owner hi use kar paye
    if user_id != CHAT_ID:
        update.message.reply_text("❌ Unauthorized")
        return
    
    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /sendto <chat_id> <course_id>")
        return
    
    chat_id = context.args[0]
    course_id = context.args[1]
    
    course_info = COURSES.get(course_id)
    if not course_info:
        update.message.reply_text(f"⚠️ Course not found for ID {course_id}.")
        return
    
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
        return
    
    url = LESSONS_URL.format(course_id=course_id)
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        if not data.get("success", True):
            update.message.reply_text(f"⚠️ API error: {data.get('message')}")
            return
        
        today_classes = data.get("todayclasses", [])
        if not today_classes:
            update.message.reply_text(f"📭 No updates today for {course_info['name']}.")
            return
        
        update.message.reply_text(f"⏳ Sending {len(today_classes)} classes of {course_info['name']} to {chat_id}...")
        for cls in today_classes:
            telegram_send(chat_id, format_class_message(cls, course_info["name"]))
        update.message.reply_text("✅ Done!")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}")
        
def class_command(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    args = context.args

    # --- Owner special ---
    if user_id == CHAT_ID and args:
        course_id = args[0]
        course_info = COURSES.get(course_id)
        if not course_info:
            update.message.reply_text(f"⚠️ Course info not found for ID {course_id}.")
            return
        if not login():
            update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
            return
        
        url = LESSONS_URL.format(course_id=course_id)
        try:
            r = requests.get(url, headers=headers)
            data = r.json()
            if not data.get("success", True):
                update.message.reply_text(f"⚠️ API error: {data.get('message')}")
                return
                
            today_classes = data.get("todayclasses", [])
            if not today_classes:
                update.message.reply_text(f"📭 No updates today for {course_info['name']}.")
                return
            
            update.message.reply_text(f"⏳ Fetching {len(today_classes)} classes...")
            for cls in today_classes:
                telegram_send(user_id, format_class_message(cls, course_info["name"]))
            update.message.reply_text("✅ Done!")
        except Exception as e:
            update.message.reply_text(f"⚠️ Error: {str(e)}")
        return

    # --- Normal authorized users ---
    if user_id not in AUTH_USERS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    user_courses = AUTH_USERS[user_id]
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
        return
    
    update.message.reply_text("⏳ Fetching your classes...")
    for course_id in user_courses:
        course_info = COURSES.get(course_id)
        if not course_info:
            update.message.reply_text(f"⚠️ Course info not found for ID {course_id}.")
            continue
        
        url = LESSONS_URL.format(course_id=course_id)
        try:
            r = requests.get(url, headers=headers)
            data = r.json()
            if not data.get("success", True):
                update.message.reply_text(f"⚠️ API error for course {course_id}: {data.get('message')}")
                continue
                
            today_classes = data.get("todayclasses", [])
            if not today_classes:
                update.message.reply_text(f"📭 No updates today for {course_info['name']}.")
                continue
            
            for cls in today_classes:
                telegram_send(user_id, format_class_message(cls, course_info["name"]))
        except Exception as e:
            update.message.reply_text(f"⚠️ Error in course {course_id}: {str(e)}")
    
    update.message.reply_text("✅ Done!")

# --- Flask App ---
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# Register all commands in dispatcher
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("ping", ping))
dispatcher.add_handler(CommandHandler("stop", stop_command))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_handler(CommandHandler("allsend", allsend))
dispatcher.add_handler(CommandHandler("sendto", sendto_command))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("class", class_command))

@app.route("/")
def home():
    return "Bot Active!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "", 200

# --- Auto Webhook Set ---
def set_webhook():
    if APP_URL:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            url = f"{APP_URL}/webhook"
            bot.set_webhook(url)
            print("[Webhook set]:", url)
        except Exception as e:
            print(f"[!] Error setting webhook: {e}")
    else:
        print("[!] APP_URL not set, webhook not configured")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
