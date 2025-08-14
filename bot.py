import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8403230749:AAGR0aSzuOGusW24Y1yWDvN0DyCfcFJCLnQ"
ADMIN_ID = 6139388819  # معرفك في تيليجرام
DATA_FILE = "data.json"

# تحميل البيانات
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# بدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    if str(user.id) not in data:
        data[str(user.id)] = {"name": user.first_name, "balance": 0}
        save_data(data)

    keyboard = [
        [InlineKeyboardButton("💼 حسابي الشخصي", callback_data="account"),
         InlineKeyboardButton("🎮 خدمات الألعاب", callback_data="games")],
        [InlineKeyboardButton("🛠 مركز الدعم", callback_data="support")]
    ]
    await update.message.reply_text(
        "مرحباً بك في البوت 🎉\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# حسابي الشخصي
async def account_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = load_data()
    bal = data[user_id]["balance"]
    text = f"⚡ حسابك:\nرصيدك الحالي: {bal} ل.س"
    keyboard = [[InlineKeyboardButton("💰 شحن رصيدي", callback_data="charge")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# شحن رصيد
async def charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Syrtel Cash", callback_data="syr")],
        [InlineKeyboardButton("USDT", callback_data="usdt")]
    ]
    await query.edit_message_text("اختر طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))

# معلومات الدفع
async def syr_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("💳 Syriatel Cash\n📱 38065983\nبعد التحويل، أرسل لقطة شاشة للإدمن.")

async def usdt_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("💳 USDT\nBEP20: 0xdde060cb91a28546e8914a525a4a19a1fac58235\nTRC20: TQVuSzibfvB5GNU4qPkiEgHN18k1SH1B1k\nالحد الأدنى 10$")

# قائمة الألعاب
async def games_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("PUBG Mobile", callback_data="pubg")]]
    await update.callback_query.edit_message_text("اختر اللعبة:", reply_markup=InlineKeyboardMarkup(keyboard))

# PUBG قائمة الباقات
async def pubg_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = {
        "60": 9507, "325": 48059, "660": 95074,
        "1800": 235074, "3850": 470149, "8100": 940298
    }
    keyboard = [[InlineKeyboardButton(f"{uc} UC - {price} ل.س", callback_data=f"buy_{uc}")]
                for uc, price in prices.items()]
    await update.callback_query.edit_message_text("اختر الباقة:", reply_markup=InlineKeyboardMarkup(keyboard))

# عند اختيار باقة
async def ask_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uc_amount = query.data.split("_")[1]
    context.user_data["uc_amount"] = uc_amount
    await query.edit_message_text(f"📌 أدخل Player ID لشحن {uc_amount} UC:")

# استقبال Player ID
async def receive_player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.text.strip()
    uc_amount = context.user_data.get("uc_amount")
    if not uc_amount:
        return

    prices = {
        "60": 9507, "325": 48059, "660": 95074,
        "1800": 235074, "3850": 470149, "8100": 940298
    }
    price = prices[uc_amount]
    user_id = str(update.effective_user.id)

    data = load_data()
    if data[user_id]["balance"] < price:
        await update.message.reply_text("❌ رصيدك غير كافي، يرجى الشحن أولاً.")
        return

    # إرسال الطلب للإدمن
    keyboard = [
        [InlineKeyboardButton("✅ قبول", callback_data=f"approve_{user_id}_{uc_amount}_{player_id}"),
         InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")]
    ]
    await context.bot.send_message(
        ADMIN_ID,
        f"📢 طلب جديد:\nالمستخدم: {data[user_id]['name']}\nID: {player_id}\nالباقة: {uc_amount} UC\nالسعر: {price} ل.س",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text("✅ تم إرسال طلبك للإدمن، سيتم الرد قريبًا.")

# قبول الطلب
async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, user_id, uc_amount, player_id = query.data.split("_")
    prices = {
        "60": 9507, "325": 48059, "660": 95074,
        "1800": 235074, "3850": 470149, "8100": 940298
    }
    price = prices[uc_amount]
    data = load_data()
    data[user_id]["balance"] -= price
    save_data(data)
    await context.bot.send_message(int(user_id), f"✅ تم شحن {uc_amount} UC لـ Player ID: {player_id}")
    await query.edit_message_text("✅ تم تنفيذ الطلب وخصم المبلغ.")

# رفض الطلب
async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, user_id = query.data.split("_")
    await context.bot.send_message(int(user_id), "❌ تم رفض طلبك.")
    await query.edit_message_text("❌ تم رفض الطلب.")

# دعم
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("للدعم تواصل مع: @Bashar2005Syria")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(account_info, pattern="account"))
app.add_handler(CallbackQueryHandler(charge, pattern="charge"))
app.add_handler(CallbackQueryHandler(syr_info, pattern="syr"))
app.add_handler(CallbackQueryHandler(usdt_info, pattern="usdt"))
app.add_handler(CallbackQueryHandler(games_list, pattern="games"))
app.add_handler(CallbackQueryHandler(pubg_info, pattern="pubg"))
app.add_handler(CallbackQueryHandler(ask_player_id, pattern="buy_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_player_id))
app.add_handler(CallbackQueryHandler(approve_order, pattern="approve_"))
app.add_handler(CallbackQueryHandler(reject_order, pattern="reject_"))
app.add_handler(CallbackQueryHandler(support, pattern="support"))

app.run_polling()