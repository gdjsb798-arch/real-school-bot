from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

from datetime import datetime

ADMIN_ID = 7684146645

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
        "age": "🎂 Jasiniz neshede?",
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


# телефон
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    digits = update.message.text
    lang = context.user_data["lang"]

    if not digits.isdigit() or len(digits) != 9:
        await update.message.reply_text(TEXTS[lang]["phone_error"])
        return PHONE

    context.user_data["phone"] = "+998" + digits
    u = context.user_data

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    message = (
        "📥 VOLUNTEER APPLICATION 🌿\n\n"
        f"🕒 Time: {time}\n\n"
        f"👤 Name: {u['name']}\n"
        f"🎂 Age: {u['age']}\n"
        f"🌱 Reason: {u['activity']}\n"
        f"❓ Question: {u['question']}\n"
        f"📱 Phone: {u['phone']}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=message
    )

    await update.message.reply_text(TEXTS[lang]["done"])

    return ConversationHandler.END


# cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token("7701518123:AAHkVm8Y6Pw83P0CTLP8Nkzu7qtXORl9wek").build()

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

    print("Бот запущен 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
