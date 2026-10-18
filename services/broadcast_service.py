import asyncio
from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError, RetryAfter
from database.connection import supabase


async def broadcast_message_to_all(bot: Bot, source_chat_id: int, message_id: int) -> Dict[str, int]:
    """
    ሁሉንም የቦቱን ተጠቃሚዎች Keyset አድርጎ በማምጣት
    መልዕክቱን በ Background በ 0.05 ሰከንድ ክፍተት Forward/Copy ያደርጋል።
    FloodWait/RetryAfter ቢያጋጥምም ራሱ ጠብቆ ያሳልፋል[cite: 13]።
    """
    last_id = 0
    batch_size = 500
    sent_count = 0
    failed_count = 0

    while True:
        try:
            res = (
                supabase.table("students")
                .select("telegram_id")
                .gt("telegram_id", last_id)
                .order("telegram_id")
                .limit(batch_size)
                .execute()
            )
            records = res.data
        except Exception:
            break

        if not records:
            break

        for record in records:
            user_id = record.get("telegram_id")
            if not user_id:
                continue

            try:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=source_chat_id,
                    message_id=message_id
                )
                sent_count += 1
            except RetryAfter as e:
                # Telegram የሰጠውን የጥበቃ ሰከንድ ጠብቆ መልሶ ይሞክራል
                await asyncio.sleep(e.retry_after + 1)
                try:
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=source_chat_id,
                        message_id=message_id
                    )
                    sent_count += 1
                except Exception:
                    failed_count += 1
            except (TelegramError, Exception):
                failed_count += 1

            # Telegram Flood Control ጥበቃ (0.05 ሰከንድ እረፍት)[cite: 13]
            await asyncio.sleep(0.05)

        last_id = records[-1]["telegram_id"]

    return {"sent": sent_count, "failed": failed_count}