from storage.db import get_connection
from storage.jobs import start_job, finish_job, fail_job, is_job_running
from preprocessing.batch_preprocessing import preprocess_batch
from ingestion.telegram.fetch_posts import fetch_telegram
from datetime import datetime
from ingestion.telegram.fetch_posts import fetch_telegram_period
from llm_actor_target_processing.processor import process


def clear_events_table(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM events;")


def insert_events(conn, events):
    with conn.cursor() as cur:
        for event in events:
            cur.execute(
                """
                INSERT INTO events (
                    event_id, source, author_id, text_raw, text_processed, created_at,
                    confidence_score, heat_score, lang, geo, context_annotations,
                    hashtags, emojis
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (event_id) DO NOTHING;
                """,
                (
                    event.get("event_id"),
                    event.get("source"),
                    event.get("author_id"),
                    event.get("text_raw"),
                    event.get("text_processed"),
                    event.get("created_at"),
                    event.get("confidence_score"),
                    event.get("heat_score"),
                    event.get("lang"),
                    event.get("geo"),
                    event.get("context_annotations"),
                    event.get("hashtags"),
                    event.get("emojis"),
                ),
            )


# FULL REBOOT OPTION :
# Delete table and fetch all events from last 3 months
async def full_reboot_events(months_back: int):

    job_name = "full_reboot"
    if is_job_running(job_name):
        return  
    start_job(job_name)

    try:
        raw_events = await fetch_telegram(months_back)
        processed_events = preprocess_batch(raw_events)

        with get_connection() as conn:
            clear_events_table(conn)
            insert_events(conn, processed_events)
            conn.commit()

        finish_job(job_name)

    except Exception as e:
        fail_job(job_name, str(e))
        raise


# UP TO DATE REFRESH OPTION
# Add the events missing from the last month until today

async def incremental_refresh_events(months_back: int):
    job_name = "incremental_refresh"

    if is_job_running(job_name):
        return

    start_job(job_name)

    try:
        raw_events = await fetch_telegram(months_back)
        processed_events = preprocess_batch(raw_events)

        with get_connection() as conn:
            insert_events(conn, processed_events)
            conn.commit()

        finish_job(job_name)

    except Exception as e:
        fail_job(job_name, str(e))
        raise


# Period start / end specified lookup option
async def fetch_events_for_period(
    start_date: datetime,
    end_date: datetime,
):
    job_name = "fetch_period"
    if is_job_running(job_name):
        return 
    start_job(job_name)

    try:
        raw_events = await fetch_telegram_period(start_date, end_date)

        processed_events = preprocess_batch(raw_events)

        with get_connection() as conn:
            insert_events(conn, processed_events)
            conn.commit()

        finish_job(job_name)

    except Exception as e:
        fail_job(job_name, str(e))
        raise

# LLM jobs background runner
async def run_llm_processing_job(mode, limit):
    try:
        await process(mode=mode, limit=limit)
        finish_job("llm_processing")
    except Exception as e:
        fail_job("llm_processing", str(e))

