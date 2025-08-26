import os
import requests
import schedule
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
APP_URL = os.environ.get("APP_URL")  # e.g., https://relaxed-vannie-asew-a4c78a9c.koyeb.app

CHAT_ID = 6268938019
bot = Bot(token=BOT_TOKEN)

# API URLs
LOGIN_URL = "https://admin2.khanglobalstudies.com/api/login-with-password"
LESSONS_URL = "https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/v2-lessons?new=1&medium=1"

# Courses with names and group chat IDs
COURSES = {
    "802": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 English Medium (Offline Prayagraj) | Price: ₹35000"},
    "801": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 Hindi Medium (Offline Prayagraj) | Price: ₹35000"},
    "800": {"name": "BPSC AEDO BATCH 2025 | Price: ₹999"},
    "799": {"name": "LIC AAO (Pre + Mains) TARGET BATCH 2025 | Price: ₹799"},
    "798": {"name": "Indian Map 2025 By Khan Sir | Price: ₹200"},
    "797": {"name": "UP SI Batch 2025"},
    "796": {"name": "CDS 2 2026 Target Batch  (Dehradun Offline) | Price: ₹40000"},
    "795": {"name": "CDS 1 2026 Target Batch (Dehradun Offline) | Price: ₹25000"},
    "794": {"name": "NDA 2 2026 Target Batch  (Dehradun Offline) | Price: ₹40000"},
    "793": {"name": "NDA 1 2026 Target Batch (Dehradun Offline) | Price: ₹25000"},
    "792": {"name": "RAS Pre + PSI Officer Batch 2025 | Price: ₹999 "},
    "791": {"name": "GS Crash Course By Khan Sir & Team | Price: ₹99", "chat_id": "6465713273"},
    "790": {"name": "UPSC EPFO 2025 APFC & EO/AO | Price: ₹1999","chat_id": "6972386636"},
    "789": {"name": "CDS OTA 01 2026 Pratishta Batch | Price: ₹1199"},
    "788": {"name": "CDS 01 2026 Prakhar Batch | Price: ₹1499"},
    "787": {"name": "NDA 01 2026 Yodha Batch | Price: ₹1499"},
    "786": {"name": "MPPSC Food Safety Batch 2025 | Price: ₹999"},
    "785": {"name": "SBI CLERK (Pre + Mains) Target batch 2025 | Price: ₹399"},
    "784": {"name": "Bihar SSC CGL 4 (PT + Mains) Batch 2025 | Price: ₹599"},
    "783": {"name": "Bihar SSC कार्यालय परिचारी Batch 2025 | Price: ₹399"},
    "782": {"name": "UP LT Grade Biology Batch 2025 | Price: ₹799"},
    "781": {"name": "UP LT Grade Home Science Batch 2025 | Price: ₹799"},
    "780": {"name": "Biology Foundation 2025 Batch By Amrita Ma'am | Price: ₹299"},
    "779": {"name": "GK/GS DAILY TEST WITH DISCUSSION | Price: ₹99"},
    "778": {"name": "UPPCS Paper 5 & 6 Module Recorded Batch | Price: ₹1499"},
    "777": {"name": "UP LT Grade Commerce Batch 2025 | Price: ₹799"},
    "776": {"name": "UP LT Grade Social Studies Batch 2025 | Price: ₹799", "chat_id": "1193912277"},
    "775": {"name": "UP LT Grade Maths Batch 2025 | Price: ₹799", "chat_id": "1298108783"},
    "774": {"name": "UP LT Grade Science (Chemistry+Physics) Batch 2025 | Price: ₹799"},
    "773": {"name": "UP LT Grade English Batch 2025 | Price: ₹799"},
    "772": {"name": "UP LT Grade Hindi Batch 2025 | Price: ₹799"},
    "771": {"name": "UPPCS Prelims Mentorship Programme 2025 | Price: ₹999"},
    "770": {"name": "INTELLIGENCE BUREAU SECURITY ASSISTANT/EXECUTIVE SPY SQUAD Target Batch-2025 (Bilingual) | Price: ₹499"},
    "769": {"name": "Half Yearly Current Affairs PDF Batch (For SSC & State Exams) | Price: ₹None"},
    "768": {"name": "Classroom off-Line BPSC Batch- IV 2025 (Branch- Boring Road) | Price: ₹20000"},
    "767": {"name": "Foundation BPSC on-line (P.T + Mains+Interview) Batch-IV - Bilingual | Price: ₹4500"},
    "766": {"name": "Triveni Batch For MPPSC | Price: ₹999"},
    "765": {"name": "UPPSC (Pre+ Mains) Foundation Batch 2026 English Medium | Price: ₹4999"},
    "764": {"name": "Bihar Police Driver Batch 2025 | Price: ₹499"},
    "763": {"name": "IB ACIO (Tier-I & II) Target Batch -2025 | Price: ₹999"},
    "762": {"name": "CUET 2026 Vision Batch (Science Domain) | Price: ₹1499"},
    "761": {"name": "RRB Technician Grade 1 & Grade 3 Batch 2025 | Price: ₹799"},
    "758": {"name": "CAPF AC 2026  Foundation Batch | Price: ₹1999"},
    "757": {"name": "CAPF + CDS 2026 Foundation Batch (Dehradun Offline) | Price: ₹30000"},
    "756": {"name": "UPPSC (Prelims +Mains) Foundation Batch 2026 | Price: ₹4999", "chat_id": "6820348443"},
    "755": {"name": "MPTET VARG 3 चयन परीक्षा Practice Batch | Price: ₹199"},
    "754": {"name": "Mind Calculation Batch – 2025 | Price: ₹199"},
    "753": {"name": "Civil Engineering Geotechnical Masterclass Batch by Amanpreet Sir | Price: ₹299"},
    "751": {"name": "UPSC G.S (Prelims+Mains) Foundation Programme 2026 English Medium (Offline Class) Karol Bagh | Price: ₹79500"},
    "750": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar | Price: ₹69500 |"},
    "749": {"name": "CSAT (UPSC + UPPCS) Prayagraj Classroom Programme | Price: ₹3499 ", "chat_id": "5400488190"},
    "748": {"name": "MPPSC Prelims Target Batch 2026 | Price: ₹2499"},
    "747": {"name": "MPPSC (Prelims + Mains) Foundation Batch 2026 | Price: ₹4999"},
    "746": {"name": "UGC NET/JRF Sociology Foundation Batch December 2025 | Price: ₹1499"},
    "735": {"name": "UGC NET/JRF Economics Foundation Batch December 2025 | Price: ₹1499"},
    "734": {"name": "IBPS PO/CLERK (Pre + Mains) Target batch 2025 | Price: ₹499"},
    "733": {"name": "Hindi Foundation Batch 2025 | Price: ₹499"},
    "732": {"name": "BSPHCL Technician Grade III Question Practice Batch (Bilingual) | Price: ₹299"},
    "731": {"name": "Class 11th Yearlong Bilingual Batch-II Mussalahpur Hat JEE 2027 | Price: ₹29999"},
    "730": {"name": "Class 11th Yearlong Bilingual Batch-II Boring Road JEE 2027 | Price: ₹34999"},
    "729": {"name": "Class 11th Yearlong Bilingual Batch-II Mussalahpur Hat NEET 2027 | Price: ₹29999"},
    "728": {"name": "Class 11th Yearlong Bilingual Batch-II Boring Road NEET 2027 | Price: ₹34999"},
    "727": {"name": "Repeater Batch Yearlong Boring Road (Patna) Offline Bilingual Batch NEET 2026 | Price: ₹34999"},
    "726": {"name": "Repeater Batch Yearlong Mussalahpur Hat (Patna) Offline Bilingual Batch NEET 2026 | Price: ₹29999"},
    "725": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 English Medium (Offline Prayagraj) | Price: ₹30000"},
    "724": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 Hindi Medium (Offline Prayagraj) | Price: ₹35000"},
    "723": {"name": "UGC NET/JRF Geography Foundation Batch December 2025"},
    "722": {"name": "UGC NET/JRF History Foundation Batch December 2025 | Price: ₹1499"},
    "721": {"name": "UGC NET/JRF Commerce Foundation Batch December 2025 | Price: ₹1499"},
    "720": {"name": "UGC NET/JRF Hindi Foundation Batch December 2025 | Price: ₹1499"},
    "719": {"name": "UGC NET/JRF Political Science Foundation Batch December 2025 | Price: ₹1499"},
    "718": {"name": "UGC NET/JRF Paper-I December Batch 2025", "chat_id": "1193912277"},
    "717": {"name": "BSTET Paper 1 2025 Target Batch | Price: ₹599"},
    "716": {"name": "Math Foundation Batch By Amit Sir", "chat_id": "6465713273"},
    "714": {"name": "Basic Science & Engineering Drawing Batch | Price: ₹449"},
    "713": {"name": "Diesel Mechanic Trade batch (RRB ALP) | Price: ₹449"},
    "712": {"name": "Electrician Trade Batch (RRB ALP) | Price: ₹449"},
    "711": {"name": "Fitter Trade Batch (RRB ALP) | Price: ₹449"},
    "710": {"name": "Computer Foundation Batch 2.0 | Price: ₹249"},
    "709": {"name": "72nd BPSC Foundation Batch VI (Online) | Price: ₹4500"},
    "708": {"name": "72nd BPSC Foundation Batch VI (Offline) | Price: ₹15000"},
    "707": {"name": "विजेता 2.0 बैच – 71वीं बीपीएससी प्रारंभिक परीक्षा | Price: ₹499"},
    "706": {"name": "DELHI POLICE प्रहरी Batch-2025 | Price: ₹799"},
    "705": {"name": "Geography Optional English Medium (Live + Recorded Batch) | Price: ₹6999"},
    "704": {"name": "GEOGRAPHY OPTIONAL HINDI MEDIUM SACHIN ARORA", "chat_id": "-1002871614152"},
    "703": {"name": "Geography Optional Hindi Medium (Recorded Batch) | Price: ₹6999"},
    "702": {"name": "NEETFLIX- Recorded Batch For NEET Preparation (Hindi Medium) | Price: ₹999"},
    "701": {"name": "NEETFLIX- Recorded Batch For NEET Preparation (English Medium) | Price: ₹999"},
    "700": {"name": "HISTORY OPTIONAL HINDI MEDIUM", "chat_id": "-1002662799575"},
    "698": {"name": "Maths Optional Bilingual"},
    "697": {"name": "Hindi Literature Optional"},
    "696": {"name": "PSIR (राजनीति विज्ञान और अंतर्राष्ट्रीय संबंध) Hindi Medium", "chat_id": "-1002898647258"},
    "695": {"name": "History Optional English Medium"},
    "694": {"name": "Public Administration Optional English Medium"},
    "693": {"name": "Sociology Optional English Medium"},
    "692": {"name": "Foundation (Recorded Batch) by Khan Sir"},
    "691": {"name": "UPSC Adhyan Current Affairs (Hindi Medium) Batch 2026", "chat_id": "-1002821163148"},
    "690": {"name": "UPSC Adhyan Current Affairs (English Medium) Batch 2026"},
    "689": {"name": "Agniveer Vayu + Navy SSR || MR + ICG Foundation Batch 2025"},
    "688": {"name": "SSC GD Foundation Batch 2025-26"},
    "687": {"name": "RRB NTPC 2025 – INJECTION Batch By PK Sir"},
    "686": {"name": "UPSC Mains Answer Writing Program 2025", "chat_id": "-1002565001732"},
    "685": {"name": "Class 10th Students NEET JEE Foundation Offline Batch at Prayagraj"},
    "684": {"name": "Class 10th Students NEET JEE Foundation Offline Batch at Boring Road Patna"},
    "683": {"name": "Economics Foundation By Khan Sir (Recorded)"},
    "682": {"name": "Biology Foundation By Khan Sir (Recorded)"},
    "681": {"name": "History Foundation By Khan Sir (Recorded)"},
    "680": {"name": "Chemistry Foundation By Khan Sir (Recorded)"},
    "679": {"name": "Physics Foundation By Khan Sir (Recorded)"},
    "678": {"name": "Indian Map by Khan Sir (Recorded)"},
    "677": {"name": "Polity Foundation by Khan Sir (Recorded)"},
    "676": {"name": "Geography Foundation By Khan Sir (Recorded)"},
    "675": {"name": "BPSC TRE 4.0 Class (1 to 5) Recorded"},
    "674": {"name": "BPSC TRE 4.0 Class (6 to 8 & 9 to 10) Recorded"},
    "672": {"name": "DI Special Batch 2025"},
    "671": {"name": "UPSC G.S (Prelims+Mains) Foundation Programme 2026 English Medium (Offline Class) Karol Bagh"},
    "670": {"name": "UPSC G.S (Prelims+Mains)फाउंडेशन प्रोग्राम 2026 हिंदी माध्यम (Offline Class) Mukherjee Nagar", "chat_id": "-1002642433551"},
    "669": {"name": "UPSC Essay and Ethics Module 2025 by Dharmendra Sir (Hindi Medium)"},
    "668": {"name": "UPSC Essay and Ethics Module 2025 (English Medium)"},
    "667": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 Hindi Medium", "chat_id": "-1002810220072"},
    "666": {"name": "UPSC (Pre + Mains) Foundation Batch 2026 (English Medium)"},
    "663": {"name": "NEET 2026 Physics By Mohit Agarwal Sir (Hindi Medium)"},
    "662": {"name": "NEET 2026 Physics By Mohit Agarwal Sir (English Medium)"},
    "661": {"name": "Puzzle Special Batch (For All Banking & Insurance Exam)"},
    "660": {"name": "KVS उन्नति Foundation Batch 2025 (For TGT)"},
    "658": {"name": "NDA offline Musallahpur"},
    "657": {"name": "UPSSSC PET Batch 2025"},
    "656": {"name": "Class 12th Pass/Dropper Students Offline Yearlong Bilingual Batch - II Prayagraj NEET 2026"},
    "655": {"name": "Class 12th Pass/Dropper Students Offline Yearlong Bilingual Batch - II Mussalahpur Hat NEET 2026"},
    "654": {"name": "Class 12th Pass/Dropper Students Offline Yearlo Bilingual Batch - II Boring Road NEET 2026"},
    "653": {"name": "Class 12th/12th Pass Offline Yearlong Bilingual Batch Guwahati NEET 2026"},
    "652": {"name": "Class 11th Offline Yearlong Bilingual Batch Guwahati NEET 2027"},
    "651": {"name": "SSB Interview Program"},
    "650": {"name": "JEE ADVANCED 2025"},
    "649": {"name": "BSSC Field Assistant Batch 2025"},
    "648": {"name": "SSC JE Electrical Engineering Batch 2025-26"},
    "647": {"name": "SSC JE Mechanical Engineering Batch 2025-26"},
    "646": {"name": "SSC JE Civil Engineering Batch 2025-26"},
    "645": {"name": "Rajasthan Police Constable Batch 2025"},
    "644": {"name": "GK/GS DAILY TEST WITH DISCUSSION"},
    "643": {"name": "RRB ALP Batch 2025"},
    "642": {"name": "KVS उन्नति Foundation Batch 2025 (TGT Social Studies)"},
    "641": {"name": "error"},
    "640": {"name": "KVS उन्नति Foundation Batch 2025 (TGT Science)"},
    "639": {"name": "error"},
    "638": {"name": "KVS उन्नति Foundation Batch 2025 (TGT English)"},
    "637": {"name": "KVS उन्नति Foundation Batch 2025 (TGT Hindi)"},
    "636": {"name": "KVS उन्नति Foundation Batch 2025 ( PRT)"},
    "635": {"name": "Rajasthan Special GK Batch"},
    "634": {"name": "Rajasthan 4th Grade 2025"},
    "633": {"name": "RRB पंचायत 1.0 RRB PO/CLERK 2025"},
    "632": {"name": "MPPSC Mains Answer Writing Program 2025"},
    "631": {"name": "Navy SSR VOD + Live Practice Batch"},
    "630": {"name": "MP व्यापम महापैक Batch 2025"},
    "629": {"name": "SSC Reasoning Foundation Batch 2025-26"},
    "628": {"name": "SSC English Foundation Batch 2025-26"},
    "627": {"name": "SSC Maths Foundation Batch 2025-26"},
    "626": {"name": "SSC Mahapack 2.0 Batch 2025-26 (Bilingual)"},
    "625": {"name": "AE Foundation Civil Engineering Batch 2025"},
    "624": {"name": "UPSC & UPPSC (Pre+Mains) Foundation Batch 2026 Hindi Medium (Offline Prayagraj)"},
    "623": {"name": "UPSC Foundation Offline Batch - 2026 (Musallahpur)"},
    "622": {"name": "UPSC Foundation Offline Batch - 2026 (Boring Road)"},
    "621": {"name": "SSC CGL Tier-1 Practice Batch 2025"},
    "620": {"name": "UP SI (Moolvidhi + Polity) Batch 2025"},
    "619": {"name": "UP SI Batch 2025"},
    "618": {"name": "SSB Interview Program"},
    "617": {"name": "Pocket GK Batch 2025", "chat_id": "-1002887628954"},
    "616": {"name": "CDS 02 2025 Target Batch"},
    "615": {"name": "NDA 02 2025 Target Batch"},
    "614": {"name": "Foundation BPSC on-line (P.T + Mains+Interview) Batch-V Hindi Medium"},
    "613": {"name": "Classroom Off-line BPSC (Pre + Mains + Interview) Foundation Batch - V (Musallahpur)"},
    "612": {"name": "Biology Foundation by Khan Sir"},
    "611": {"name": "Chemistry Foundation by Khan Sir"},
    "610": {"name": "Economics Foundation by Khan Sir"},
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
    "592": {"name": "Class 11th VISION BATCH JEE 2027 BILINGUAL", "chat_id": "8064538295"},
    "591": {"name": "Bihar Police Batch 2025"},
    "372": {"name": "Geography optional english medium", "chat_id": "-1002170644891"}
}

# Multiple groups with their topic IDs
GROUPS = {
    # --- Pehla group (tumhara real group jisme topics diye hue the) ---
    -1002810170749: {   # Group 1 (REAL)
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

    # --- Dusra group (dummy, apna real ID daalna) ---
    -1002170592198: {   # Group 2
        "797": 4616,
        "696": 4617,
        "802": 23,
    },

    # --- Teesra group (dummy) ---
    -1002171722847: {   # Group 3
        "696": 315,
        "797": 314,
    },

    # --- Chautha group (dummy) ---
    -1002922862014: {   # Group 4
        "696": 47,
        "797": 46,
    },
}

# Authorized Users
AUTH_USERS = {
    6268938019: ["696"],
    5400488190: ["696","749"],
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
def fetch_and_send():
    global stop_flag
    if stop_flag:   # agar stop command diya hai
        return

    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed! Check credentials.")
        return
    
    for course_id, course_info in COURSES.items():
        if stop_flag:   # loop ke beech me bhi check
            break

        try:
            if "chat_id" not in course_info:
                continue
                
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
                if stop_flag:   # agar /stop aa gaya to class bhejna bhi band
                    break
                telegram_send(course_info["chat_id"], format_class_message(cls, course_info["name"]))
        except Exception as e:
            print(f"[!] Error in course {course_id}: {e}")

def fetch_and_send_to_owner_only():
    if not login():
        telegram_send(CHAT_ID, f"{CREDIT_MESSAGE}\n❌ Login failed! Check credentials.")
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
                telegram_send(CHAT_ID, format_class_message(cls, course_info["name"]))
        except Exception as e:
            print(f"[!] Error in course {course_id}: {e}")

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
        "/send - Owner only\n/grpsend - All groups\n/allsend - One group all topics\n/class - Your subscribed course\n/ping - Alive check\n/help - Show help\n/start - Public info\n\n" + CREDIT_MESSAGE,
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
        
def send(update: Update, context: CallbackContext):
    if update.effective_chat.id != CHAT_ID:
        update.message.reply_text("❌ Unauthorized")
        return

    args = context.args

    # Agar arguments diye gaye hain
    if args:
        target_chat_id = args[0]  # pehla argument hamesha chat_id hoga
        if not target_chat_id.lstrip("-").isdigit():
            update.message.reply_text("⚠️ Invalid chat_id. Example: /send -1001234567890 OR /send -1001234567890 696")
            return

        target_chat_id = int(target_chat_id)

        # Agar sirf chat_id diya hai
        if len(args) == 1:
            update.message.reply_text(f"⏳ Sending ALL courses to chat {target_chat_id}...")
            if not login():
                update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
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
                        telegram_send(target_chat_id, format_class_message(cls, course_info["name"]))
                except Exception as e:
                    print(f"[!] Error in course {course_id}: {e}")

            update.message.reply_text("✅ Done!")
            return

        # Agar chat_id + course_id dono diye hain
        elif len(args) == 2:
            course_id = args[1]
            course_info = COURSES.get(course_id)
            if not course_info:
                update.message.reply_text(f"⚠️ Course ID {course_id} not found in COURSES list.")
                return

            if not login():
                update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed!", parse_mode="HTML")
                return

            update.message.reply_text(f"⏳ Sending {course_info['name']} to chat {target_chat_id}...")

            try:
                url = LESSONS_URL.format(course_id=course_id)
                r = requests.get(url, headers=headers)
                data = r.json()

                if not data.get("success", True):
                    update.message.reply_text(f"⚠️ API error: {data.get('message')}")
                    return

                today_classes = data.get("todayclasses", [])
                if not today_classes:
                    update.message.reply_text(f"📭 No updates found today for {course_info['name']}.")
                    return

                for cls in today_classes:
                    telegram_send(target_chat_id, format_class_message(cls, course_info["name"]))

                update.message.reply_text("✅ Done!")
            except Exception as e:
                update.message.reply_text(f"⚠️ Error: {str(e)}")
            return

        else:
            update.message.reply_text("⚠️ Invalid usage. Example:\n/send -1001234567890\n/send -1001234567890 696")
            return

    # Agar koi argument nahi diya hai → default old behaviour (owner chat me hi bhejna)
    else:
        update.message.reply_text("⏳ Fetching updates...")
        fetch_and_send_to_owner_only()
        update.message.reply_text("✅ Done!")

def grpsend(update: Update, context: CallbackContext):
    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text("⏳ Sending to all groups...")
        fetch_and_send()
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

def class_command(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    args = context.args  # /class ke baad ka text

    # --- Owner ka special feature ---
    if user_id == CHAT_ID and args:
        course_id = args[0]  # First argument as course ID
        course_info = COURSES.get(course_id)
        if not course_info:
            update.message.reply_text(f"⚠️ Course info not found for ID {course_id}.")
            return
        if not login():
            update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed! Try again later.", parse_mode="HTML")
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
                update.message.reply_text(f"📭 No updates found today for {course_info['name']}.")
                return
            
            update.message.reply_text(f"⏳ Fetching {len(today_classes)} classes...")
            for cls in today_classes:
                telegram_send(user_id, format_class_message(cls, course_info["name"]))
            update.message.reply_text("✅ Done!")
        except Exception as e:
            update.message.reply_text(f"⚠️ Error: {str(e)}")
        return

    # --- Authorized user ka normal feature ---
    if user_id not in AUTH_USERS:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    user_courses = AUTH_USERS[user_id]  # List of course IDs
    if not login():
        update.message.reply_text(f"{CREDIT_MESSAGE}\n❌ Login failed! Try again later.", parse_mode="HTML")
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
                update.message.reply_text(f"📭 No updates found today for {course_info['name']}.")
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
dispatcher.add_handler(CommandHandler("send", send))
dispatcher.add_handler(CommandHandler("stop", stop_command))
dispatcher.add_handler(CommandHandler("grpsend", grpsend))
dispatcher.add_handler(CommandHandler("allsend", allsend))
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

# --- Scheduler ---
def scheduler_job():
    print("⏰ Running scheduled job...")
    fetch_and_send()

schedule.every().day.at("21:30").do(scheduler_job)

def run_scheduler():
    global stop_flag
    while True:
        if stop_flag:
            print("⏹ Scheduler stopped.")
            break
        schedule.run_pending()
        time.sleep(10)
        
if __name__ == "__main__":
    set_webhook()
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
