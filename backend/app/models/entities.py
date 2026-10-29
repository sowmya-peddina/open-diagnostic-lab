from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"


class OrderStatus(str, enum.Enum):
    registered = "registered"
    in_progress = "in_progress"
    completed = "completed"


class Sex(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.staff)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    age_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[Sex] = mapped_column(Enum(Sex), default=Sex.unknown)
    phone: Mapped[str] = mapped_column(String(32), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    external_id: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    orders: Mapped[list[Order]] = relationship(back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(128), index=True)
    specialty: Mapped[str] = mapped_column(String(128), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(128), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    orders: Mapped[list[Order]] = relationship(back_populates="doctor")


class TestDefinition(Base):
    __tablename__ = "test_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    sample_type: Mapped[str] = mapped_column(String(64), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    parameters: Mapped[list[TestParameter]] = relationship(
        back_populates="test_definition", cascade="all, delete-orphan"
    )


class TestParameter(Base):
    __tablename__ = "test_parameters"
    __table_args__ = (UniqueConstraint("test_definition_id", "code", name="uq_param_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_definition_id: Mapped[int] = mapped_column(ForeignKey("test_definitions.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    unit: Mapped[str] = mapped_column(String(32), default="")
    reference_text: Mapped[str] = mapped_column(String(255), default="")
    reference_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    test_definition: Mapped[TestDefinition] = relationship(back_populates="parameters")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("doctors.id"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.registered)
    notes: Mapped[str] = mapped_column(Text, default="")
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient: Mapped[Patient] = relationship(back_populates="orders")
    doctor: Mapped[Doctor | None] = relationship(back_populates="orders")
    order_tests: Mapped[list[OrderTest]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderTest(Base):
    __tablename__ = "order_tests"
    __table_args__ = (UniqueConstraint("order_id", "test_definition_id", name="uq_order_test"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    test_definition_id: Mapped[int] = mapped_column(ForeignKey("test_definitions.id"))

    order: Mapped[Order] = relationship(back_populates="order_tests")
    test_definition: Mapped[TestDefinition] = relationship()
    results: Mapped[list[ResultValue]] = relationship(
        back_populates="order_test", cascade="all, delete-orphan"
    )


class ResultValue(Base):
    __tablename__ = "result_values"
    __table_args__ = (UniqueConstraint("order_test_id", "test_parameter_id", name="uq_result_param"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_test_id: Mapped[int] = mapped_column(ForeignKey("order_tests.id", ondelete="CASCADE"))
    test_parameter_id: Mapped[int] = mapped_column(ForeignKey("test_parameters.id"))
    value_text: Mapped[str] = mapped_column(String(128), default="")
    value_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    flag: Mapped[str] = mapped_column(String(16), default="")  # H, L, or empty
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    order_test: Mapped[OrderTest] = relationship(back_populates="results")
    test_parameter: Mapped[TestParameter] = relationship()


class ClinicSettings(Base):
    __tablename__ = "clinic_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    clinic_name: Mapped[str] = mapped_column(String(255), default="Open Diagnostic Lab")
    address: Mapped[str] = mapped_column(Text, default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    footer: Mapped[str] = mapped_column(Text, default="This report is computer generated.")
    logo_url: Mapped[str] = mapped_column(String(512), default="")
