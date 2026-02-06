from typing import Optional, Iterable
from storage.db import get_connection
import asyncio
from typing import Optional

from llm_actor_target_processing.row_selectors import select_rows, ProcessingMode
from llm_actor_target_processing.extract import extract_actor_target_from_text
from llm_actor_target_processing.ground import resolve_states
from llm_actor_target_processing.llm_client import OllamaClient
from storage.db import get_connection


def update_extraction(
    *,
    row_id: int,
    actor: Optional[str],
    target: Optional[str],
    event_type: Optional[str],
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE actortargetevents
                SET actor = %s,
                    target = %s,
                    event_type = %s
                WHERE id = %s;
                """,
                (actor, target, event_type, row_id),
            )
        conn.commit()


def update_grounding(
    *,
    row_id: int,
    actor_state: Optional[str],
    target_state: Optional[str],
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE actortargetevents
                SET actor_state = %s,
                    target_state = %s,
                    states_resolved = TRUE
                WHERE id = %s;
                """,
                (actor_state, target_state, row_id),
            )
        conn.commit()


async def process(
    *,
    mode: ProcessingMode,
    limit: Optional[int] = None,
):
    """
    Unified LLM processing pipeline.

    - Selects rows based on mode
    - Runs extraction if missing
    - Runs grounding if missing
    - Updates DB
    """

    client = OllamaClient()

    rows = select_rows(mode=mode, limit=limit)
    print(f"[processor] selected {len(rows)} rows")

    if not rows:
        return {"processed": 0}

    # load states whitelist ONCE per run
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM states;")
            states_list = [r[0] for r in cur.fetchall()]
    states_set = set(states_list)

    processed = 0

    for (
        row_id,
        event_id,
        sentence_index,
        sentence_text,
        actor,
        target,
        event_type,
        actor_state,
        target_state,
        states_resolved,
    ) in rows:
        print(f"[row {row_id}] actor={actor}, target={target}, event_type={event_type}")

        # ---- EXTRACTION (if missing) ----
        if actor is None or target is None or event_type is None:
            print(f"[row {row_id}] running extraction")
            extracted = await extract_actor_target_from_text(
                event_id=event_id,
                text=sentence_text,
                client=client,
            )

            # extraction returns list, but here we process ONE sentence
            if extracted:
                _, _, _, actor, target, event_type = extracted[0]

                update_extraction(
                    row_id=row_id,
                    actor=actor,
                    target=target,
                    event_type=event_type,
                )
                # Update local variables so grounding can run in same iteration
                print(f"[row {row_id}] extracted: actor={actor}, target={target}, event_type={event_type}")

        # ---- GROUNDING (if missing) ----
        print(
            f"[row {row_id}] states_resolved={states_resolved}, actor={actor}, target={target}"
        )
        if not states_resolved and actor and target and event_type:
            print(f"[row {row_id}] running grounding")
            grounded = await resolve_states(
                client=client,
                states_list=states_list,
                states_set=states_set,
                actor=actor,
                target=target,
                event_type=event_type,
                sentence_text=sentence_text,
            )

            update_grounding(
                row_id=row_id,
                actor_state=grounded["actor_state"],
                target_state=grounded["target_state"],
            )
            print(f"[row {row_id}] grounded: actor_state={grounded['actor_state']}, target_state={grounded['target_state']}")

        processed += 1

    return {"processed": processed}
