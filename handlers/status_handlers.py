from telegram import Update
from telegram.ext import ContextTypes
from database.repositories.student_repo import student_repo
from keyboards.user_keyboards import get_status_keyboard, get_discard_keyboard, get_verified_keyboard
from config.constants import STATUS_VERIFIED, STATUS_DISCARDED, STATUS_PENDING


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    query = update.callback_query

    if query:
        await query.answer()

    student = student_repo.get_student(user_id)

    if not student:
        msg = "እስካሁን ምንም አይነት የምዝገባ መረጃ አልተገኘም። እባክዎ በ /start ይመዝገቡ።"
        if query:
            await query.edit_message_text(msg)
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    status = student.get("status")
    full_name = student.get("full_name") or "ያልተሞላ"
    stream = student.get("stream") or "ያልተመረጠ"
    discards = student.get("discard_count", 0)

    status_icon = {
        STATUS_VERIFIED: "✅ የተረጋገጠ (Verified)",
        STATUS_PENDING: "⏳ በመጠባበቅ ላይ (Under Review)",
        STATUS_DISCARDED: "❌ ውድቅ የተደረገ (Discarded)"
    }.get(status, "📝 ምዝገባ አልተጠናቀቀም (Started)")

    text = (
        "📊 <b>የእርስዎ የምዝገባ ሁኔታ (My Status)፦</b>\n\n"
        f"👤 <b>ሙሉ ስም፦</b> {full_name}\n"
        f"📚 <b>Stream፦</b> {stream}\n"
        f"📌 <b>የወቅቱ ሁኔታ፦</b> {status_icon}\n"
        f"⚠️ <b>Discard የተደረገበት ቁጥር፦</b> {discards} ጊዜ\n"
    )

    reply_markup = get_status_keyboard()

    if status == STATUS_VERIFIED and student.get("single_use_invite_link"):
        text += f"\n🔗 <b>የመማሪያ ሊንክዎ፦</b>\n{student['single_use_invite_link']}"
        reply_markup = get_verified_keyboard()
    elif status == STATUS_DISCARDED:
        reason = student.get("discard_reason") or "ያልተገለጸ"
        text += f"\n📋 <b>ውድቅ የተደረገበት ምክንያት፦</b>\n<i>{reason}</i>\n"
        reply_markup = get_discard_keyboard()

    if query:
        await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=reply_markup)