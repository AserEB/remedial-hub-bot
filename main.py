import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from config.settings import settings
from handlers.common_handlers import start_command, check_sub_callback, cancel_command, show_main_menu
from handlers.navigation_handlers import (
    nav_about_callback,
    nav_testimonial_callback,
    nav_faq_callback,
    faq_answer_callback,
    nav_how_to_callback,
    back_to_main_menu_callback
)
from handlers.status_handlers import status_handler
from handlers.registration_handlers import get_registration_conversation_handler
from handlers.admin_handlers import (
    admin_dashboard_command,
    toggle_registration_callback,
    admin_verify_callback,
    admin_discard_start,
    admin_discard_reason_received,
    export_data_callback,
    broadcast_prompt,
    broadcast_msg_received,
    broadcast_confirmed,
    broadcast_cancelled,
    pin_notice_prompt,
    pin_text_received,
    pin_confirmed,
    pin_cancelled,
    AWAITING_DISCARD_REASON,
    AWAITING_BROADCAST_MSG,
    AWAITING_PIN_TEXT
)

# Setup basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Remedial Hub Telegram Bot - Application Entry Point"""
    logger.info("Initializing Remedial Hub Telegram Bot...")

    # Build Application
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    # 1. Base User Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_handler))
    application.add_handler(CommandHandler("cancel", cancel_command))

    # 2. Force Subscription & Common Callbacks
    application.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(back_to_main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(status_handler, pattern="^check_status$"))

    # 3. Static Navigation Callbacks
    application.add_handler(CallbackQueryHandler(nav_about_callback, pattern="^nav_about$"))
    application.add_handler(CallbackQueryHandler(nav_testimonial_callback, pattern="^nav_testimonial$"))
    application.add_handler(CallbackQueryHandler(nav_faq_callback, pattern="^nav_faq$"))
    application.add_handler(CallbackQueryHandler(faq_answer_callback, pattern="^faq_ans_"))
    application.add_handler(CallbackQueryHandler(nav_how_to_callback, pattern="^nav_how_to$"))

    # 4. Student Registration Flow (ConversationHandler)
    application.add_handler(get_registration_conversation_handler())

    # 5. Admin Dashboard Command & Toggle
    application.add_handler(CommandHandler("admin", admin_dashboard_command))
    application.add_handler(CallbackQueryHandler(admin_dashboard_command, pattern="^admin_dashboard$"))
    application.add_handler(CallbackQueryHandler(toggle_registration_callback, pattern="^admin_toggle_reg$"))

    # 6. Admin Verification & CSV Export Callbacks
    application.add_handler(CallbackQueryHandler(admin_verify_callback, pattern="^adm_verify_"))
    application.add_handler(CallbackQueryHandler(export_data_callback, pattern="^export_"))

    # 7. Admin Discard Flow (ConversationHandler)
    discard_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_discard_start, pattern="^adm_discard_")],
        states={
            AWAITING_DISCARD_REASON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_discard_reason_received)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True
    )
    application.add_handler(discard_conv)

    # 8. Admin Broadcast Flow (ConversationHandler)
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(broadcast_prompt, pattern="^admin_start_broadcast$")],
        states={
            AWAITING_BROADCAST_MSG: [
                CallbackQueryHandler(broadcast_confirmed, pattern="^broadcast_confirm$"),
                CallbackQueryHandler(broadcast_cancelled, pattern="^broadcast_cancel$"),
                MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_msg_received)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True
    )
    application.add_handler(broadcast_conv)

    # 9. Admin Pinned Notice Flow (ConversationHandler)
    pin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(pin_notice_prompt, pattern="^admin_manage_pin$")],
        states={
            AWAITING_PIN_TEXT: [
                CallbackQueryHandler(pin_confirmed, pattern="^pin_confirm$"),
                CallbackQueryHandler(pin_cancelled, pattern="^pin_cancel$"),
                CallbackQueryHandler(pin_notice_prompt, pattern="^pin_edit$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, pin_text_received)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True
    )
    application.add_handler(pin_conv)

    # Start Polling
    logger.info("Bot is polling for updates...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()