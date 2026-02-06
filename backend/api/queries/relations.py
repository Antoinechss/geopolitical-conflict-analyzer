from storage.db import get_connection
from typing import Optional
from datetime import date


def fetch_relations(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    sql = """
    SELECT
        ate.actor_state_iso3   AS source,
        ate.target_state_iso3  AS target,
        ate.event_type,
        COUNT(*)               AS weight,
        sa.latitude            AS source_lat,
        sa.longitude           AS source_lon,
        st.latitude            AS target_lat,
        st.longitude           AS target_lon
    FROM actortargetevents ate
    JOIN events ev ON ev.event_id = ate.event_id
    JOIN states sa ON sa.iso3 = ate.actor_state_iso3
    JOIN states st ON st.iso3 = ate.target_state_iso3
    WHERE
        ate.actor_state_iso3 IS NOT NULL
        AND ate.target_state_iso3 IS NOT NULL
        AND ate.event_type IS NOT NULL
        AND (%s IS NULL OR ev.created_at >= %s)
        AND (%s IS NULL OR ev.created_at <= %s)
    GROUP BY
        ate.actor_state_iso3,
        ate.target_state_iso3,
        ate.event_type,
        sa.latitude,
        sa.longitude,
        st.latitude,
        st.longitude
    ORDER BY weight DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (from_date, from_date, to_date, to_date),
            )
            rows = cur.fetchall()

    return [
        {
            "source": r[0],        # ISO3
            "target": r[1],        # ISO3
            "event_type": r[2],
            "weight": r[3],
            "source_lat": r[4],
            "source_lon": r[5],
            "target_lat": r[6],
            "target_lon": r[7],
        }
        for r in rows
    ]
