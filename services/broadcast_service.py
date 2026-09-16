import asyncio
from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from database.connection import supabase


async def broadcast_message_to_all(bot: Bot, source_chat_id: int, message_id: int) -> Dict[str, int]:
    """
    ሁሉንም የቦቱን ተጠቃሚዎች Keyset አድርጎ በማምጣት
    መልዕክቱን በ 0.05 ሰከንድ ክፍተት Forward/Copy ያደርጋል[cite: 1]።
    """
    last_id = 0
    batch_size = 500
    sent_count = 0
    failed_count = 0

    while True:
        res = (
            supabase.table("students")
            .select("telegram_id")
            .gt("telegram_id", last_id)
            .order("telegram_id")
            .limit(batch_size)
            .execute()
        )
        records = res.data
        if not records:
            break

        for record in records:
            user_id = record["telegram_id"]
            try:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=source_chat_id,
                    message_id=message_id
                )
                sent_count += 1
            except TelegramError:
                failed_count += 1

            # Telegram FloodWait Protection (0.05 sec pause)[cite: 1]
            await asyncio.sleep(0.05)

        last_id = records[-1]["telegram_id"]

    return {"sent": sent_count, "failed": failed_count}