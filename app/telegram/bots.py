import asyncio
import logging

from telegram import Update, Bot
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.config import settings
from app.data.sahmk import SahmkDataProvider
from app.data.validation import validate_quote
from app.indicators.technical import add_indicators
from app.strategy.scoring import score_row
from app.risk.engine import build_levels

logger = logging.getLogger("telegram_bots")


# =========================================================
# STARTUP MESSAGE
# =========================================================

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
                f"🧪 Paper Trading"
            ),
        )

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


# =========================================================
# SIGNAL SCANNER
# =========================================================

async def scan_best_signal():

    if not settings.sahmk_api_key:
        raise RuntimeError("SAHMK_API_KEY غير موجود")

    symbols = [
        s.strip()
        for s in settings.tasi_symbols.split(",")
        if s.strip()
    ]

    if not symbols:
        raise RuntimeError(
            "TASI_SYMBOLS فارغ. أضف الأسهم في ملف .env"
        )

    provider = SahmkDataProvider(
        settings.sahmk_api_key
    )

    candidates = []

    logger.info(
        "🔎 Starting TASI scan: %s symbols",
        len(symbols),
    )

    for symbol in symbols:

        try:

            # ---------------------------------------------
            # Quote
            # ---------------------------------------------

            quote = await provider.quote(symbol)

            valid, reason = validate_quote(
                quote,
                settings.data_max_delay_minutes,
            )

            if not valid:
                logger.warning(
                    "%s rejected: %s",
                    symbol,
                    reason,
                )
                continue

            # ---------------------------------------------
            # Historical data
            # ---------------------------------------------

            df = await provider.historical(
                symbol,
                interval="1d",
            )

            if df is None or len(df) < 220:
                logger.warning(
                    "%s rejected: insufficient history",
                    symbol,
                )
                continue

            # ---------------------------------------------
            # Indicators
            # ---------------------------------------------

            df = add_indicators(df)

            row = df.iloc[-1]

            required = [
                "ema20",
                "ema50",
                "rsi14",
                "macd_hist",
                "volume_ratio",
                "higher_high",
                "higher_low",
                "resistance20",
                "atr14",
            ]

            if any(
                pd_is_missing(row.get(x))
                for x in required
            ):
                continue

            # ---------------------------------------------
            # Score
            # ---------------------------------------------

            result = score_row(row)

            if result.total < settings.min_score:
                logger.info(
                    "%s rejected: score %.1f",
                    symbol,
                    result.total,
                )
                continue

            # ---------------------------------------------
            # Trade levels
            # ---------------------------------------------

            levels = build_levels(
                float(quote.price),
                float(row["atr14"]),
                settings.min_rr,
            )

            candidates.append(
                {
                    "symbol": symbol,
                    "name": quote.name,
                    "price": float(quote.price),
                    "score": result.total,
                    "reasons": result.reasons,
                    "levels": levels,
                    "delay": quote.delay_seconds,
                }
            )

        except Exception as exc:

            logger.exception(
                "❌ Scan failed for %s: %s",
                symbol,
                exc,
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            x["score"],
            x["levels"].rr,
        ),
        reverse=True,
    )

    return candidates[0]


def pd_is_missing(value):

    if value is None:
        return True

    try:
        return bool(value != value)
    except Exception:
        return False


# =========================================================
# TELEGRAM SIGNAL MESSAGE
# =========================================================

def format_signal(signal):

    levels = signal["levels"]

    reasons = "\n".join(
        f"• {x}"
        for x in signal["reasons"]
    )

    return (
        "🚨 <b>فرصة تداول جديدة</b>\n\n"

        f"📌 <b>{signal['symbol']}</b>"
        f" — {signal['name']}\n"

        f"📈 الاتجاه: <b>شراء</b>\n\n"

        f"💰 منطقة الدخول: "
        f"<b>{levels.entry_low:.2f} – "
        f"{levels.entry_high:.2f}</b>\n\n"

        f"🛑 وقف الخسارة: "
        f"<b>{levels.stop_loss:.2f}</b>\n\n"

        f"🎯 TP1: <b>{levels.tp1:.2f}</b>\n"
        f"🎯 TP2: <b>{levels.tp2:.2f}</b>\n"
        f"🎯 TP3: <b>{levels.tp3:.2f}</b>\n\n"

        f"📊 Score: <b>{signal['score']:.0f}/100</b>\n"
        f"⚖️ Risk/Reward: "
        f"<b>1 : {levels.rr:.2f}</b>\n\n"

        f"📋 أسباب الإشارة:\n"
        f"{reasons}\n\n"

        f"⏱️ تأخير البيانات: "
        f"~{signal['delay'] / 60:.0f} دقيقة\n\n"

        "🧪 <b>PAPER TRADING</b>"
    )


# =========================================================
# /signal COMMAND
# =========================================================

async def signal_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id

    logger.info(
        "📥 /signal received from chat %s",
        chat_id,
    )

    message = await update.effective_message.reply_text(
        "🔎 جاري فحص السوق السعودي...\n"
        "⏳ لحظة، أبحث عن أفضل فرصة."
    )

    try:

        signal = await scan_best_signal()

        if signal is None:

            await message.edit_text(
                "❌ لم أجد حاليًا سهمًا يحقق شروط النظام.\n\n"
                f"الحد الأدنى للـScore: "
                f"{settings.min_score}/100\n"
                f"الحد الأدنى R:R: "
                f"1:{settings.min_rr}\n\n"
                "سأنتظر فرصة أقوى بدل إعطاء إشارة ضعيفة."
            )

            return

        await message.edit_text(
            format_signal(signal),
            parse_mode="HTML",
        )

        logger.info(
            "🚨 SIGNAL SENT: %s score=%s",
            signal["symbol"],
            signal["score"],
        )

    except Exception as exc:

        logger.exception(
            "❌ SIGNAL COMMAND ERROR: %s",
            exc,
        )

        await message.edit_text(
            "❌ حدث خطأ أثناء فحص السوق.\n\n"
            f"<code>{str(exc)[:500]}</code>",
            parse_mode="HTML",
        )


# =========================================================
# Arabic command: سقنل
# =========================================================

async def arabic_signal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await signal_command(update, context)


# =========================================================
# START SIGNAL BOT
# =========================================================

async def start_signal_bot():

    token = settings.signal_bot_token

    if not token:
        logger.error(
            "❌ SIGNAL_BOT_TOKEN is missing"
        )
        return None

    application = (
        Application
        .builder()
        .token(token)
        .build()
    )

    # /signal
    application.add_handler(
        CommandHandler(
            "signal",
            signal_command,
        )
    )

    # /سقنل إذا تيليجرام قبل الأمر
    application.add_handler(
        CommandHandler(
            "سقنل",
            arabic_signal,
        )
    )

    # كلمة "سقنل" بدون /
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Regex(r"(?i)^\s*سقنل\s*$"),
            arabic_signal,
        )
    )

    await application.initialize()

    await application.start()

    if application.updater is None:
        raise RuntimeError(
            "Telegram updater is unavailable"
        )

    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES
    )

    logger.info(
        "🟢 SIGNAL BOT POLLING STARTED"
    )

    return application


# =========================================================
# STOP SIGNAL BOT
# =========================================================

async def stop_signal_bot(application):

    if application is None:
        return

    try:

        if application.updater:

            await application.updater.stop()

        await application.stop()
        await application.shutdown()

        logger.info(
            "🔴 SIGNAL BOT STOPPED"
        )

    except Exception:

        logger.exception(
            "Error while stopping SIGNAL BOT"
        )


# =========================================================
# START ALL
# =========================================================

async def start_all_bots():

    logger.info(
        "========================================"
    )

    logger.info(
        "🚀 STARTING TELEGRAM BOTS"
    )

    logger.info(
        "========================================"
    )

    # Startup messages
    await send_startup_message(
        "SIGNAL BOT",
        settings.signal_bot_token,
        settings.telegram_chat_id,
    )

    # Actual Telegram listener
    signal_application = await start_signal_bot()

    return {
        "signal": signal_application,
    }


# =========================================================
# STOP ALL
# =========================================================

async def stop_all_bots(applications):

    if not applications:
        return

    await stop_signal_bot(
        applications.get("signal")
    )
