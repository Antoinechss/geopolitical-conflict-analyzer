import asyncio

from storage.db import get_connection
from ingestion.fetch_global import fetch_all
from preprocessing.batch_preprocessing import preprocess_batch


def refresh_db():
    # Scrape a fresh batch of posts
    fresh_batch_raw = asyncio.run(fetch_all())
    # Apply gross preprocessing
    fresh_batch_processed = preprocess_batch(fresh_batch_raw)

    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # Remove all existing rows
            cur.execute("DELETE FROM events;")
            # Insert new rows
            for event in fresh_batch_processed:
                cur.execute(
                    """
                    INSERT INTO events (
                        event_id, source, author_id, text_raw, text_processed, created_at,
                        confidence_score, heat_score, lang, geo, context_annotations,
                        hashtags, emojis
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s
                    );
                    """,
                    (
                        event.get("event_id"),      
                        event.get("source"),      
                        event.get("author_id", None),                                 
                        event.get("text_raw"),
                        event.get("text_processed"),
                        event.get("created_at"),
                        event.get("confidence_score", None),
                        event.get("heat_score", None),     
                        event.get("lang"),
                        event.get("geo", None),
                        event.get("context_annotations", None),                            
                        event.get("hashtags"),
                        event.get("emojis")                
                    )
                )
    conn.close()
