
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

BOT_TOKEN = 'PUT_YOUR_BOT_TOKEN_HERE'
ADMIN_USERNAME = '@Adamcharge'

CHOOSING_SERVICE, GET_NAME, GET_ID, GET_AMOUNT, GET_PAYMENT_METHOD, GET_RECEIPT = range(6)

services = [
    ["شحن شدات ببجي", "بطاقات Google Play"],
    ["شحن لايفات", "شراء / بيع USDT"]
]

payment_methods = ["هرم", "فؤاد", "سيرياتل كاش", "USDT (TRC20)"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(services, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("مرحباً بك في متجر آدم. يرجى اختيار الخدمة:", reply_markup=reply_markup)
    return CHOOSING_SERVICE

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['service'] = update.message.text
    await update.message.reply_text("يرجى إدخال اسمك الكامل:", reply_markup=ReplyKeyboardRemove())
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("يرجى إدخال رقم الحساب أو ID:")
    return GET_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id'] = update.message.text
    await update.message.reply_text("يرجى إدخال الكمية المطلوبة:")
    return GET_AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    reply_markup = ReplyKeyboardMarkup([payment_methods], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("يرجى اختيار وسيلة الدفع:", reply_markup=reply_markup)
    return GET_PAYMENT_METHOD

async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment_method'] = update.message.text
    await update.message.reply_text("يرجى إرسال صورة إيصال الدفع أو اكتب 'تخطي':")
    return GET_RECEIPT

async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    receipt = update.message.photo[-1].file_id if update.message.photo else "لم يتم إرسال إيصال"
    context.user_data['receipt'] = receipt

    user_data = context.user_data
    message = (
        f"طلب جديد:
"
        f"الخدمة: {user_data['service']}
"
        f"الاسم: {user_data['name']}
"
        f"ID الحساب: {user_data['id']}
"
        f"الكمية: {user_data['amount']}
"
        f"وسيلة الدفع: {user_data['payment_method']}
"
        f"إيصال الدفع: {'مرفق' if receipt != 'لم يتم إرسال إيصال' else 'غير موجود'}"
    )

    await context.bot.send_message(chat_id=ADMIN_USERNAME, text=message)
    if receipt != "لم يتم إرسال إيصال":
        await context.bot.send_photo(chat_id=ADMIN_USERNAME, photo=receipt)

    await update.message.reply_text("تم إرسال طلبك بنجاح. سنتواصل معك قريباً.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية. يمكنك البدء من جديد بإرسال /start.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
            GET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            GET_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_method)],
            GET_RECEIPT: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, get_receipt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
