from telegram import Bot
from telegram.error import TelegramError
from config.settings import settings


async def check_user_channel_subscription(bot: Bot, user_id: int) -> bool:
    """
    ተጠቃሚው @Remedial_Hub ቻናል ውስጥ መኖሩን በ Telegram API ያረጋግጣል።
    Member, Administrator ወይም Creator ከሆነ True ይመልሳል።
    """
    try:
        member = await bot.get_chat_member(
            chat_id=settings.REQUIRED_CHANNEL_ID,
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except TelegramError:
        # ቻናሉን ካልተቀላቀለ ወይም ስህተት ከተፈጠረ
        return False