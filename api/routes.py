from fastapi import APIRouter, BackgroundTasks, HTTPException
from storage.db import get_connection
from storage.refresh_db import (
    full_reboot_events,
    incremental_refresh_events,
    fetch_events_for_period,
)
from ingestion.configs.time_windows import (
    FULL_REBOOT_MONTHS,
    INCREMENTAL_REFRESH_MONTHS,
)
from api.schemas import FetchPeriodRequest
from api.globe import fetch_globe_relations
from storage.jobs import start_job, finish_job, fail_job, is_job_running
from llm_actor_target_processing.processor import process
from llm_actor_target_processing.row_selectors import ProcessingMode
from api.queries.relations import fetch_relations
from typing import Optional
from fastapi import Query
from datetime import date



router = APIRouter()


# Full reboot option
@router.post("/reboot-full")
async def reboot_full():
    await full_reboot_events(FULL_REBOOT_MONTHS)
    return {"status": "completed", "months_back": FULL_REBOOT_MONTHS}


# Up to date option
@router.post("/refresh-incremental")
async def refresh_incremental():
    await incremental_refresh_events(INCREMENTAL_REFRESH_MONTHS)
    return {"status": "completed", "months_back": INCREMENTAL_REFRESH_MONTHS}


# Custom period option
@router.post("/fetch-period")
async def fetch_period(payload: FetchPeriodRequest):
    await fetch_events_for_period(payload.start_date, payload.end_date)
    return {
        "status": "completed",
        "start_date": payload.start_date,
        "end_date": payload.end_date,
    }


# Status endpoint
@router.get("/jobs/{job_name}")
def job_status(job_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, started_at, finished_at, error FROM jobs WHERE job_name = %s",
                (job_name,),
            )
            row = cur.fetchone()

    if not row:
        return {"status": "never_run"}

    return {
        "status": row[0],
        "started_at": row[1],
        "finished_at": row[2],
        "error": row[3],
    }


# Reset/cancel a stuck job
@router.post("/jobs/{job_name}/reset")
def reset_job_endpoint(job_name: str):
    from storage.jobs import reset_job
    reset_job(job_name)
    return {"status": "reset", "job_name": job_name}


# -------------------- LLM Processing Routes -------------


async def run_llm_processing_job(mode, limit):
    """
    Background task wrapper for LLM processing.
    Handles job lifecycle transitions.
    """
    try:
        await process(mode=mode, limit=limit)
        finish_job("llm_processing")
    except Exception as e:
        fail_job("llm_processing", str(e))


# LLM processing of raw events
@router.post("/process")
async def process_events(
    background_tasks: BackgroundTasks,
    mode: ProcessingMode,
    limit: int | None = None,
):
    if is_job_running("llm_processing"):
        raise HTTPException(
            status_code=409,
            detail="LLM processing job already running",
        )

    start_job("llm_processing")

    background_tasks.add_task(
        run_llm_processing_job,
        mode,
        limit,
    )

    return {
        "status": "started",
        "job_name": "llm_processing",
    }


# -------------------- Globe visualization -------------

# Building arcs 
@router.get("/globe/relations")
def globe_relations():
    return fetch_globe_relations()

@router.get("/relations")
def get_relations(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    return fetch_relations(from_date=from_date, to_date=to_date)
