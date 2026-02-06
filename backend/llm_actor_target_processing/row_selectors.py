from typing import Literal, Optional, List, Tuple
from storage.db import get_connection

ProcessingMode = Literal[
    "all",
    "last_n",
    "missing_extraction",
    "missing_states",
]


def select_rows(
    *,
    mode: ProcessingMode,
    limit: Optional[int] = None,
) -> List[Tuple]:
    """
    Returns rows from actortargetevents depending on mode.

    Row format (fixed):
    (
        id,
        event_id,
        sentence_index,
        sentence_text,
        actor,
        target,
        event_type,
        actor_state,
        target_state,
        states_resolved,
    )
    """

    base_select = """
    SELECT
        id,
        event_id,
        sentence_index,
        sentence_text,
        actor,
        target,
        event_type,
        actor_state,
        target_state,
        states_resolved
    FROM actortargetevents
    """

    if mode == "all":
        where = ""
        order = "ORDER BY id"

    elif mode == "last_n":
        where = ""
        order = "ORDER BY id DESC"

    elif mode == "missing_extraction":
        where = "WHERE actor IS NULL OR target IS NULL OR event_type IS NULL"
        order = "ORDER BY id"

    elif mode == "missing_states":
        where = "WHERE states_resolved = FALSE"
        order = "ORDER BY id"

    else:
        raise ValueError(f"Unknown mode: {mode}")

    limit_clause = f"LIMIT {limit}" if limit else ""

    sql = f"""
    {base_select}
    {where}
    {order}
    {limit_clause};
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
