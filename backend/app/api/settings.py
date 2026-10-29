from fastapi import APIRouter

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.entities import ClinicSettings
from app.schemas.common import ClinicSettingsOut, ClinicSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _get_or_create(db: DbSession) -> ClinicSettings:
    settings = db.query(ClinicSettings).first()
    if not settings:
        settings = ClinicSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/clinic", response_model=ClinicSettingsOut)
def get_clinic_settings(db: DbSession, _: CurrentUser) -> ClinicSettings:
    return _get_or_create(db)


@router.put("/clinic", response_model=ClinicSettingsOut)
def update_clinic_settings(
    payload: ClinicSettingsUpdate, db: DbSession, _: AdminUser
) -> ClinicSettings:
    settings = _get_or_create(db)
    for key, value in payload.model_dump().items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
