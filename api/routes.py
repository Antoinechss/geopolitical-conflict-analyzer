from fastapi import APIRouter
from storage.refresh_db import full_reboot_events, incremental_refresh_events, fetch_events_for_period
from ingestion.configs.time_windows import (
    FULL_REBOOT_MONTHS,
    INCREMENTAL_REFRESH_MONTHS,
)
from api.schemas import FetchPeriodRequest


router = APIRouter()


# Full reboot option
@router.post("/reboot-full")
def reboot_full():
    full_reboot_events(FULL_REBOOT_MONTHS)
    return {"status": "completed", "months_back": FULL_REBOOT_MONTHS}


# Up to date option
@router.post("/refresh-incremental")
def refresh_incremental():
    incremental_refresh_events(INCREMENTAL_REFRESH_MONTHS)
    return {"status": "completed", "months_back": INCREMENTAL_REFRESH_MONTHS}


# Custom period option
@router.post("/fetch-period")
def fetch_period(payload: FetchPeriodRequest):
    fetch_events_for_period(
        payload.start_date,
        payload.end_date
    )
    return {
        "status": "completed",
        "start_date": payload.start_date,
        "end_date": payload.end_date
    }