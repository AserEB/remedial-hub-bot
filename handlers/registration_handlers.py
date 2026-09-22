from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from config.settings import settings
from config.constants import (
    STATUS_VERIFIED,
    STATUS_PENDING,
    STREAM_NATURAL,
    STREAM_SOCIAL,
    BANK_CBE,
    BANK_ABYSSINIA
)
from database.repositories.student_repo import student_repo
from database.repositories.config_repo import config_repo
from keyboards.user_keyboards import (
    get_stream_selection_keyboard,
    get_bank_selection_keyboard,
    get_payment_details_keyboard,
    get_main_menu_keyboard
)
from keyboards.admin_keyboards import get_admin_verification_keyboard

# Conversation States
WAITING_NAME, SELECTING_STREAM, SELECTING_BANK, AWAITING_RECEIPT = range(4)


async def start_registration_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የምዝገባ መጀመሪያ ፍሰት"""
    query = update.callback_query
    user = update.effective_user
    chat_id = update.effective_chat.id

    if query:
        await query.answer()

    # 1. ምዝገባ ክፍት መሆኑን ማረጋገጥ
    sys_settings = config_repo.get_settings()
    if not sys_settings.get("is_registration_active", True):
        msg = "⚠️ <b>ይቅርታ፣ የወቅቱ ምዝገባ ለጊዜው ተዘግቷል!</b>\n\nእባክዎ ቻናላችንን በመከታተል ምዝገባ ሲከፈት ይጠብቁ።"
        if query:
            await query.edit_message_text(msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END

    # 2. የተማሪውን የወቅቱን ሁኔታ መፈተሽ
    student = student_repo.get_student(user.id)
    if student:
        current_status = student.get("status")
        if current_status == STATUS_VERIFIED:
            msg = "✅ <b>እርስዎ ቀደም ሲል በተሳካ ሁኔታ ተመዝግበዋል!</b>\n\nየመማሪያ ሊንክዎን ለማየት <b>My Status</b> የሚለውን ይጫኑ።"
            if query:
                await query.edit_message_text(msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
            return ConversationHandler.END

        if current_status == STATUS_PENDING:
            msg = (
                "⏳ <b>የእርስዎ ምዝገባ በመገምገም ላይ ይገኛል!</b>\n\n"
                "የከፈሉት ክፍያ በአድሚኖች ታይቶ እስኪረጋገጥ ድረስ በትዕግስት ይጠብቁ። "
                "ሁኔታውን በ <b>My Status</b> መከታተል ይችላሉ።"
            )
            if query:
                await query.edit_message_text(msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
            return ConversationHandler.END

    # ስም መጠየቅ
    prompt_text = (
        "📝 <b>የተማሪዎች ምዝገባ (Registration)፦</b>\n\n"
        "እባክዎ ሙሉ ስምዎን (የአያት ስም ጨምረው) ጽፈው ይላኩ፦"
    )
    if query:
        await query.message.reply_text(prompt_text, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=chat_id, text=prompt_text, parse_mode="HTML")

    return WAITING_NAME


async def re_register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Discard የተደረገ ተማሪ ዳታው ተጠርጎ እንደ አዲስ የሚጀምርበት"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # የድሮውን Stream እና Screenshot Clear ማድረግ
    student_repo.reset_for_re_registration(user_id)

    await query.message.reply_text(
        "🔄 <b>እንደ አዲስ መመዝገብ፦</b>\n\nእባክዎ ሙሉ ስምዎን (የአያት ስም ጨምረው) ጽፈው ይላኩ፦",
        parse_mode="HTML"
    )
    return WAITING_NAME


async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ስም ሲገባ ተቀብሎ የ Stream መምረጫ ያቀርባል"""
    full_name = update.message.text.strip()
    if len(full_name.split()) < 2:
        await update.message.reply_text("❗️ እባክዎ ትክክለኛ ሙሉ ስምዎን (ቢያንስ ስሞትን እና የአባት ስም) ያስገቡ፦")
        return WAITING_NAME

    context.user_data["full_name"] = full_name

    text = (
        f"👤 <b>ተማሪ፦</b> {full_name}\n\n"
        "⚠️ <b>ትክክለኛውን የትምህርት ዘርፍዎን (Stream) ይምረጡ፦</b>\n\n"
        "❗️ <i>ማሳሰቢያ፡ የመረጡት Stream የመማሪያ ግሩፕዎን ስለሚወስን እንዳይሳሳቱ በጥንቃቄ ይምረጡ!</i>"
    )
    await update.message.reply_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_stream_selection_keyboard()
    )
    return SELECTING_STREAM


async def edit_name_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ስም ለማስተካከል ሲፈለግ"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("እባክዎ የተስተካከለ ሙሉ ስምዎን ያስገቡ፦")
    return WAITING_NAME


async def stream_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የትምህርት ዘርፍ (Stream) ሲመረጥ የባንክ አማራጭ ያቀርባል"""
    query = update.callback_query
    await query.answer()

    stream_choice = query.data.replace("stream_", "")
    context.user_data["stream"] = stream_choice

    stream_label = "Natural Science 🔬" if stream_choice == STREAM_NATURAL else "Social Science 📚"

    text = (
        f"👤 <b>ተማሪ፦</b> {context.user_data.get('full_name')}\n"
        f"📚 <b>የተመረጠው Stream፦</b> {stream_label}\n\n"
        "ክፍያ የሚፈጽሙበትን የባንክ አማራጭ ይምረጡ፦"
    )
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_bank_selection_keyboard()
    )
    return SELECTING_BANK


async def edit_stream_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stream ለመቀየር ሲፈለግ"""
    query = update.callback_query
    await query.answer()
    text = (
        f"👤 <b>ተማሪ፦</b> {context.user_data.get('full_name')}\n\n"
        "⚠️ <b>ትክክለኛውን የትምህርት ዘርፍዎን (Stream) ይምረጡ፦</b>"
    )
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_stream_selection_keyboard()
    )
    return SELECTING_STREAM


async def bank_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ባንክ ሲመረጥ የሂሳብ ቁጥሩን (Tap-to-copy) ያቀርባል"""
    query = update.callback_query
    await query.answer()

    bank_choice = query.data.replace("bank_", "")
    context.user_data["bank"] = bank_choice

    if bank_choice == BANK_CBE:
        acc_name = settings.CBE_ACCOUNT_NAME
        acc_num = settings.CBE_ACCOUNT_NUMBER
        bank_title = "የኢትዮጵያ ንግድ ባንክ (CBE)"
    else:
        acc_name = settings.ABYSSINIA_ACCOUNT_NAME
        acc_num = settings.ABYSSINIA_ACCOUNT_NUMBER
        bank_title = "አቢሲንያ ባንክ (Bank of Abyssinia)"

    fee = settings.REGISTRATION_FEE_ETB

    text = (
        f"🏦 <b>{bank_title} የክፍያ መረጃ፦</b>\n\n"
        f"💰 <b>የሚከፈል መጠን፦</b> <code>{fee}</code> ብር\n"
        "❗️ <i>ይህ ክፍያ ለ 1 ሳምንት ብቻ የሚቆይ ልዩ ቅናሽ ነው፤ ከዛ በኋላ ዋጋ ይጨምራል!</i>\n"
        f"⚠️ <i>ከ {fee} ብር በታችም ሆነ በላይ መክፈል ተቀባይነት የለውም!</i>\n\n"
        f"👤 <b>የሂሳብ ስም፦</b> <code>{acc_name}</code>\n"
        f"💳 <b>የሂሳብ ቁጥር (ይጫኑት ኮፒ ይሆናል)፦</b>\n"
        f"<code>{acc_num}</code>\n\n"
        "──────────────────────────────\n"
        "ክፍያ ከፈጸሙ በኋላ ከታች ያለውን <b>Send Payment Screenshot</b> የሚለውን በመጫን "
        "የከፈሉበትን ደረሰኝ (ፎቶ ወይም ዶክመንት) ይላኩ።"
    )

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_payment_details_keyboard()
    )
    return AWAITING_RECEIPT


async def prompt_receipt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ደረሰኝ እንዲልኩ መጠየቂያ"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📸 <b>እባክዎ የከፈሉበትን የባንክ ማረጋገጫ ደረሰኝ (Screenshot ወይም PDF) አሁን ይላኩ፦</b>",
        parse_mode="HTML"
    )
    return AWAITING_RECEIPT


async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ደረሰኝ ተቀብሎ ዳታቤዝ ላይ ማስቀመጥ እና ለአድሚኖች መላክ"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ፋይል መለያየት (Photo ወይስ Document)
    file_id = None
    is_doc = False

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document:
        file_id = update.message.document.file_id
        is_doc = True
    else:
        await update.message.reply_text("❗️ እባክዎ ትክክለኛ የደረሰኝ ፎቶ (Image) ወይም PDF ዶክመንት ይላኩ።")
        return AWAITING_RECEIPT

    full_name = context.user_data.get("full_name", user.full_name)
    stream = context.user_data.get("stream", STREAM_NATURAL)
    bank = context.user_data.get("bank", BANK_CBE)

    # 1. ዳታቤዝ ላይ PENDING አድርጎ ማስቀመጥ
    student_repo.submit_for_verification(
        telegram_id=user.id,
        full_name=full_name,
        stream=stream,
        payment_method=bank,
        file_id=file_id
    )

    # 2. ለተማሪው ማረጋገጫ መላክ
    user_confirm_text = (
        "⏳ <b>የምዝገባ ጥያቄዎ በመገምገም ላይ ይገኛል (On Review/Pending)</b>\n\n"
        f"👤 <b>ስም፦</b> {full_name}\n"
        f"📚 <b>Stream፦</b> {stream}\n"
        f"🏦 <b>ባንክ፦</b> {bank}\n\n"
        "የከፈሉት ክፍያ በአድሚኖች ታይቶ እስኪረጋገጥ ድረስ ከ <b>2 እስከ 3 ትዓት</b> በትዕግስት ይጠብቁ።\n"
        "ልክ እንደተረጋገጠ የመማሪያ ሊንክዎን በዚህ ቦት የምንልክልዎ ይሆናል።\n\n"
        "✨ <i>Remedial Hub — መልካም ቆይታ!</i>"
    )
    await update.message.reply_text(user_confirm_text, parse_mode="HTML")

    # 3. ለ 4ቱም አድሚኖች ደረሰኙን ከነማረጋገጫ አዝራሮች መላክ
    admin_caption = (
        "🔔 <b>አዲስ የክፍያ ማረጋገጫ ጥያቄ!</b>\n\n"
        f"👤 <b>ስም፦</b> {full_name}\n"
        f"🆔 <b>Telegram ID፦</b> <code>{user.id}</code>\n"
        f"🏷 <b>Username፦</b> @{user.username or 'ያልተገኘ'}\n"
        f"📚 <b>Stream፦</b> <b>{stream}</b>\n"
        f"🏦 <b>Bank፦</b> {bank}\n"
    )
    admin_markup = get_admin_verification_keyboard(user.id)

    for admin_id in settings.admin_ids:
        try:
            if is_doc:
                await context.bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=admin_caption,
                    parse_mode="HTML",
                    reply_markup=admin_markup
                )
            else:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=admin_caption,
                    parse_mode="HTML",
                    reply_markup=admin_markup
                )
        except Exception:
            pass

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ምዝገባ ሲቋረጥ"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.message.reply_text("❌ ምዝገባው ተቋርጧል። ወደ ዋናው ሜኑ ለመመለስ /start ይበሉ።")
    else:
        await update.message.reply_text("❌ ምዝገባው ተቋርጧል። ወደ ዋናው ሜኑ ለመመለስ /start ይበሉ።")

    context.user_data.clear()
    return ConversationHandler.END


def get_registration_conversation_handler() -> ConversationHandler:
    """የምዝገባ ConversationHandler ማሰሪያ"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_registration_entry, pattern="^start_registration$"),
            CallbackQueryHandler(re_register_callback, pattern="^re_register_start$"),
            CommandHandler("register", start_registration_entry)
        ],
        states={
            WAITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, name_received),
                CallbackQueryHandler(cancel_registration, pattern="^reg_cancel$")
            ],
            SELECTING_STREAM: [
                CallbackQueryHandler(stream_selected, pattern="^stream_"),
                CallbackQueryHandler(edit_name_callback, pattern="^reg_edit_name$"),
                CallbackQueryHandler(cancel_registration, pattern="^reg_cancel$")
            ],
            SELECTING_BANK: [
                CallbackQueryHandler(bank_selected, pattern="^bank_"),
                CallbackQueryHandler(edit_stream_callback, pattern="^reg_edit_stream$"),
                CallbackQueryHandler(cancel_registration, pattern="^reg_cancel$")
            ],
            AWAITING_RECEIPT: [
                CallbackQueryHandler(prompt_receipt_callback, pattern="^prompt_receipt$"),
                CallbackQueryHandler(edit_stream_callback, pattern="^reg_edit_bank$"),
                CallbackQueryHandler(cancel_registration, pattern="^reg_cancel$"),
                MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_received)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel_registration),
            CallbackQueryHandler(cancel_registration, pattern="^reg_cancel$")
        ],
        allow_reentry=True
    )