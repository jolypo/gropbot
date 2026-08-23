import asyncio
import logging

from telegram import Bot
from telegram.error import TelegramError

from app.config import settings

logger = logging.getLogger("telegram_bots")


async def send_startup_message(
    name: str,
    token: str,
    chat_id: str,
) -> bool:
    if not token:
        logger.error("❌ %s: BOT TOKEN IS MISSING", name)
        return False

    if not chat_id:
        logger.error("❌ %s: TELEGRAM CHAT ID IS MISSING", name)
        return False

    bot = Bot(token=token)

    try:
        me = await bot.get_me()

        logger.info(
            "✅ %s CONNECTED: @%s (id=%s)",
            name,
            me.username,
            me.id,
        )

        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ {name} يعمل الآن\n\n"
                f"🤖 @{me.username}\n"
                f"🟢 الاتصال مع Telegram ناجح\n"
                f"📡 القروب متصل\n"
            ),
        )

        logger.info("✅ %s STARTUP MESSAGE SENT TO GROUP", name)

        await bot.shutdown()
        return True

    except TelegramError as exc:
        logger.exception(
            "❌ %s TELEGRAM ERROR: %s",
            name,
            exc,
        )

    except Exception as exc:
        logger.exception(
            "❌ %s UNEXPECTED ERROR: %s",
            name,
            exc,
        )

    try:
        await bot.shutdown()
    except Exception:
        pass

    return False


async def start_all_bots() -> None:
    logger.info("========================================")
    logger.info("🚀 STARTING TELEGRAM BOTS")
    logger.info("========================================")

    results = await asyncio.gather(
        send_startup_message(
            "SIGNAL BOT",
            settings.signal_bot_token,
            settings.telegram_chat_id,
        ),
        send_startup_message(
            "PROFIT BOT",
            settings.profit_bot_token,
            settings.telegram_chat_id,
        ),
        send_startup_message(
            "LOSS BOT",
            settings.loss_bot_token,
            settings.telegram_chat_id,
        ),
        send_startup_message(
            "REPORT BOT",
            settings.report_bot_token,
            settings.telegram_chat_id,
        ),
        return_exceptions=False,
    )

    logger.info("========================================")

    names = [
        "SIGNAL BOT",
        "PROFIT BOT",
        "LOSS BOT",
        "REPORT BOT",
    ]

    for name, result in zip(names, results):
        logger.info(
            "%s => %s",
            name,
            "🟢 ONLINE" if result else "🔴 FAILED",
        )

    logger.info("========================================")
