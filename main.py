from datetime import date, datetime, timezone
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Repair Requests API", version="1.0.0")

Priority = Literal["low", "medium", "high"]
RequestStatus = Literal["registered", "in_progress", "closed"]


class RepairRequestBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=3)
    equipment: str = Field(..., min_length=1, max_length=200)
    laboratory: str = Field(..., min_length=1, max_length=200)
    priority: Priority = "medium"
    status: RequestStatus = "registered"
    applicant: str = Field(..., min_length=1, max_length=200)
    assignee: Optional[str] = None
    planned_repair_date: Optional[date] = None
    completion_report: Optional[str] = None


class RepairRequestCreate(RepairRequestBase):
    pass


class RepairRequest(RepairRequestBase):
    id: int
    created_at: datetime


requests_db: dict[int, RepairRequest] = {}
next_id = 1


@app.get("/api/v1/requests/", response_model=list[RepairRequest])
def list_requests():
    return list(requests_db.values())


@app.get("/api/v1/requests/{request_id}", response_model=RepairRequest)
def get_request(request_id: int):
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return requests_db[request_id]


@app.post(
    "/api/v1/requests/",
    response_model=RepairRequest,
    status_code=status.HTTP_201_CREATED,
)
def create_request(payload: RepairRequestCreate):
    global next_id
    repair_request = RepairRequest(
        id=next_id,
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    requests_db[next_id] = repair_request
    next_id += 1
    return repair_request


@app.delete("/api/v1/requests/{request_id}")
def delete_request(request_id: int):
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    del requests_db[request_id]
    return {"message": "Заявка удалена", "id": request_id}
