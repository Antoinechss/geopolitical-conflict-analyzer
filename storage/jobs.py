from datetime import datetime
from storage.db import get_connection


def start_job(job_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO jobs (job_name, status, started_at)
                VALUES (%s, 'running', NOW())
                ON CONFLICT (job_name)
                DO UPDATE SET
                  status = 'running',
                  started_at = NOW(),
                  finished_at = NULL,
                  error = NULL;
                """,
                (job_name,),
            )
        conn.commit()


def finish_job(job_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE jobs
                SET status = 'done',
                    finished_at = NOW()
                WHERE job_name = %s;
                """,
                (job_name,),
            )
        conn.commit()


def fail_job(job_name: str, error: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE jobs
                SET status = 'failed',
                    finished_at = NOW(),
                    error = %s
                WHERE job_name = %s;
                """,
                (error, job_name),
            )
        conn.commit()


def is_job_running(job_name: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status FROM jobs
                WHERE job_name = %s;
                """,
                (job_name,),
            )
            row = cur.fetchone()

    return row is not None and row[0] == "running"

