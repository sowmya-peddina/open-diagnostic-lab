from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session, selectinload
from weasyprint import HTML

from app.models.entities import ClinicSettings, Order, OrderTest, ResultValue, TestDefinition

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def load_order(db: Session, order_id: int) -> Order | None:
    return (
        db.query(Order)
        .options(
            selectinload(Order.patient),
            selectinload(Order.doctor),
            selectinload(Order.order_tests)
            .selectinload(OrderTest.test_definition)
            .selectinload(TestDefinition.parameters),
            selectinload(Order.order_tests)
            .selectinload(OrderTest.results)
            .selectinload(ResultValue.test_parameter),
        )
        .filter(Order.id == order_id)
        .first()
    )


def clinic_settings(db: Session) -> ClinicSettings:
    settings = db.query(ClinicSettings).first()
    if not settings:
        settings = ClinicSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def render_report_html(db: Session, order: Order) -> str:
    settings = clinic_settings(db)
    sections = []
    for ot in order.order_tests:
        rows = []
        for r in sorted(ot.results, key=lambda x: x.test_parameter.sort_order if x.test_parameter else 0):
            p = r.test_parameter
            rows.append(
                {
                    "name": p.name if p else "",
                    "value": r.value_text or "—",
                    "unit": p.unit if p else "",
                    "reference": p.reference_text if p else "",
                    "flag": r.flag or "",
                }
            )
        sections.append(
            {
                "test_name": ot.test_definition.name if ot.test_definition else "",
                "sample_type": ot.test_definition.sample_type if ot.test_definition else "",
                "rows": rows,
            }
        )

    patient = order.patient
    age = ""
    if patient:
        if patient.age_years is not None:
            age = f"{patient.age_years} yrs"
        elif patient.date_of_birth and order.ordered_at:
            age = f"{(order.ordered_at.date() - patient.date_of_birth).days // 365} yrs"

    html = _env().get_template("report.html").render(
        clinic=settings,
        order=order,
        patient=patient,
        doctor=order.doctor,
        age=age,
        sections=sections,
    )
    return html


def render_report_pdf(db: Session, order: Order) -> bytes:
    html = render_report_html(db, order)
    return HTML(string=html).write_pdf()
