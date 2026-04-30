import os
import csv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# قراءة ملف الجامعات
def load_data():
    data = []
    with open("universities.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

universities = load_data()

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في مكتب الأمل للدراسة خارج العراق 🎓\n"
        "اكتب اسم الجامعة أو التخصص حتى أبحث لك بسرعة."
    )

# الرد على الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()

    results = []

    for uni in universities:
        if user_msg in uni["university"] or user_msg in uni["major"]:
            results.append(uni)

    if results:
        reply = "📚 المعلومات المتوفرة:\n\n"

        for r in results:
            reply += f"""🏫 الجامعة: {r['university']}
🌍 الدولة: {r['country']}
🎓 التخصص: {r['major']}
💰 القسط: {r['annual_fee']} {r['currency']}
📝 ملاحظة: {r['notes']}

"""

        reply += "📞 للتأكيد والتقديم تواصل ويانا بمكتب الأمل."

    else:
        reply = (
            "❌ ما لقيت معلومات دقيقة حالياً عن هذا السؤال.\n"
            "اكتب اسم الجامعة أو التخصص حتى أبحث لك بشكل أدق.\n\n"
            "📞 للتأكيد والتقديم تواصل ويانا بمكتب الأمل."
        )

    await update.message.reply_text(reply)

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()