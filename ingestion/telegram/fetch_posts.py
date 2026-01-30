import os
from telethon import TelegramClient
import asyncio
from datetime import datetime, timezone, timedelta

from ingestion.configs import telegram_channels, CUTOFF

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

channel_name = telegram_channels[0]

# Fetching Until Cutoff
cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF)


async def fetch_telegram():
    msg_batch = []
    async with TelegramClient("session", api_id, api_hash) as client:
        
        # Get channel entity
        channel = await client.get_entity(channel_name)
        # Iterate messages from newest to oldest until older than cutoff
        async for msg in client.iter_messages(channel, limit=1000):
            if msg.date < cutoff:
                break
            if not msg.text:
                continue
            # Print simple output
            cur_message = {
                    "created_at": msg.date.isoformat(),
                    "text_raw": msg.text,
                    "source": "telegram", 
                    "lang": "eng"
                }
            msg_batch.append(cur_message)
    return msg_batch