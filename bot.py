import os
import csv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CSV_FILE = "universities.csv"


def load_data():
    data = []
    try:
        with open(CSV_FILE, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print("CSV ERROR:", e)
    return data


universities = load_data()


def clean(text):
    return str(text or "").strip().lower()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في مكتب الأمل للدراسة خارج العراق 🎓\n"
        "اكتب اسم الجامعة أو التخصص أو المستوى الدراسي، وأنا أبحث لك بالمعلومات المتوفرة."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = clean(update.message.text)
    words = user_msg.split()

    results = []

    for r in universities:
        searchable = " ".join([
            clean(r.get("country")),
            clean(r.get("university")),
            clean(r.get("major")),
            clean(r.get("level")),
            clean(r.get("annual_fee")),
            clean(r.get("currency")),
            clean(r.get("notes")),
        ])

        score = 0
        for word in words:
            if word in searchable:
                score += 1

        if score >= 1:
            results.append((score, r))

    results.sort(key=lambda x: x[0], reverse=True)
    results = [r for score, r in results]

    if results:
        reply = "📚 المعلومات المتوفرة:\n\n"

        for r in results[:10]:
            reply += (
                f"🏫 الجامعة: {r.get('university', '')}\n"
                f"🌍 الدولة: {r.get('country', '')}\n"
                f"🎓 التخصص: {r.get('major', '')}\n"
                f"📘 المستوى: {r.get('level', '')}\n"
                f"💰 القسط السنوي: {r.get('annual_fee', '')} {r.get('currency', '')}\n"
                f"📝 ملاحظة: {r.get('notes', '')}\n\n"
            )

        if len(results) > 10:
            reply += f"تم عرض أول 10 نتائج من أصل {len(results)} نتيجة.\n\n"

        reply += "📞 للتأكيد والتقديم تواصل ويانا بمكتب الأمل."
    else:
        reply = (
            "أعتذر، ما لقيت معلومة دقيقة حالياً عن هذا السؤال.\n"
            "اكتب اسم الجامعة أو التخصص أو المستوى الدراسي بشكل أوضح حتى أبحث لك أسرع.\n\n"
            "📞 للتأكيد والتقديم تواصل ويانا بمكتب الأمل."
        )

    await update.message.reply_text(reply)


def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is missing")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()