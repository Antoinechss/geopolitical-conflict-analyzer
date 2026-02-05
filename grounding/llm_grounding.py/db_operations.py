from typing import Optional, Tuple, List 

SELECT_BATCH_SQL = """
SELECT id, actor, target, event_type, sentence_text
FROM actortargetevents
WHERE states_resolved = FALSE
ORDER BY id
LIMIT %s;
"""

UPDATE_ROW_SQL = """
UPDATE actortargetevents
SET actor_state = %s,
    target_state = %s,
    states_resolved = TRUE
WHERE id = %s;

"""



def fetch_batch(conn, batch_size: int):
    with conn.cursor() as cur:
        cur.execute(SELECT_BATCH_SQL, (batch_size,))
        return cur.fetchall()


def update_row(conn, row_id: int, actor_state: Optional[str], target_state: Optional[str]):
    with conn.cursor() as cur:
        cur.execute(UPDATE_ROW_SQL, (actor_state, target_state, row_id))


def load_states_whitelist(conn) -> Tuple[List[str], set]:
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM states;")
        states = [r[0] for r in cur.fetchall()]
    return states, set(states)