import os
import csv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CSV_FILE = "universities.csv"


def normalize(text):
    return str(text).lower().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")


def load_universities():
    with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def search_answer(user_text):
    user_text = normalize(user_text)

    correction_words = ["غلط", "خطا", "خطأ", "مو صحيح", "معلوماتك غلط", "غير صحيح"]
    if any(word in user_text for word in correction_words):
        return (
            "أعتذر إذا كانت المعلومة غير دقيقة تماماً.\n"
            "قد تختلف الرسوم حسب آخر تحديثات الجامعة أو الجنسية أو السنة الدراسية.\n\n"
            "للتأكيد الدقيق، تواصل ويانا بمكتب الأمل 📞"
        )

    rows = load_universities()
    results = []

    for row in rows:
        combined = normalize(
            f"{row.get('country','')} {row.get('university','')} {row.get('major','')}"
        )

        score = 0
        for word in user_text.split():
            if len(word) > 2 and word in combined:
                score += 1

        if score > 0:
            results.append((score, row))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        return (
            "ما لقيت معلومة دقيقة حالياً عن هذا السؤال.\n"
            "اكتب اسم الجامعة أو القسم حتى أبحث لك أسرع.\n\n"
            "📞 للتأكيد تواصل ويانا بمكتب الأمل."
        )

    row = results[0][1]

    university = row.get("university", "الجامعة")
    country = row.get("country", "الدولة")
    major = row.get("major", "التخصص")
    available = row.get("available", "نعم")
    fee = row.get("fee", "غير محدد")
    currency = row.get("currency", "")
    notes = row.get("notes", "")

    if normalize(available) in ["لا", "no", "غير متوفر"]:
        return (
            f"حالياً تخصص {major} غير متوفر في {university} - {country}.\n\n"
            f"📌 {notes}\n"
            "📞 للتأكد من البدائل المتاحة تواصل ويانا بمكتب الأمل."
        )

    return (
        f"نعم، تخصص {major} متوفر في {university} - {country}.\n"
        f"القسط تقريباً {fee} {currency} سنوياً.\n\n"
        f"📌 {notes}\n"
        "قد تختلف التفاصيل حسب السنة الدراسية والتحديثات.\n\n"
        "📞 للتأكيد تواصل ويانا بمكتب الأمل."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في مكتب الأمل للدراسة خارج العراق 🎓\n"
        "اكتب اسم الجامعة أو القسم حتى أبحث لك بسرعة."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(search_answer(update.message.text))


def main():
    if not TELEGRAM_TOKEN:
        print("حط TELEGRAM_BOT_TOKEN داخل ملف .env")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()