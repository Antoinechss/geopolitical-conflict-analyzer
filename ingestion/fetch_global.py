from ingestion.telegram.fetch_posts import fetch_telegram


async def fetch_all(): 
    full_batch = []
    telegram_batch = await fetch_telegram()
    for post in telegram_batch:
        full_batch.append(post)
    return full_batch

