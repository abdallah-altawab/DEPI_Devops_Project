from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=100)

    appointment_at: datetime

    notes: str | None = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_name: str
    appointment_at: datetime
    notes: str | None
    status: str
    created_at: datetime