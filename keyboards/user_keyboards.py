from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.settings import settings


def get_force_sub_keyboard() -> InlineKeyboardMarkup:
    """ቻናሉን የግዴታ እንዲቀላቀሉ የሚያስገድድ አዝራር"""
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=f"https://t.me/{settings.REQUIRED_CHANNEL_USERNAME.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ ተቀላቅያለሁ / Verify",
                callback_data="check_subscription",
                style="success"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard():
    keyboard = [
        # 1ኛ ረድፍ፡ Register Now (ከላይ ሙሉ ስፋት)
        [InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success")],
        
        # 2ኛ ረድፍ፡ My Status እና FAQ ጎን ለጎን
        [
            InlineKeyboardButton("📊 My Status", callback_data="check_status", style="primary"),
            InlineKeyboardButton("❓ FAQ", callback_data="nav_faq", style="primary")
        ],b
        
        # 3ኛ ረድፍ፡ How To Register? እና About Us ጎን ለጎን
        [
            InlineKeyboardButton("🎥 How To Register?", callback_data="nav_how_to", style="primary"),
            InlineKeyboardButton("ℹ️ About Us", callback_data="nav_about", style="primary")
        ],
        
        # 4ኛ ረድፍ፡ Testimonial (ሙሉ ስፋት)
        [InlineKeyboardButton("🌟 Testimonial", callback_data="nav_testimonial", style="primary")],
        
        # 5ኛ ረድፍ፡ Contact Us (ሙሉ ስፋት)
        [InlineKeyboardButton("📞 Contact Us", url="https://t.me/Remedial_Admin")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_keyboard() -> InlineKeyboardMarkup:
    """About Us ስር የሚታዩ አዝራሮች"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success"),
            InlineKeyboardButton("📞 Contact Us", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="main_menu", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_testimonial_keyboard() -> InlineKeyboardMarkup:
    """Testimonial ስር የሚታዩ አዝራሮች"""
    keyboard = [
        [
            InlineKeyboardButton(
                "🌟 Open Testimonial Channel",
                url="https://t.me/+e92-h9mv5dpjM2Q0"
            )
        ],
        [
            InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success"),
            InlineKeyboardButton("📞 Contact Us", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="main_menu", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_faq_list_keyboard() -> InlineKeyboardMarkup:
    """FAQ ጥያቄዎች ዝርዝር"""
    keyboard = [
        [InlineKeyboardButton("1️⃣ ትምህርቱን እንዴት ያስተምራል?", callback_data="faq_ans_1", style="primary")],
        [InlineKeyboardButton("2️⃣ ትምህርቱን እንዴት መከታተል እችላለሁ?", callback_data="faq_ans_2", style="primary")],
        [InlineKeyboardButton("3️⃣ ያለፈውን ትምህርት እንዴት ማግኘት እችላለሁ?", callback_data="faq_ans_3", style="primary")],
        [InlineKeyboardButton("4️⃣ ክፍያው በየወሩ ነው ወይስ አንዴ ብቻ ነው?", callback_data="faq_ans_4", style="primary")],
        [InlineKeyboardButton("5️⃣ መመዝገቢያ ስንት ብር ነው?", callback_data="faq_ans_5", style="primary")],
        [
            InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success"),
            InlineKeyboardButton("📞 Contact Us", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu", style="danger")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_faq_detail_keyboard() -> InlineKeyboardMarkup:
    """የተመረጠው FAQ መልስ ስር የሚታዩ አዝራሮች"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success"),
            InlineKeyboardButton("📞 Contact Us", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")
        ],
        [
            InlineKeyboardButton("🔙 Back to FAQ", callback_data="nav_faq", style="primary"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_how_to_register_keyboard() -> InlineKeyboardMarkup:
    """How to Register ስር የሚታዩ አዝራሮች"""
    keyboard = [
        [InlineKeyboardButton("📝 Register Now", callback_data="start_registration", style="success")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu", style="danger")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stream_selection_keyboard() -> InlineKeyboardMarkup:
    """የትምህርት ዘርፍ መምረጫ አዝራሮች"""
    keyboard = [
        [
            InlineKeyboardButton("🔬 Natural Science", callback_data="stream_NATURAL", style="primary"),
            InlineKeyboardButton("📚 Social Science", callback_data="stream_SOCIAL", style="primary")
        ],
        [
            InlineKeyboardButton("✏️ Edit Name", callback_data="reg_edit_name", style="primary"),
            InlineKeyboardButton("❌ Cancel", callback_data="reg_cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_bank_selection_keyboard() -> InlineKeyboardMarkup:
    """የባንክ መምረጫ አዝራሮች"""
    keyboard = [
        [InlineKeyboardButton("🏦 CBE (Commercial Bank of Ethiopia)", callback_data="bank_CBE", style="primary")],
        [InlineKeyboardButton("🏦 Bank of Abyssinia", callback_data="bank_ABYSSINIA", style="primary")],
        [
            InlineKeyboardButton("🔄 Edit Stream", callback_data="reg_edit_stream", style="primary"),
            InlineKeyboardButton("❌ Cancel", callback_data="reg_cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_details_keyboard() -> InlineKeyboardMarkup:
    """የባንክ አካውንት ከታየ በኋላ የሚመጣ ደረሰኝ መላኪያ አዝራር"""
    keyboard = [
        [InlineKeyboardButton("📤 Send Payment Screenshot", callback_data="prompt_receipt", style="success")],
        [
            InlineKeyboardButton("🔄 Change Bank", callback_data="reg_edit_bank", style="primary"),
            InlineKeyboardButton("❌ Cancel", callback_data="reg_cancel", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_status_keyboard() -> InlineKeyboardMarkup:
    """Status ገጽ ስር የሚታዩ አዝራሮች"""
    keyboard = [
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu", style="danger")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_discard_keyboard() -> InlineKeyboardMarkup:
    """ተማሪው Discard ሲደረግ የሚታዩት አዝራሮች"""
    keyboard = [
        [InlineKeyboardButton("🔄 Re-Register", callback_data="re_register_start", style="success")],
        [
            InlineKeyboardButton("📊 My Status", callback_data="check_status", style="primary"),
            InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style="danger")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_verified_keyboard() -> InlineKeyboardMarkup:
    """ተማሪው Verify ሲደረግ የሚታዩት አዝራሮች"""
    keyboard = [
        [InlineKeyboardButton("📊 Check My Status", callback_data="check_status", style="primary")],
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{settings.ADMIN_CONTACT_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu", style="danger")]
    ]
    return InlineKeyboardMarkup(keyboard)