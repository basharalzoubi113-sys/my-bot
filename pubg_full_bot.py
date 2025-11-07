import telebot
import random
import json
import os
import time

BOT_TOKEN = "8449125516:AAFr5xM2suBp-0J1LCrePC5UJoV7-V7h6uw"
CHANNEL_USERNAME = "@Hack_CarX_Street"  # بدون https
ADMIN_ID = 6139388819
bot = telebot.TeleBot(BOT_TOKEN)

SAVE_FILE = "accounts.json"
USED_FILE = "used_accounts.json"

# تحميل الحسابات
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        ACCOUNTS = json.load(f)
else:
    ACCOUNTS = []

if os.path.exists(USED_FILE):
    with open(USED_FILE, "r") as f:
        user_accounts = json.load(f)
else:
    user_accounts = {}

# === دالة التحقق الحقيقي من الاشتراك ===
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except telebot.apihelper.ApiTelegramException as e:
        if "user not found" in str(e):
            return False
        return False
    except:
        return False

# === لوحة الأدمن ===
def admin_panel():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("إضافة حساب", "عرض الحسابات", "عرض المستخدمين", "حذف كل الحسابات")
    markup.add("Start")
    return markup

# === لوحة المستخدم ===
def main_menu_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("حساب مجاني")
    markup.add("Start")
    return markup

# === /start ===
@bot.message_handler(commands=["start"])
def start_cmd(message):
    send_welcome(message.chat.id)

def send_welcome(chat_id):
    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "*لوحة تحكم الأدمن*", reply_markup=admin_panel(), parse_mode='Markdown')
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("تشغيل البوت"))
        markup.add("Start")
        bot.send_message(chat_id, "أهلاً! اضغط على الزر لتشغيل البوت:", reply_markup=markup)

# === تحقق حقيقي + زر اشتراك ===
def send_real_subscribe(chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    check_btn = telebot.types.InlineKeyboardButton("تحقق من الاشتراك", callback_data="real_verify")
    markup.add(btn)
    markup.add(check_btn)
    bot.send_message(chat_id, 
        "يجب أن تكون مشتركًا في القناة لاستخدام البوت:\n"
        f"القناة: {CHANNEL_USERNAME}", 
        reply_markup=markup)

# === معالجة الأزرار ===
@bot.message_handler(func=lambda msg: True)
def handle(message):
    global ACCOUNTS, user_accounts
    user_id = str(message.chat.id)
    text = message.text

    # === زر Start ===
    if text == "Start":
        send_welcome(message.chat.id)
        return

    # === الأدمن ===
    if message.chat.id == ADMIN_ID:
        if text == "إضافة حساب":
            bot.send_message(message.chat.id, "أرسل الحساب: `email|pass`", parse_mode='Markdown')
            bot.register_next_step_handler(message, add_account_step)
        elif text == "عرض الحسابات":
            txt = "\n".join(ACCOUNTS) if ACCOUNTS else "لا توجد"
            bot.send_message(message.chat.id, f"*المتبقية:*\n\n`{txt}`", parse_mode='Markdown')
        elif text == "عرض المستخدمين":
            txt = "\n\n".join([f"`{u}` → `{a}`" for u, a in user_accounts.items()]) if user_accounts else "لا يوجد"
            bot.send_message(message.chat.id, f"*المنصرفة:*\n\n{txt}", parse_mode='Markdown')
        elif text == "حذف كل الحسابات":
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("تأكيد", callback_data="confirm_delete"))
            markup.add(telebot.types.InlineKeyboardButton("إلغاء", callback_data="cancel"))
            bot.send_message(message.chat.id, "*تحذير: حذف نهائي!*", reply_markup=markup, parse_mode='Markdown')

    # === المستخدم العادي ===
    else:
        if text == "تشغيل البوت":
            if is_user_subscribed(message.chat.id):
                bot.send_message(message.chat.id, "البوت شغال!", reply_markup=main_menu_keyboard())
            else:
                send_real_subscribe(message.chat.id)

        elif text == "حساب مجاني":
            if not is_user_subscribed(message.chat.id):
                send_real_subscribe(message.chat.id)
                return

            if user_id in user_accounts:
                bot.send_message(message.chat.id, f"سبق وأخذت:\n`{user_accounts[user_id]}`", parse_mode='Markdown')
            elif ACCOUNTS:
                acc = random.choice(ACCOUNTS)
                ACCOUNTS.remove(acc)
                user_accounts[user_id] = acc
                save_accounts()
                bot.send_message(message.chat.id, f"*حسابك:*\n`{acc}`", parse_mode='Markdown')
                bot.send_message(ADMIN_ID, f"مستخدم جديد:\n`{user_id}`\n`{acc}`", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "ما فيه حسابات.")

# === إضافة حساب ===
def add_account_step(message):
    if message.chat.id != ADMIN_ID: return
    acc = message.text.strip()
    if "|" not in acc:
        bot.send_message(message.chat.id, "خطأ: `email|pass`")
        return
    ACCOUNTS.append(acc)
    save_accounts()
    bot.send_message(message.chat.id, f"تم إضافة:\n`{acc}`", parse_mode='Markdown')

# === حفظ ===
def save_accounts():
    with open(SAVE_FILE, "w") as f:
        json.dump(ACCOUNTS, f, indent=2)
    with open(USED_FILE, "w") as f:
        json.dump(user_accounts, f, indent=2)

# === تحقق حقيقي عند الضغط ===
@bot.callback_query_handler(func=lambda call: call.data == "real_verify")
def real_verify(call):
    user_id = call.message.chat.id
    if is_user_subscribed(user_id):
        bot.answer_callback_query(call.id, "تم التحقق بنجاح!")
        bot.edit_message_text("تم التحقق! البوت جاهز.", call.message.chat.id, call.message.message_id)
        bot.send_message(user_id, "البوت شغال!", reply_markup=main_menu_keyboard())
    else:
        bot.answer_callback_query(call.id, "لم تشترك بعد!", show_alert=True)
        time.sleep(1)
        send_real_subscribe(user_id)

# === حذف كل الحسابات ===
@bot.callback_query_handler(func=lambda call: True)
def confirm(call):
    if call.from_user.id != ADMIN_ID: return
    if call.data == "confirm_delete":
        global ACCOUNTS, user_accounts
        ACCOUNTS = []
        user_accounts = {}
        save_accounts()
        bot.edit_message_text("تم حذف كل الحسابات!", call.message.chat.id, call.message.message_id)
    elif call.data == "cancel":
        bot.edit_message_text("تم الإلغاء.", call.message.chat.id, call.message.message_id)

# === تشغيل ===
print("البوت شغال مع تحقق حقيقي...")
bot.infinity_polling()