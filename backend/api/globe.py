from storage.db import get_connection

def fetch_globe_relations():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    actor_state   AS source,
                    target_state  AS target,
                    event_type    AS type,
                    COUNT(*)      AS weight
                FROM actortargetevents
                WHERE
                    states_resolved = TRUE
                    AND actor_state IS NOT NULL
                    AND target_state IS NOT NULL
                GROUP BY
                    actor_state,
                    target_state,
                    event_type;
                """
            )

            rows = cur.fetchall()

    return [
        {
            "source": r[0],
            "target": r[1],
            "type": r[2],
            "weight": r[3],
        }
        for r in rows
    ]
