
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment
from app.schemas import AppointmentCreate, AppointmentResponse


app = FastAPI(
    title="Physio API",
    description="Physio appointment management API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "application": "Physio API",
        "version": "1.0.0",
        "message": "Application is running",
    }


@app.get("/health/live")
def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


@app.post(
    "/api/v1/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
):
    db_appointment = Appointment(**appointment.model_dump())

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


@app.get(
    "/api/v1/appointments",
    response_model=list[AppointmentResponse],
)
def get_appointments(db: Session = Depends(get_db)):
    statement = select(Appointment).order_by(Appointment.id)

    return db.scalars(statement).all()


@app.get(
    "/api/v1/appointments/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


@app.delete(
    "/api/v1/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
):
    appointment = db.get(Appointment, appointment_id)

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    db.delete(appointment)
    db.commit()
