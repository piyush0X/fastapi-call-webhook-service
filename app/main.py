from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Call
from .schemas import CallEndedRequest, CallResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Call Service")


@app.post(
    "/call-ended",
    response_model=CallResponse,
)
def call_ended(
    payload: CallEndedRequest,
    db: Session = Depends(get_db),
):
    # Check whether this call_id already exists
    existing_call = (
        db.query(Call)
        .filter(Call.call_id == payload.call_id)
        .first()
    )

    if existing_call:
        return existing_call

    # Create new database record
    new_call = Call(
        call_id=payload.call_id,
        status=payload.status,
        duration_secs=payload.duration_secs,
    )

    db.add(new_call)

    try:
        db.commit()
        db.refresh(new_call)
        return new_call

    except IntegrityError:
        # Handles the case where another request inserted
        # the same call_id at almost the same time.
        db.rollback()

        existing_call = (
            db.query(Call)
            .filter(Call.call_id == payload.call_id)
            .first()
        )

        if existing_call:
            return existing_call

        raise HTTPException(
            status_code=500,
            detail="Unable to store call",
        )


@app.get(
    "/calls/{call_id}",
    response_model=CallResponse,
)
def get_call(
    call_id: str,
    db: Session = Depends(get_db),
):
    call = (
        db.query(Call)
        .filter(Call.call_id == call_id)
        .first()
    )

    if call is None:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    return call