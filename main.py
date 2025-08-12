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
    "789": {"name": "CDS OTA 01 2026 Pratishta Batch | Price: ₹1199", "chat_id": "0000000000"},
    "788": {"name": "CDS 01 2026 Prakhar Batch | Price: ₹1499", "chat_id": "0000000000"},
    "787": {"name": "NDA 01 2026 Yodha Batch | Price: ₹1499", "chat_id": "0000000000"},
    "786": {"name": "MPPSC Food Safety Batch 2025 | Price: ₹999", "chat_id": "0000000000"},
    "785": {"name": "SBI CLERK (Pre + Mains) Target batch 2025 | Price: ₹399", "chat_id": "0000000000"},
    "784": {"name": "Bihar SSC CGL 4 (PT + Mains) Batch 2025 | Price: ₹599", "chat_id": "0000000000"},
    "783": {"name": "Bihar SSC कार्यालय परिचारी Batch 2025 | Price: ₹399", "chat_id": "0000000000"},
    "782": {"name": "UP LT Grade Biology Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "781": {"name": "UP LT Grade Home Science Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "780": {"name": "Biology Foundation 2025 Batch By Amrita Ma'am | Price: ₹299", "chat_id": "0000000000"},
    "779": {"name": "GK/GS DAILY TEST WITH DISCUSSION | Price: ₹99", "chat_id": "0000000000"},
    "778": {"name": "UPPCS Paper 5 & 6 Module Recorded Batch | Price: ₹1499", "chat_id": "0000000000"},
    "777": {"name": "UP LT Grade Commerce Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "776": {"name": "UP LT Grade Social Studies Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "775": {"name": "UP LT Grade Maths Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "774": {"name": "UP LT Grade Science (Chemistry+Physics) Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "773": {"name": "UP LT Grade English Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "772": {"name": "UP LT Grade Hindi Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "771": {"name": "UPPCS Prelims Mentorship Programme 2025 | Price: ₹999", "chat_id": "0000000000"},
    "770": {"name": "INTELLIGENCE BUREAU SECURITY ASSISTANT/EXECUTIVE SPY SQUAD Target Batch-2025 (Bilingual) | Price: ₹499", "chat_id": "0000000000"},
    "769": {"name": "Half Yearly Current Affairs PDF Batch (For SSC & State Exams) | Price: ₹None", "chat_id": "0000000000"},
    "768": {"name": "Classroom off-Line BPSC Batch- IV 2025 (Branch- Boring Road) | Price: ₹20000", "chat_id": "0000000000"},
    "767": {"name": "Foundation BPSC on-line (P.T + Mains+Interview) Batch-IV - Bilingual | Price: ₹4500", "chat_id": "0000000000"},
    "766": {"name": "Triveni Batch For MPPSC | Price: ₹999", "chat_id": "0000000000"},
    "765": {"name": "UPPSC (Pre+ Mains) Foundation Batch 2026 English Medium | Price: ₹4999", "chat_id": "0000000000"},
    "764": {"name": "Bihar Police Driver Batch 2025 | Price: ₹499", "chat_id": "0000000000"},
    "763": {"name": "IB ACIO (Tier-I & II) Target Batch -2025 | Price: ₹999", "chat_id": "0000000000"},
    "762": {"name": "CUET 2026 Vision Batch (Science Domain) | Price: ₹1499", "chat_id": "0000000000"},
    "761": {"name": "RRB Technician Grade 1 & Grade 3 Batch 2025 | Price: ₹799", "chat_id": "0000000000"},
    "758": {"name": "CAPF AC 2026  Foundation Batch | Price: ₹1999", "chat_id": "0000000000"},
    "757": {"name": "CAPF + CDS 2026 Foundation Batch (Dehradun Offline) | Price: ₹30000", "chat_id": "0000000000"},
    "756": {"name": "UPPSC (Prelims +Mains) Foundation Batch 2026 | Price: ₹4999", "chat_id": "00"},
    "755": {"name": "MPTET VARG 3 चयन परीक्षा Practice Batch | Price: ₹199", "chat_id": "0000000000"},
    "754": {"name": "Mind Calculation Batch – 2025 | Price: ₹199", "chat_id": "0000000000"},
    "753": {"name": "Civil Engineering Geotechnical Masterclass Batch by Amanpreet Sir | Price: ₹299", "chat_id": "0000000000"},
    "751": {"name": "UPSC G.S (Prelims+Mains) Foundation Programme 2026 English Medium (Offline Class) Karol Bagh | Price: ₹79500", "chat_id": "0000000000"},
    "750": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar | Price: ₹69500 |", "chat_id": "0000000000"},
    "749": {"name": "CSAT (UPSC + UPPCS) Prayagraj Classroom Programme | Price: ₹3499 ", "chat_id": "0000000000"},
    "748": {"name": "MPPSC Prelims Target Batch 2026 | Price: ₹2499", "chat_id": "0000000000"},
    "747": {"name": "MPPSC (Prelims + Mains) Foundation Batch 2026 | Price: ₹4999", "chat_id": "0000000000"},
    "746": {"name": "UGC NET/JRF Sociology Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "735": {"name": "UGC NET/JRF Economics Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "734": {"name": "IBPS PO/CLERK (Pre + Mains) Target batch 2025 | Price: ₹499", "chat_id": "0000000000"},
    "733": {"name": "Hindi Foundation Batch 2025 | Price: ₹499", "chat_id": "0000000000"},
    "732": {"name": "BSPHCL Technician Grade III Question Practice Batch (Bilingual) | Price: ₹299", "chat_id": "0000000000"},
    "731": {"name": "Class 11th Yearlong Bilingual Batch-II Mussalahpur Hat JEE 2027 | Price: ₹29999", "chat_id": "0000000000"},
    "730": {"name": "Class 11th Yearlong Bilingual Batch-II Boring Road JEE 2027 | Price: ₹34999", "chat_id": "0000000000"},
    "729": {"name": "Class 11th Yearlong Bilingual Batch-II Mussalahpur Hat NEET 2027 | Price: ₹29999", "chat_id": "0000000000"},
    "728": {"name": "Class 11th Yearlong Bilingual Batch-II Boring Road NEET 2027 | Price: ₹34999", "chat_id": "0000000000"},
    "727": {"name": "Repeater Batch Yearlong Boring Road (Patna) Offline Bilingual Batch NEET 2026 | Price: ₹34999", "chat_id": "0000000000"},
    "726": {"name": "Repeater Batch Yearlong Mussalahpur Hat (Patna) Offline Bilingual Batch NEET 2026 | Price: ₹29999", "chat_id": "0000000000"},
    "725": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 English Medium (Offline Prayagraj) | Price: ₹30000", "chat_id": "0000000000"},
    "724": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 Hindi Medium (Offline Prayagraj) | Price: ₹35000", "chat_id": "0000000000"},
    "723": {"name": "UGC NET/JRF Geography Foundation Batch December 2025", "chat_id": "7879332317"},
    "722": {"name": "UGC NET/JRF History Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "721": {"name": "UGC NET/JRF Commerce Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "720": {"name": "UGC NET/JRF Hindi Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "719": {"name": "UGC NET/JRF Political Science Foundation Batch December 2025 | Price: ₹1499", "chat_id": "0000000000"},
    "718": {"name": "UGC NET/JRF Paper-I December Batch 2025", "chat_id": "1193912277"},
    "717": {"name": "BSTET Paper 1 2025 Target Batch | Price: ₹599", "chat_id": "0000000000"},
    "716": {"name": "Math Foundation Batch By Amit Sir", "chat_id": "6465713273"},
    "714": {"name": "Basic Science & Engineering Drawing Batch | Price: ₹449", "chat_id": "0000000000"},
    "713": {"name": "Diesel Mechanic Trade batch (RRB ALP) | Price: ₹449", "chat_id": "0000000000"},
    "712": {"name": "Electrician Trade Batch (RRB ALP) | Price: ₹449", "chat_id": "0000000000"},
    "711": {"name": "Fitter Trade Batch (RRB ALP) | Price: ₹449", "chat_id": "0000000000"},
    "710": {"name": "Computer Foundation Batch 2.0 | Price: ₹249", "chat_id": "0000000000"},
    "709": {"name": "72nd BPSC Foundation Batch VI (Online) | Price: ₹4500", "chat_id": "0000000000"},
    "708": {"name": "72nd BPSC Foundation Batch VI (Offline) | Price: ₹15000", "chat_id": "0000000000"},
    "707": {"name": "विजेता 2.0 बैच – 71वीं बीपीएससी प्रारंभिक परीक्षा | Price: ₹499", "chat_id": "0000000000"},
    "706": {"name": "DELHI POLICE प्रहरी Batch-2025 | Price: ₹799", "chat_id": "0000000000"},
    "705": {"name": "Geography Optional English Medium (Live + Recorded Batch) | Price: ₹6999", "chat_id": "0000000000"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA", "chat_id": "-1002871614152"},
    "703": {"name": "Geography Optional Hindi Medium (Recorded Batch) | Price: ₹6999", "chat_id": "0000000000"},
    "702": {"name": "NEETFLIX- Recorded Batch For NEET Preparation (Hindi Medium) | Price: ₹999", "chat_id": "0000000000"},
    "701": {"name": "NEETFLIX- Recorded Batch For NEET Preparation (English Medium) | Price: ₹999", "chat_id": "0000000000"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM", "chat_id": "-1002662799575"},
    "698": {"name": "Maths Optional Bilingual | Price: ₹6999", "chat_id": "0000000000"},
    "697": {"name": "Hindi Literature Optional | Price: ₹6999", "chat_id": "0000000000"},
    "696": {"name": "PSIR BY SANJAY THAKUR", "chat_id": "-1002898647258"},
    "695": {"name": "History Optional English Medium | Price: ₹6999", "chat_id": "0000000000"},
    "694": {"name": "Public Administration Optional English Medium | Price: ₹6999", "chat_id": "0000000000"},
    "693": {"name": "Sociology Optional English Medium | Price: ₹6999", "chat_id": "0000000000"},
    "692": {"name": "Foundation (Recorded Batch) by Khan Sir | Price: ₹1499", "chat_id": "0000000000"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026", "chat_id": "-1002821163148"},
    "690": {"name": "UPSC Adhyan Current Affairs (English Medium) Batch 2026 | Price: ₹999", "chat_id": "0000000000"},
    "689": {"name": "Indian Coast Guard || Agniveer Vayu || Navy SSR || MR Batch | Price: ₹799", "chat_id": "0000000000"},
    "688": {"name": "SSC GD Foundation Batch 2025-26 | Price: ₹499", "chat_id": "0000000000"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025", "chat_id": "-1002565001732"},
    "683": {"name": "Economics Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "682": {"name": "Biology Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "681": {"name": "History Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "680": {"name": "Chemistry Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "679": {"name": "Physics Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "678": {"name": "Indian Map by Khan Sir (Recorded) | Price: ₹200", "chat_id": "0000000000"},
    "677": {"name": "Polity Foundation by Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "676": {"name": "Geography Foundation By Khan Sir (Recorded) | Price: ₹300", "chat_id": "0000000000"},
    "675": {"name": "BPSC TRE 4.0 Class (1 to 5) Recorded | Price: ₹599", "chat_id": "0000000000"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar", "chat_id": "-1002642433551"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium", "chat_id": "-1002810220072"},
    "617": {"name": "Pocket gk batch", "chat_id": "-1002887628954"},
    "592": {"name": " Class 11th VISION BATCH JEE 2027 BILINGUAL | Price: ₹1999", "chat_id": "8064538295"},
    "372": {"name": "Geography optional english medium", "chat_id": "-1002170644891"}
}

# Topic IDs
GROUP_ID = -1002810170749
TOPIC_IDS = {
    "696": 5, "686": 6, "691": 10, "704": 11,
    "700": 12, "667": 13, "670": 14, "617": 15,
    "372": 16, "718": 17, "716": 18
}

# Auth Users storage file
AUTH_FILE = "auth_users.json"

def load_auth_users():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_auth_users(data):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f)

AUTH_USERS = load_auth_users()

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer undefined"
}

# Credit
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
        "/send - Owner only\n/grpsend - All groups\n/allsend - One group all topics\n/class - Your course\n/auth - Authorize user\n/unauth - Remove user\n/authlist - List users\n/ping - Alive\n/help - Help\n/start - Info\n\n" + CREDIT_MESSAGE,
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
    user_id = str(update.effective_chat.id)
    if user_id not in AUTH_USERS:
        update.message.reply_text("❌ Not authorized")
        return
    course_id = AUTH_USERS[user_id]
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
        return
    r = requests.get(LESSONS_URL.format(course_id=course_id), headers=headers)
    for cls in r.json().get("todayclasses", []):
        message = format_class_message(cls, COURSES[course_id]["name"])
        telegram_send(user_id, message)

def auth_user(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        return update.message.reply_text("❌ Unauthorized")
    if len(context.args) != 2:
        return update.message.reply_text("Usage: /auth <user_id> <course_id>")
    user_id, course_id = context.args
    AUTH_USERS[user_id] = course_id
    save_auth_users(AUTH_USERS)
    update.message.reply_text(f"✅ Authorized {user_id} for course {course_id}")

def unauth_user(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        return update.message.reply_text("❌ Unauthorized")
    if len(context.args) != 1:
        return update.message.reply_text("Usage: /unauth <user_id>")
    user_id = context.args[0]
    if user_id in AUTH_USERS:
        del AUTH_USERS[user_id]
        save_auth_users(AUTH_USERS)
        update.message.reply_text(f"✅ UnAuthorized {user_id}")
    else:
        update.message.reply_text("❌ User not found")

def auth_list(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        return update.message.reply_text("❌ Unauthorized")
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
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_handler(CommandHandler("allsend", allsend))
dispatcher.add_handler(CommandHandler("start", start))
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
    app.run(host="0.0.0.0", port=8000)
