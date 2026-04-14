from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler
)

from datetime import datetime
import os

# 🔐 лучше хранить токен так
TOKEN = os.getenv("7701518123:AAFohQGHS_ZcYDkdDqEbmGV_HEBS3fMRbNI")

# 👥 админы с именами
ADMIN_IDS = {
    2040362478: "Fatima",
    5563072937: "Zuxra",
    7684146645: "Sevara"
}

# 🧠 память заявок
taken_requests = {}

LANG, NAME, AGE, ACTIVITY, QUESTION, PHONE = range(6)

# 🌍 клавиатура языка
lang_kb = ReplyKeyboardMarkup(
    [
        ["🇷🇺 Русский", "🇬🇧 English"],
        ["🇺🇿 Қарақалпақша"]
    ],
    resize_keyboard=True
)

# 🌐 тексты
TEXTS = {
    "🇷🇺 Русский": {
        "welcome": "👋 Добро пожаловать в Real School Eco Community!",
        "name": "👤 Как вас зовут?",
        "age": "🎂 Сколько вам лет?",
        "activity": "🌱 Почему решили заниматься волонтёрством?",
        "question": "❓ Есть ли вопросы к админу?",
        "phone": "📱 Введите номер (+998XXXXXXXXX)\n🔢 Только 9 цифр после +998:",
        "phone_error": "❌ Неверный номер!\n🔢 Введите только 9 цифр после +998\n\nПример: 901234567",
        "done": "✅ Спасибо! Ваша заявка отправлена.\n📩 Скоро с вами свяжутся."
    },

    "🇬🇧 English": {
        "welcome": "👋 Welcome to Real School Eco Community!",
        "name": "👤 What is your name?",
        "age": "🎂 How old are you?",
        "activity": "🌱 Why did you decide to do volunteering?",
        "question": "❓ Any questions for admin?",
        "phone": "📱 Enter number (+998XXXXXXXXX)\n🔢 Only 9 digits after +998:",
        "phone_error": "❌ Invalid number!\n🔢 Enter only 9 digits after +998\n\nExample: 901234567",
        "done": "✅ Thank you! Your application has been sent.\n📩 Admin will contact you soon."
    },

    "🇺🇿 Қарақалпақша": {
        "welcome": "👋 Real School Eco Communityge xosh kelipsiz!",
        "name": "👤 Atińız kim?",
        "age": "🎂 Jasińız neshede?",
        "activity": "🌱 Ne ushin volontyor boliwdi tanladiniz?",
        "question": "❓ Adminge soraw bar ma?",
        "phone": "📱 Telefon (+998XXXXXXXXX)\n🔢 +998 den keyin 9 san jazıń:",
        "phone_error": "❌ Qate nomer!\n🔢 +998 den keyin 9 san jazıń\n\nMısal: 901234567",
        "done": "✅ Rahmet! zayavka jiberildi. Admin tez arada baylanısadı."
    }
}


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🌍 Выберите язык / Choose language / Til tanlań:",
        reply_markup=lang_kb
    )
    return LANG


# выбор языка
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    context.user_data["lang"] = lang

    await update.message.reply_text(
        TEXTS[lang]["welcome"],
        reply_markup=ReplyKeyboardRemove()
    )

    await update.message.reply_text(TEXTS[lang]["name"])
    return NAME


# имя
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    lang = context.user_data["lang"]

    await update.message.reply_text(TEXTS[lang]["age"])
    return AGE


# возраст
async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    lang = context.user_data["lang"]

    await update.message.reply_text(TEXTS[lang]["activity"])
    return ACTIVITY


# причина
async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["activity"] = update.message.text
    lang = context.user_data["lang"]

    await update.message.reply_text(TEXTS[lang]["question"])
    return QUESTION


# вопрос
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question"] = update.message.text
    lang = context.user_data["lang"]

    await update.message.reply_text(TEXTS[lang]["phone"])
    return PHONE


# телефон + отправка админам
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    digits = update.message.text
    lang = context.user_data["lang"]

    if not digits.isdigit() or len(digits) != 9:
        await update.message.reply_text(TEXTS[lang]["phone_error"])
        return PHONE

    context.user_data["phone"] = "+998" + digits
    u = context.user_data

    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_id = update.message.from_user.id

    message = (
        "📥 VOLUNTEER APPLICATION 🌿\n\n"
        f"🕒 Time: {time}\n\n"
        f"👤 Name: {u['name']}\n"
        f"🎂 Age: {u['age']}\n"
        f"🌱 Reason: {u['activity']}\n"
        f"❓ Question: {u['question']}\n"
        f"📱 Phone: {u['phone']}\n\n"
        f"🆔 User ID: {user_id}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Принял", callback_data=f"take_{user_id}")]
    ])

    taken_requests[str(user_id)] = []

    for admin in ADMIN_IDS.keys():
        await context.bot.send_message(
            chat_id=admin,
            text=message,
            reply_markup=keyboard
        )

    await update.message.reply_text(TEXTS[lang]["done"])

    return ConversationHandler.END


# обработка кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    admin_id = query.from_user.id

    if data.startswith("take_"):
        user_id = data.split("_")[1]

        if user_id not in taken_requests:
            taken_requests[user_id] = []

        if admin_id in taken_requests[user_id]:
            await query.answer("Ты уже принял эту заявку")
            return

        taken_requests[user_id].append(admin_id)

        names = []
        for a_id in taken_requests[user_id]:
            name = ADMIN_IDS.get(a_id, f"Admin {a_id}")
            names.append(f"- {name}")

        admins_text = "\n".join(names)

        base_text = query.message.text.split("✅ Приняли:")[0]

        new_text = base_text + f"\n\n✅ Приняли:\n{admins_text}"

        await query.edit_message_text(text=new_text)


# cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT, choose_lang)],
            NAME: [MessageHandler(filters.TEXT, name)],
            AGE: [MessageHandler(filters.TEXT, age)],
            ACTIVITY: [MessageHandler(filters.TEXT, activity)],
            QUESTION: [MessageHandler(filters.TEXT, question)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
