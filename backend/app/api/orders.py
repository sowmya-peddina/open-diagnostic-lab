from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.entities import (
    Doctor,
    Order,
    OrderStatus,
    OrderTest,
    Patient,
    ResultValue,
    TestDefinition,
    TestParameter,
)
from app.schemas.common import OrderCreate, OrderOut, OrderResultsUpdate, ResultValueOut
from app.services.codes import next_order_number
from app.services.flags import compute_flag

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_query(db: DbSession):
    return db.query(Order).options(
        selectinload(Order.patient),
        selectinload(Order.doctor),
        selectinload(Order.order_tests)
        .selectinload(OrderTest.test_definition)
        .selectinload(TestDefinition.parameters),
        selectinload(Order.order_tests)
        .selectinload(OrderTest.results)
        .selectinload(ResultValue.test_parameter),
    )


def _serialize_order(order: Order) -> dict:
    order_tests = []
    for ot in order.order_tests:
        results = []
        for r in ot.results:
            results.append(
                ResultValueOut(
                    id=r.id,
                    test_parameter_id=r.test_parameter_id,
                    value_text=r.value_text,
                    value_numeric=r.value_numeric,
                    flag=r.flag,
                    parameter=r.test_parameter,
                )
            )
        order_tests.append(
            {
                "id": ot.id,
                "test_definition_id": ot.test_definition_id,
                "test_definition": ot.test_definition,
                "results": results,
            }
        )
    return {
        "id": order.id,
        "order_number": order.order_number,
        "patient_id": order.patient_id,
        "doctor_id": order.doctor_id,
        "status": order.status,
        "notes": order.notes,
        "ordered_at": order.ordered_at,
        "completed_at": order.completed_at,
        "patient": order.patient,
        "doctor": order.doctor,
        "order_tests": order_tests,
    }


@router.get("", response_model=list[OrderOut])
def list_orders(
    db: DbSession,
    _: CurrentUser,
    limit: int = Query(default=50, le=200),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
) -> list[dict]:
    query = _order_query(db).order_by(Order.id.desc())
    if status_filter:
        query = query.filter(Order.status == status_filter)
    orders = query.limit(limit).all()
    return [_serialize_order(o) for o in orders]


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: DbSession, user: CurrentUser) -> dict:
    patient = db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=400, detail="Patient not found")
    if payload.doctor_id:
        doctor = db.get(Doctor, payload.doctor_id)
        if not doctor:
            raise HTTPException(status_code=400, detail="Doctor not found")

    tests = (
        db.query(TestDefinition)
        .options(selectinload(TestDefinition.parameters))
        .filter(TestDefinition.id.in_(payload.test_definition_ids), TestDefinition.is_active.is_(True))
        .all()
    )
    if len(tests) != len(set(payload.test_definition_ids)):
        raise HTTPException(status_code=400, detail="One or more tests not found/active")

    order = Order(
        order_number=next_order_number(db),
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        notes=payload.notes,
        status=OrderStatus.registered,
        created_by_id=user.id,
        updated_by_id=user.id,
    )
    db.add(order)
    db.flush()

    for test in tests:
        ot = OrderTest(order_id=order.id, test_definition_id=test.id)
        db.add(ot)
        db.flush()
        for param in test.parameters:
            db.add(
                ResultValue(
                    order_test_id=ot.id,
                    test_parameter_id=param.id,
                    value_text="",
                    updated_by_id=user.id,
                )
            )

    db.commit()
    order = _order_query(db).filter(Order.id == order.id).first()
    return _serialize_order(order)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: DbSession, _: CurrentUser) -> dict:
    order = _order_query(db).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)


@router.put("/{order_id}/results", response_model=OrderOut)
def update_results(
    order_id: int, payload: OrderResultsUpdate, db: DbSession, user: CurrentUser
) -> dict:
    order = _order_query(db).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    result_map: dict[int, ResultValue] = {}
    for ot in order.order_tests:
        for r in ot.results:
            result_map[r.test_parameter_id] = r

    any_value = False
    for item in payload.results:
        result = result_map.get(item.test_parameter_id)
        if not result:
            raise HTTPException(
                status_code=400, detail=f"Parameter {item.test_parameter_id} not on this order"
            )
        param = db.get(TestParameter, item.test_parameter_id)
        numeric, flag = compute_flag(
            item.value_text,
            param.reference_min if param else None,
            param.reference_max if param else None,
        )
        result.value_text = item.value_text.strip()
        result.value_numeric = numeric
        result.flag = flag
        result.updated_by_id = user.id
        if result.value_text:
            any_value = True

    order.updated_by_id = user.id
    if payload.mark_completed:
        missing = [
            r
            for ot in order.order_tests
            for r in ot.results
            if not (r.value_text or "").strip()
        ]
        if missing:
            raise HTTPException(
                status_code=400, detail="All result values required before completing"
            )
        order.status = OrderStatus.completed
        order.completed_at = datetime.now(timezone.utc)
    elif any_value and order.status == OrderStatus.registered:
        order.status = OrderStatus.in_progress

    db.commit()
    order = _order_query(db).filter(Order.id == order_id).first()
    return _serialize_order(order)
