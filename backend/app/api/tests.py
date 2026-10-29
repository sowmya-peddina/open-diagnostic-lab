from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import selectinload

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.entities import TestDefinition, TestParameter
from app.schemas.common import TestDefinitionCreate, TestDefinitionOut, TestDefinitionUpdate

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("", response_model=list[TestDefinitionOut])
def list_tests(
    db: DbSession,
    _: CurrentUser,
    active_only: bool = Query(default=True),
) -> list[TestDefinition]:
    query = (
        db.query(TestDefinition)
        .options(selectinload(TestDefinition.parameters))
        .order_by(TestDefinition.name)
    )
    if active_only:
        query = query.filter(TestDefinition.is_active.is_(True))
    return query.all()


@router.post("", response_model=TestDefinitionOut, status_code=status.HTTP_201_CREATED)
def create_test(payload: TestDefinitionCreate, db: DbSession, _: AdminUser) -> TestDefinition:
    existing = db.query(TestDefinition).filter(TestDefinition.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Test code already exists")
    data = payload.model_dump()
    params = data.pop("parameters", [])
    test = TestDefinition(**data)
    test.parameters = [TestParameter(**p) for p in params]
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.put("/{test_id}", response_model=TestDefinitionOut)
def update_test(
    test_id: int, payload: TestDefinitionUpdate, db: DbSession, _: AdminUser
) -> TestDefinition:
    test = (
        db.query(TestDefinition)
        .options(selectinload(TestDefinition.parameters))
        .filter(TestDefinition.id == test_id)
        .first()
    )
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    data = payload.model_dump()
    params = data.pop("parameters", [])
    for key, value in data.items():
        setattr(test, key, value)
    test.parameters.clear()
    for p in params:
        test.parameters.append(TestParameter(**p))
    db.commit()
    db.refresh(test)
    return test


@router.get("/{test_id}", response_model=TestDefinitionOut)
def get_test(test_id: int, db: DbSession, _: CurrentUser) -> TestDefinition:
    test = (
        db.query(TestDefinition)
        .options(selectinload(TestDefinition.parameters))
        .filter(TestDefinition.id == test_id)
        .first()
    )
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test
