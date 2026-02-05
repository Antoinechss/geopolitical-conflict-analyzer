# Request model to validate user input of dates

from pydantic import BaseModel
from datetime import datetime


class FetchPeriodRequest(BaseModel):
    start_date: datetime
    end_date: datetime
