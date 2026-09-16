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
from config.constants import STATUS_VERIFIED, STATUS_DISCARDED
from database.repositories.admin_repo import admin_repo
from database.repositories.student_repo import student_repo
from database.repositories.config_repo import config_repo
from keyboards.admin_keyboards import (
    get_admin_dashboard_keyboard,
    get_broadcast_confirm_keyboard,
    get_pin_confirm_keyboard
)
from keyboards.user_keyboards import get_discard_keyboard, get_verified_keyboard
from services.invite_service import generate_single_use_invite_link
from services.export_service import export_students_to_csv
from services.broadcast_service import broadcast_message_to_all

# States for Admin Operations
AWAITING_DISCARD_REASON = 101
AWAITING_BROADCAST_MSG = 102
AWAITING_PIN_TEXT = 103


def is_admin(user_id: int) -> bool:
    """ተጠቃሚው አድሚን መሆኑን ያረጋግጣል"""
    return user_id in settings.admin_ids


async def admin_dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/admin ትዕዛዝ ሲገባ ዳሽቦርዱን ያሳያል"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.effective_message.reply_text("⛔️ ይቅርታ፣ ይህ ትዕዛዝ ለአድሚኖች ብቻ የተፈቀደ ነው!")
        return

    sys_settings = config_repo.get_settings()
    is_active = sys_settings.get("is_registration_active", True)
    pin_text = sys_settings.get("pinned_notice_text") or "የለም"

    text = (
        "🛠 <b>Remedial Hub — የአድሚን መቆጣጠሪያ Dashboard</b>\n\n"
        f"📊 <b>የምዝገባ ሁኔታ፦</b> {'🟢 ክፍት (ACTIVE)' if is_active else '🔴 ዝግ (CLOSED)'}\n"
        f"📌 <b>የተለጠፈ ማስታወቂያ፦</b> <i>{pin_text}</i>\n\n"
        "ከታች ያሉትን Button በመጠቀም ሲስተሙን መቆጣጠር ይችላሉ፦"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode="HTML",
            reply_markup=get_admin_dashboard_keyboard(is_active)
        )
    else:
        await update.effective_message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=get_admin_dashboard_keyboard(is_active)
        )


async def toggle_registration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የምዝገባውን ክፍት/ዝግ መቀያየሪያ"""
    query = update.callback_query
    admin_id = query.from_user.id
    if not is_admin(admin_id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    new_state = config_repo.toggle_registration_status(admin_id)
    await query.answer(f"ምዝገባ አሁን {'ክፍት ሆኗል!' if new_state else 'ተዘግቷል!'}", show_alert=True)
    await admin_dashboard_command(update, context)


# ==========================================
# 1. VERIFY & DISCARD LOGIC (WITH CONCURRENCY LOCK)
# ==========================================

async def admin_verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ተማሪን የማረጋገጫ ሂደት"""
    query = update.callback_query
    admin = query.from_user
    if not is_admin(admin.id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    student_id = int(query.data.replace("adm_verify_", ""))
    admin_display_name = admin.first_name

    # Concurrency Lock ማረጋገጥ
    acquired, msg = admin_repo.acquire_processing_lock(
        student_id=student_id,
        admin_id=admin.id,
        admin_name=admin_display_name
    )

    if not acquired:
        await query.answer(msg, show_alert=True)
        return

    await query.answer("ተማሪው በመረጋገጥ ላይ ነው...")

    student = student_repo.get_student(student_id)
    if not student:
        await query.answer("የተማሪው ዳታ አልተገኘም!", show_alert=True)
        return

    stream = student.get("stream", "NATURAL")

    # 1 ሰው ብቻ የሚያስገባ ሊንክ ማመንጨት
    invite_link = await generate_single_use_invite_link(context.bot, stream, student_id)

    # ዳታቤዝ ላይ VERIFIED ማድረግ
    admin_repo.verify_student(
        student_id=student_id,
        admin_id=admin.id,
        admin_name=admin_display_name,
        invite_link=invite_link
    )

    # ለአድሚኑ ማረጋገጫ ማሳየት
    await query.edit_message_caption(
        caption=f"{query.message.caption}\n\n✅ <b>በአድሚን {admin_display_name} ጸድቋል (VERIFIED)!</b>",
        parse_mode="HTML"
    )

    # ለተማሪው ሊንኩን መላክ
    student_msg = (
        "🎉 <b>እንኳን ደስ አለዎት! ምዝገባዎ በተሳካ ሁኔታ ተረጋግጧል።</b>\n\n"
        f"🔗 <b>የመማሪያ ግሩፕ ሊንክዎ፦</b>\n{invite_link}\n\n"
        "❗️ <b>እጅግ ጠቃሚ ማሳሰቢያ፦</b>\n"
        "ይህ ሊንክ <b>ለአንድ ሰው ብቻ</b> የሚያገለግል ስለሆነ ለሌላ ሰው እንዳያጋሩ! "
        "ለሌላ ሰው ሰጥተው ሌላ ሰው ቢገባበት እርስዎ መግባት አይችሉም፤ ለዚህም ማዕከላችን ኃላፊነት አይወስድም!\n\n"
        "📌 <i>ሊንኩን ተጭነው ግሩፑን እንደተቀላቀሉ እንዳይጠፋብዎ Pin አድርገው ያስቀምጡት።</i>\n\n"
        "✨ <b>Remedial Hub — ከእኛ ጋር ይታለፋል!</b>"
    )
    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=student_msg,
            parse_mode="HTML",
            reply_markup=get_verified_keyboard()
        )
    except Exception:
        pass


async def admin_discard_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Discard አዝራር ሲነካ ምክንያት ለመጠየቅ Lock መያዝ"""
    query = update.callback_query
    admin = query.from_user
    if not is_admin(admin.id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    student_id = int(query.data.replace("adm_discard_", ""))
    admin_display_name = admin.first_name

    # Lock መያዝ
    acquired, msg = admin_repo.acquire_processing_lock(
        student_id=student_id,
        admin_id=admin.id,
        admin_name=admin_display_name
    )

    if not acquired:
        await query.answer(msg, show_alert=True)
        return

    context.user_data["discard_student_id"] = student_id
    context.user_data["discard_admin_name"] = admin_display_name
    context.user_data["discard_msg_id"] = query.message.message_id

    await query.answer()
    await query.message.reply_text(
        f"✍️ ተማሪ <code>{student_id}</code> ውድቅ የተደረገበትን ምክንያት ጽፈው ይላኩ፦"
    )
    return AWAITING_DISCARD_REASON


async def admin_discard_reason_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የተጻፈውን ምክንያት ተቀብሎ Discard ማጠናቀቅ"""
    reason = update.message.text.strip()
    student_id = context.user_data.get("discard_student_id")
    admin_name = context.user_data.get("discard_admin_name")
    admin_id = update.effective_user.id

    if not student_id:
        await update.message.reply_text("የተማሪ መረጃ ተቋርጧል። እንደገና ይሞክሩ።")
        return ConversationHandler.END

    # ዳታቤዝ ላይ DISCARDED ማድረግ
    admin_repo.discard_student(
        student_id=student_id,
        admin_id=admin_id,
        admin_name=admin_name,
        reason=reason
    )

    await update.message.reply_text(f"❌ ተማሪ <code>{student_id}</code> ውድቅ ተደርጓል። ለተማሪው መልዕክት ተልኳል።")

    # ለተማሪው ምክንያቱን መላክ
    student_msg = (
        "❌ <b>የምዝገባ ጥያቄዎ ውድቅ ተደርጓል!</b>\n\n"
        f"📋 <b>ምክንያት፦</b>\n<i>{reason}</i>\n\n"
        "──────────────────────────────\n"
        "መረጃዎን ወይም የከፈሉበትን ደረሰኝ አስተካክለው ከታች ያለውን <b>Re-Register</b> በመጫን እንደገና መመዝገብ ይችላሉ።"
    )
    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=student_msg,
            parse_mode="HTML",
            reply_markup=get_discard_keyboard()
        )
    except Exception:
        pass

    context.user_data.clear()
    return ConversationHandler.END


# ==========================================
# 2. CSV EXPORT LOGIC
# ==========================================

async def export_data_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የተለያዩ የተማሪዎች ዳታዎችን በ CSV ማውጫ"""
    query = update.callback_query
    admin_id = query.from_user.id
    if not is_admin(admin_id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    export_type = query.data.replace("export_", "")
    await query.answer("ዳታው እየተፈለገ ነው...")

    csv_file, total_count = await export_students_to_csv(status_filter=export_type)

    if total_count == 0 or csv_file is None:
        await query.message.reply_text(
            f"ℹ️ <b>ምንም የተገኘ ተማሪ የለም!</b>\n\nበአሁኑ ሰዓት በ <b>{export_type}</b> ሁኔታ ውስጥ ያለ ምንም የተመዘገበ ተማሪ አልተገኘም።",
            parse_mode="HTML"
        )
        return

    file_name = f"Students_{export_type}.csv"

    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=csv_file,
        filename=file_name,
        caption=f"📊 <b>የተማሪዎች ዳታ ({export_type})</b> ተዘጋጅቷል።\n👥 <b>አጠቃላይ የተማሪዎች ብዛት፦</b> {total_count}",
        parse_mode="HTML"
    )


# ==========================================
# 3. BROADCAST CONVERSATION
# ==========================================

async def broadcast_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast መልዕክት ለመቀበል መጠየቂያ"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    await query.answer()
    await query.message.reply_text(
        "📢 <b>አጠቃላይ መልዕክት (Broadcast)፦</b>\n\n"
        "ለተማሪዎች የሚተላለፈውን መልዕክት (ጽሑፍ፣ ፎቶ፣ ቪዲዮ ወይም ፋይል ከነ Caption) አሁን ይላኩ፦",
        parse_mode="HTML"
    )
    return AWAITING_BROADCAST_MSG


async def broadcast_msg_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """መልዕክቱን ይዞ ማረጋገጫ ማሳየት"""
    msg = update.message
    context.user_data["b_chat_id"] = msg.chat_id
    context.user_data["b_msg_id"] = msg.message_id

    await msg.reply_text(
        "⚠️ <b>ይህ መልዕክት ለሁሉም የሚላክ ነው፤ እርግጠኛ ነዎት?</b>",
        parse_mode="HTML",
        reply_markup=get_broadcast_confirm_keyboard()
    )
    return AWAITING_BROADCAST_MSG


async def broadcast_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Post Now ሲባል በ 0.05s Delay መላክ"""
    query = update.callback_query
    await query.answer()

    source_chat = context.user_data.get("b_chat_id")
    source_msg = context.user_data.get("b_msg_id")

    await query.edit_message_text("🚀 መልዕክቱ እየተላከ ነው፤ እባክዎ ትንሽ ይጠብቁ...")

    results = await broadcast_message_to_all(context.bot, source_chat, source_msg)

    await query.message.reply_text(
        f"✅ <b>Broadcast ተጠናቋል!</b>\n\n"
        f"📤 በተሳካ ሁኔታ የተላከ፦ <b>{results['sent']}</b>\n"
        f"❌ ያልተላከ (Failed/Blocked)፦ <b>{results['failed']}</b>",
        parse_mode="HTML"
    )
    context.user_data.clear()
    return ConversationHandler.END


async def broadcast_cancelled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Broadcast ተሰርዟል።")
    context.user_data.clear()
    return ConversationHandler.END


# ==========================================
# 4. PINNED NOTICE CONVERSATION (MAX 85 CHARS)
# ==========================================

async def pin_notice_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("ፍቃድ የለዎትም!", show_alert=True)
        return

    await query.answer()
    await query.message.reply_text(
        "📌 <b>ማስታወቂያ መለጠፊያ (Pinned Notice)፦</b>\n\n"
        "በዋናው ሜኑ ላይ Pin የሚሆነውን ጽሑፍ ይላኩ።\n"
        "⚠️ <i>ገደብ፡ ጽሑፉ ከ 85 ፊደላት መብለጥ የለበትም!</i>",
        parse_mode="HTML"
    )
    return AWAITING_PIN_TEXT


async def pin_text_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) > 85:
        await update.message.reply_text(
            f"❗️ ጽሑፉ {len(text)} ፊደላት ነው። ከ 85 ፊደላት መብለጥ የለበትም። እባክዎ አሳጥረው ይላኩ፦"
        )
        return AWAITING_PIN_TEXT

    context.user_data["pending_pin_text"] = text

    await update.message.reply_text(
        f"📌 <b>የተዘጋጀው ማስታወቂያ፦</b>\n\n<i>{text}</i>\n\nይህ ጽሑፍ Pin ይሁን?",
        parse_mode="HTML",
        reply_markup=get_pin_confirm_keyboard()
    )
    return AWAITING_PIN_TEXT


async def pin_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    admin_id = query.from_user.id
    notice_text = context.user_data.get("pending_pin_text")

    config_repo.update_pinned_notice(notice_text=notice_text, active=True, admin_id=admin_id)

    await query.edit_message_text(f"✅ ማስታወቂያው Pin ተደርጓል፦\n<i>{notice_text}</i>", parse_mode="HTML")
    context.user_data.clear()
    return ConversationHandler.END


async def pin_cancelled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ ማስታወቂያ Post ማድረግ ተሰርዟል።")
    context.user_data.clear()
    return ConversationHandler.END