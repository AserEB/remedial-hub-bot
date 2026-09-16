from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_dashboard_keyboard(is_active: bool) -> InlineKeyboardMarkup:
    """የአድሚን ዳሽቦርድ ዋና ሜኑ"""
    status_label = "🟢 Registration: ACTIVE" if is_active else "🔴 Registration: CLOSED"
    status_style = "danger" if is_active else "success"

    keyboard = [
        [
            InlineKeyboardButton(status_label, callback_data="admin_toggle_reg", style=status_style)
        ],
        [
            InlineKeyboardButton("📥 Export Verified (CSV)", callback_data="export_VERIFIED", style="primary"),
            InlineKeyboardButton("📥 Export Discarded (CSV)", callback_data="export_DISCARDED", style="primary")
        ],
        [
            InlineKeyboardButton("📥 Export All Students (CSV)", callback_data="export_ALL", style="primary")
        ],
        [
            InlineKeyboardButton("📢 Send Broadcast", callback_data="admin_start_broadcast", style="primary"),
            InlineKeyboardButton("📌 Pinned Notice", callback_data="admin_manage_pin", style="primary")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_verification_keyboard(student_id: int) -> InlineKeyboardMarkup:
    """የተማሪውን ደረሰኝ ለአድሚኖች ሲልክ የሚቀርቡ ውሳኔ ሰጪ አዝራሮች"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Verify (Approve)", callback_data=f"adm_verify_{student_id}", style="success"),
            InlineKeyboardButton("❌ Discard (Reject)", callback_data=f"adm_discard_{student_id}", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Broadcast ከመላኩ በፊት የሚቀርብ ማረጋገጫ"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 Post Now (ይላክ)", callback_data="broadcast_confirm", style="success"),
            InlineKeyboardButton("❌ Cancel (ሰርዝ)", callback_data="broadcast_cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pin_confirm_keyboard() -> InlineKeyboardMarkup:
    """ማስታወቂያ Pin ከመደረጉ በፊት የሚቀርብ ማረጋገጫ"""
    keyboard = [
        [
            InlineKeyboardButton("📌 Yes (Pin ይሁን)", callback_data="pin_confirm", style="success"),
            InlineKeyboardButton("✏️ Edit", callback_data="pin_edit", style="primary")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="pin_cancel", style="danger"),
            InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_dashboard", style="primary")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)