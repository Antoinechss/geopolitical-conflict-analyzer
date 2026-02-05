import os
from telethon import TelegramClient
from datetime import datetime, timezone, timedelta

from ingestion.configs.sources import telegram_channels


async def fetch_telegram(months_back: int):
    """Fetch posts from past date until today (full reboot and refresh functions)"""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError("TELEGRAM_API_ID or TELEGRAM_API_HASH not set")

    cutoff = datetime.now(timezone.utc) - timedelta(days=30 * months_back)

    channel_name = telegram_channels[0]
    msg_batch = []

    async with TelegramClient("telegram_fetch", api_id, api_hash) as client:
        channel = await client.get_entity(channel_name)

        async for msg in client.iter_messages(channel, limit=5000):
            if msg.date < cutoff:
                break
            if not msg.text:
                continue

            msg_batch.append({
                "created_at": msg.date.isoformat(),
                "text_raw": msg.text,
                "source": "telegram",
                "lang": "eng",
            })

    return msg_batch


async def fetch_telegram_period(
    start_date: datetime,
    end_date: datetime,
):
    """Fetch posts from user provided start / end period"""
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        raise RuntimeError("TELEGRAM_API_ID or TELEGRAM_API_HASH not set")

    channel_name = telegram_channels[0]
    msg_batch = []

    async with TelegramClient("telegram_fetch", api_id, api_hash) as client:
        channel = await client.get_entity(channel_name)

        async for msg in client.iter_messages(channel, limit=10000):
            if msg.date < start_date:
                break
            if msg.date > end_date:
                continue
            if not msg.text:
                continue

            msg_batch.append({
                "created_at": msg.date.isoformat(),
                "text_raw": msg.text,
                "source": "telegram",
                "lang": "eng",
            })

    return msg_batch

