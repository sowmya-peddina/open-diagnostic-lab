from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import OrderStatus, Sex, UserRole


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserOut(ORMModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    is_active: bool


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = ""
    role: UserRole = UserRole.staff


class LoginRequest(BaseModel):
    username: str
    password: str


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=128)
    date_of_birth: Optional[date] = None
    age_years: Optional[int] = Field(default=None, ge=0, le=150)
    sex: Sex = Sex.unknown
    phone: str = ""
    address: str = ""
    external_id: str = ""


class PatientUpdate(PatientCreate):
    pass


class PatientOut(ORMModel):
    id: int
    patient_code: str
    full_name: str
    date_of_birth: Optional[date]
    age_years: Optional[int]
    sex: Sex
    phone: str
    address: str
    external_id: str
    created_at: datetime


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=128)
    specialty: str = ""
    phone: str = ""
    email: str = ""
    is_active: bool = True


class DoctorUpdate(DoctorCreate):
    pass


class DoctorOut(ORMModel):
    id: int
    full_name: str
    specialty: str
    phone: str
    email: str
    is_active: bool


class TestParameterIn(BaseModel):
    code: str
    name: str
    unit: str = ""
    reference_text: str = ""
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    sort_order: int = 0


class TestParameterOut(ORMModel):
    id: int
    code: str
    name: str
    unit: str
    reference_text: str
    reference_min: Optional[float]
    reference_max: Optional[float]
    sort_order: int


class TestDefinitionCreate(BaseModel):
    code: str
    name: str
    sample_type: str = ""
    description: str = ""
    price: Optional[float] = None
    is_active: bool = True
    parameters: list[TestParameterIn] = []


class TestDefinitionUpdate(BaseModel):
    name: str
    sample_type: str = ""
    description: str = ""
    price: Optional[float] = None
    is_active: bool = True
    parameters: list[TestParameterIn] = []


class TestDefinitionOut(ORMModel):
    id: int
    code: str
    name: str
    sample_type: str
    description: str
    price: Optional[float]
    is_active: bool
    parameters: list[TestParameterOut] = []


class OrderCreate(BaseModel):
    patient_id: int
    doctor_id: Optional[int] = None
    test_definition_ids: list[int] = Field(min_length=1)
    notes: str = ""


class ResultValueIn(BaseModel):
    test_parameter_id: int
    value_text: str = ""


class OrderResultsUpdate(BaseModel):
    results: list[ResultValueIn]
    mark_completed: bool = False


class ResultValueOut(ORMModel):
    id: int
    test_parameter_id: int
    value_text: str
    value_numeric: Optional[float]
    flag: str
    parameter: Optional[TestParameterOut] = None


class OrderTestOut(ORMModel):
    id: int
    test_definition_id: int
    test_definition: Optional[TestDefinitionOut] = None
    results: list[ResultValueOut] = []


class OrderOut(ORMModel):
    id: int
    order_number: str
    patient_id: int
    doctor_id: Optional[int]
    status: OrderStatus
    notes: str
    ordered_at: datetime
    completed_at: Optional[datetime]
    patient: Optional[PatientOut] = None
    doctor: Optional[DoctorOut] = None
    order_tests: list[OrderTestOut] = []


class ClinicSettingsOut(ORMModel):
    clinic_name: str
    address: str
    phone: str
    footer: str
    logo_url: str


class ClinicSettingsUpdate(BaseModel):
    clinic_name: str
    address: str = ""
    phone: str = ""
    footer: str = ""
    logo_url: str = ""
