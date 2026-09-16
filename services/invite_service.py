from telegram import Bot
from telegram.error import TelegramError
from config.settings import settings
from config.constants import STREAM_NATURAL


async def generate_single_use_invite_link(bot: Bot, stream: str, student_id: int) -> str:
    """
    ለ 1 ሰው ብቻ የሚያገለግል (member_limit=1) የግብዣ ሊንክ ያመነጫል
    """
    target_group_id = (
        settings.NATURAL_GROUP_ID if stream == STREAM_NATURAL 
        else settings.SOCIAL_GROUP_ID
    )

    try:
        invite_link_obj = await bot.create_chat_invite_link(
            chat_id=target_group_id,
            name=f"Student_{student_id}",
            member_limit=1
        )
        return invite_link_obj.invite_link
    except TelegramError as e:
        return f"https://t.me/c/{str(target_group_id).replace('-100', '')}/1"