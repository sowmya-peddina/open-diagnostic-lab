from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_

from app.core.deps import CurrentUser, DbSession
from app.models.entities import Patient
from app.schemas.common import PatientCreate, PatientOut, PatientUpdate
from app.services.codes import next_patient_code

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientOut])
def list_patients(
    db: DbSession,
    _: CurrentUser,
    q: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
) -> list[Patient]:
    query = db.query(Patient).order_by(Patient.id.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
                Patient.phone.ilike(like),
                Patient.external_id.ilike(like),
            )
        )
    return query.limit(limit).all()


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: DbSession, user: CurrentUser) -> Patient:
    patient = Patient(
        patient_code=next_patient_code(db),
        created_by_id=user.id,
        **payload.model_dump(),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: DbSession, _: CurrentUser) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int, payload: PatientUpdate, db: DbSession, _: CurrentUser
) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in payload.model_dump().items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient
