from storage.db import get_connection
from llm_actor_target_processing.extract import split_sentences


def initialize_actortargetevents(limit: int | None = None):
    """
    Create sentence-level rows in actortargetevents
    for events that are not yet materialized.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id, text_processed
                FROM events
                WHERE text_processed IS NOT NULL
                  AND event_id NOT IN (
                      SELECT DISTINCT event_id FROM actortargetevents
                  )
                """
                + (" LIMIT %s" if limit else ""),
                (limit,) if limit else None,
            )

            events = cur.fetchall()

        inserted = 0

        with conn.cursor() as cur:
            for event_id, text in events:
                sentences = split_sentences(text)

                for idx, sentence in enumerate(sentences):
                    cur.execute(
                        """
                        INSERT INTO actortargetevents (
                            event_id,
                            sentence_index,
                            sentence_text,
                            states_resolved
                        )
                        VALUES (%s, %s, %s, FALSE)
                        ON CONFLICT DO NOTHING;
                        """,
                        (event_id, idx, sentence),
                    )
                    inserted += 1

        conn.commit()

    return {"inserted": inserted}
