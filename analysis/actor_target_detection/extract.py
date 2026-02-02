import subprocess
import spacy
import json

from prompts import build_prompt
from storage.db import (
    get_connection,
    insert_actor_target_rows,
    mark_event_failed,
    mark_event_done,
    mark_event_processing,
)

# Spacy sentence segmentation configs
nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")


def parse_llm_output(
    llm_output: str, event_id: str, sentence_index: int, sentence_text: str
):
    try:
        obj = json.loads(llm_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    event_type = obj.get("event")

    if event_type == "UNDEFINED":
        return None

    return (
        event_id,
        sentence_index,
        sentence_text,
        obj.get("actor"),
        obj.get("target"),
        event_type,
    )


# LLM Call
def llm_extract(text: str) -> str:
    try:
        print("  ↳ LLM call…")

        result = subprocess.run(
            ["python", "llm_runner.py"],
            input=text,
            text=True,
            capture_output=True,
            timeout=30,  # REQUIRED
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout

    except subprocess.TimeoutExpired:
        raise RuntimeError("LLM timeout")


def extract_event_sentences(text: str) -> list[str]:
    """
    Split event text into clean sentences for LLM processing.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text and sent.text.strip()]


def main():
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT event_id, text_processed
            FROM events
            WHERE processing_status = 'pending'
              AND text_processed IS NOT NULL
            ORDER BY event_id
            """
        )
        events = cur.fetchall()

    print(f"Selected {len(events)} pending events")

    for event_id, text in events:
        print(f"\n▶ Event {event_id}")

        try:
            mark_event_processing(conn, event_id)

            sentences = extract_event_sentences(text)
            rows = []
            sentence_errors = 0

            for i, sentence in enumerate(sentences):
                prompt = build_prompt(sentence)

                try:
                    for attempt in (1, 2):
                        llm_output = llm_extract(prompt)

                        try:
                            row = parse_llm_output(
                                llm_output,
                                event_id,
                                i,
                                sentence
                            )
                            break
                        except ValueError:
                            if attempt == 2:
                                raise
                            print("    ↳ retrying sentence due to JSON error")

                    if row:
                        rows.append(row)

                except Exception:
                    sentence_errors += 1
                    print(f"    ⚠ skipping sentence {i}")
                    continue

            if not rows:
                raise RuntimeError("No valid extractions in event")

            insert_actor_target_rows(conn, rows)

            mark_event_done(conn, event_id)
            conn.commit()

            print(
                f"✔ done ({len(rows)} rows, "
                f"{sentence_errors} sentence errors)"
            )

        except Exception as e:
            conn.rollback()
            mark_event_failed(conn, event_id)
            conn.commit()
            print(f"✖ failed: {e}")

    conn.close()


if __name__ == "__main__":
    main()
