import psycopg2
import os
from psycopg2.extras import execute_values
from contextlib import contextmanager

from dotenv import load_dotenv
load_dotenv()

# Default batch size for fetching events
BATCH_SIZE = 100


@contextmanager
def get_connection():
    conn = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
    )
    try:
        yield conn
    finally:
        conn.close()



def fetch_events(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT event_id, text_processed
            FROM events
            WHERE text_processed IS NOT NULL
              AND lang = 'eng'
              AND event_id NOT IN (
                  SELECT DISTINCT event_id FROM actortargetevents
              )
            LIMIT %s
        """,
            (BATCH_SIZE,),
        )
        return cur.fetchall()


def insert_rows(conn, rows):
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO actortargetevents
            (event_id, sentence_index, sentence_text, actor, target, event_type)
            VALUES %s
            ON CONFLICT (event_id, sentence_index) DO NOTHING
            """,
            rows,
        )
    conn.commit()


def insert_actor_target_rows(conn, rows):
    """
    rows: list of tuples
    (event_id, sentence_index, sentence_text, actor, target, event_type)
    """
    if not rows:
        return

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO actortargetevents
            (event_id, sentence_index, sentence_text, actor, target, event_type)
            VALUES %s
            ON CONFLICT (event_id, sentence_index) DO NOTHING
            """,
            rows,
        )


# Processing Status Helpers : 

def mark_event_processing(conn, event_id):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE events SET processing_status = 'processing' WHERE event_id = %s",
            (event_id,),
        )


def mark_event_done(conn, event_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE events
            SET processing_status = 'done',
                processed_at = NOW()
            WHERE event_id = %s
            """,
            (event_id,),
        )


def mark_event_failed(conn, event_id):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE events SET processing_status = 'failed' WHERE event_id = %s",
            (event_id,),
        )
 