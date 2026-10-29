"""Idempotent seed for admin user, clinic settings, and sample test catalog."""

from copy import deepcopy

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.entities import ClinicSettings, Doctor, TestDefinition, TestParameter, User, UserRole

SAMPLE_TESTS = [
    {
        "code": "FBS",
        "name": "Fasting Blood Sugar",
        "sample_type": "Blood",
        "parameters": [
            {
                "code": "GLU",
                "name": "Glucose (Fasting)",
                "unit": "mg/dL",
                "reference_text": "70 - 100",
                "reference_min": 70,
                "reference_max": 100,
                "sort_order": 1,
            }
        ],
    },
    {
        "code": "CBC",
        "name": "Complete Blood Count",
        "sample_type": "Blood",
        "parameters": [
            {
                "code": "HB",
                "name": "Hemoglobin",
                "unit": "g/dL",
                "reference_text": "12.0 - 16.0",
                "reference_min": 12.0,
                "reference_max": 16.0,
                "sort_order": 1,
            },
            {
                "code": "WBC",
                "name": "Total Leukocyte Count",
                "unit": "/cumm",
                "reference_text": "4000 - 11000",
                "reference_min": 4000,
                "reference_max": 11000,
                "sort_order": 2,
            },
            {
                "code": "PLT",
                "name": "Platelet Count",
                "unit": "lakhs/cumm",
                "reference_text": "1.5 - 4.5",
                "reference_min": 1.5,
                "reference_max": 4.5,
                "sort_order": 3,
            },
        ],
    },
    {
        "code": "LIPID",
        "name": "Lipid Profile",
        "sample_type": "Blood",
        "parameters": [
            {
                "code": "CHOL",
                "name": "Total Cholesterol",
                "unit": "mg/dL",
                "reference_text": "< 200",
                "reference_min": None,
                "reference_max": 200,
                "sort_order": 1,
            },
            {
                "code": "TG",
                "name": "Triglycerides",
                "unit": "mg/dL",
                "reference_text": "< 150",
                "reference_min": None,
                "reference_max": 150,
                "sort_order": 2,
            },
            {
                "code": "HDL",
                "name": "HDL Cholesterol",
                "unit": "mg/dL",
                "reference_text": "> 40",
                "reference_min": 40,
                "reference_max": None,
                "sort_order": 3,
            },
            {
                "code": "LDL",
                "name": "LDL Cholesterol",
                "unit": "mg/dL",
                "reference_text": "< 100",
                "reference_min": None,
                "reference_max": 100,
                "sort_order": 4,
            },
        ],
    },
]


def seed(db: Session) -> None:
    cfg = get_settings()

    if not db.query(User).filter(User.username == cfg.admin_username).first():
        db.add(
            User(
                username=cfg.admin_username,
                full_name="Administrator",
                role=UserRole.admin,
                hashed_password=hash_password(cfg.admin_password),
            )
        )

    if not db.query(ClinicSettings).first():
        db.add(
            ClinicSettings(
                clinic_name=cfg.clinic_name,
                address=cfg.clinic_address,
                phone=cfg.clinic_phone,
                footer=cfg.clinic_footer,
            )
        )

    if not db.query(Doctor).first():
        db.add(
            Doctor(
                full_name="Dr. Sample Referring",
                specialty="General Medicine",
                phone="",
            )
        )

    for raw in SAMPLE_TESTS:
        item = deepcopy(raw)
        if db.query(TestDefinition).filter(TestDefinition.code == item["code"]).first():
            continue
        params = item.pop("parameters")
        test = TestDefinition(**item, parameters=[TestParameter(**p) for p in params])
        db.add(test)

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
