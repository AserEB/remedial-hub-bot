import os
from telegram import Update
from telegram.ext import ContextTypes
from config.constants import (
    ABOUT_US_TEXT,
    TESTIMONIAL_TEXT,
    FAQ_HEADER_TEXT,
    FAQ_QUESTIONS,
    HOW_TO_REGISTER_CAPTION
)
from keyboards.user_keyboards import (
    get_about_keyboard,
    get_testimonial_keyboard,
    get_faq_list_keyboard,
    get_faq_detail_keyboard,
    get_how_to_register_keyboard,
    get_main_menu_keyboard
)


async def nav_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=ABOUT_US_TEXT,
        parse_mode="HTML",
        reply_markup=get_about_keyboard()
    )


async def nav_testimonial_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=TESTIMONIAL_TEXT,
        parse_mode="HTML",
        reply_markup=get_testimonial_keyboard()
    )


async def nav_faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=FAQ_HEADER_TEXT,
        parse_mode="HTML",
        reply_markup=get_faq_list_keyboard()
    )


async def faq_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    answer_text = FAQ_QUESTIONS.get(action, "መረጃው አልተገኘም።")
    await query.edit_message_text(
        text=answer_text,
        parse_mode="HTML",
        reply_markup=get_faq_detail_keyboard()
    )


async def nav_how_to_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id

    video_path = os.path.join("assets", "media", "How-to-register.mp4")

    if os.path.exists(video_path):
        await query.message.delete()
        with open(video_path, "rb") as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=HOW_TO_REGISTER_CAPTION,
                parse_mode="HTML",
                reply_markup=get_how_to_register_keyboard()
            )
    else:
        # ቪዲዮው ገና ካልተቀመጠ ጽሑፉን ብቻ ይልካል
        await query.edit_message_text(
            text=HOW_TO_REGISTER_CAPTION,
            parse_mode="HTML",
            reply_markup=get_how_to_register_keyboard()
        )


async def back_to_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    main_menu_text = (
        "<b>እንኳን ወደ Remedial Hub በደህና መጡ!</b> 🎓\n\n"
        "ከታች ያሉትን አማራጮች በመጠቀም ስለ ማዕከላችን ማወቅ፣ ተደጋጋሚ ጥያቄዎችን ማንበብ "
        "ወይም አሁኑኑ መመዝገብ ይችላሉ።"
    )
    
    try:
        # መልዕክቱ ቪዲዮ፣ ፎቶ ወይም ዶክመንት ከሆነ አጥፍተን አዲስ እንልካለን
        if query.message.video or query.message.photo or query.message.document:
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=main_menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # መልዕክቱ ጽሑፍ ብቻ ከሆነ በተለመደው መንገድ Edit እናደርጋለን
            await query.edit_message_text(
                text=main_menu_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
    except Exception as e:
        print(f"Error returning to main menu: {e}")
        # በምንም ምክንያት Edit ማድረግ ካልቻለ አዲስ ይልካል
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=main_menu_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )