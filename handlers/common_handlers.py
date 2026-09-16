from telegram import Update
from telegram.ext import ContextTypes
from database.repositories.student_repo import student_repo
from database.repositories.config_repo import config_repo
from services.channel_service import check_user_channel_subscription
from keyboards.user_keyboards import get_force_sub_keyboard, get_main_menu_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የ /start ትዕዛዝ እና የተጠቃሚ ምዝገባ መጀመሪያ"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ተማሪውን ዳታቤዝ ላይ መመዝገብ ወይም መፈተሽ
    student_repo.get_or_create_student(
        telegram_id=user.id,
        username=user.username
    )

    # ቻናሉን መቀላቀሉን ማረጋገጥ
    is_subscribed = await check_user_channel_subscription(context.bot, user.id)

    if not is_subscribed:
        text = (
            f"ሰላም <b>{user.first_name}</b>! 👋\n\n"
            "ወደ <b>Remedial Hub</b> የትምህርት ማዕከል ቦት በደህና መጡ! 🎓\n\n"
            "ወደ ምዝገባ እና ሌሎች መረጃዎች ከማለፍዎ በፊት እባክዎ ይፋዊ የቴሌግራም ቻናላችንን ይቀላቀሉ።\n"
            "📢 <b>Official Channel:</b> @Remedial_Hub"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=get_force_sub_keyboard()
        )
        return

    await show_main_menu(update, context)


async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የ 'ተቀላቅያለሁ / Verify' አዝራር ሲነካ የሚሰራ"""
    query = update.callback_query
    user_id = query.from_user.id

    is_subscribed = await check_user_channel_subscription(context.bot, user_id)
    if is_subscribed:
        await query.answer("✅ ቻናሉን መቀላቀልዎ ተረጋግጧል!")
        await query.message.delete()
        await show_main_menu(update, context)
    else:
        # ለተጠቃሚው Alert እና በግልጽ የሚነበብ መልዕክት
        await query.answer("❗️ እባክዎ መጀመሪያ ቻናላችንን ይቀላቀሉ!", show_alert=True)
        warning_text = (
            "⚠️ <b>አልተቀላቀሉም!</b>\n\n"
            "እባክዎ መጀመሪያ ከታች ያለውን <b>📢 Join Channel</b> የሚለውን ተጭነው ቻናሉን ይቀላቀሉ። "
            "ከተቀላቀሉ በኋላ በድጋሚ <b>✅ ተቀላቅያለሁ / Verify</b> የሚለውን ይጫኑ።"
        )
        try:
            await query.message.reply_text(warning_text, parse_mode="HTML")
        except Exception:
            pass


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ዋናውን ሜኑ ከ Pinned Notice ጋር ማሳያ"""
    chat_id = update.effective_chat.id
    settings = config_repo.get_settings()
    
    notice_banner = ""
    if settings.get("pinned_notice_active") and settings.get("pinned_notice_text"):
        notice_banner = (
            f"📌 <b>ማስታወቂያ፦</b>\n"
            f"<i>{settings['pinned_notice_text']}</i>\n"
            f"──────────────────────────────\n\n"
        )

    text = (
        f"{notice_banner}"
        "<b>እንኳን ወደ Remedial Hub በደህና መጡ!</b> 🎓\n\n"
        "ከታች ያሉትን አማራጮች በመጠቀም ስለ ማዕከላችን ማወቅ፣ ተደጋጋሚ ጥያቄዎችን ማንበብ "
        "ወይም አሁኑኑ መመዝገብ ይችላሉ።"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የ /cancel ትዕዛዝ"""
    await update.effective_message.reply_text(
        "❌ ሂደቱ ተሰርዟል። ወደ ዋናው ሜኑ ለመመለስ /start ይበሉ።"
    )