from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Order, Patient


def next_patient_code(db: Session) -> str:
    count = db.scalar(select(func.count()).select_from(Patient)) or 0
    return f"P{count + 1:06d}"


def next_order_number(db: Session) -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"ORD-{today}-"
    existing = db.scalar(
        select(func.count()).select_from(Order).where(Order.order_number.like(f"{prefix}%"))
    ) or 0
    return f"{prefix}{existing + 1:04d}"
