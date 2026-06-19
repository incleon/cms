"""
Student Schemas
=================
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime


class StudentCreate(BaseModel):
    # User fields
    email: str
    username: str
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    # Student fields
    enrollment_number: str
    department_id: int
    date_of_birth: Optional[date] = None
    admission_date: Optional[date] = None
    semester: int = 1
    section: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None
    status: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    enrollment_number: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_name: Optional[str] = None
    department_id: Optional[int] = None
    semester: int = 1
    section: Optional[str] = None
    date_of_birth: Optional[date] = None
    admission_date: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None
    status: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
