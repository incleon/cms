"""Course Schemas"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CourseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    semester: Optional[int] = None
    teacher_id: Optional[int] = None
    department_id: int


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    semester: Optional[int] = None
    teacher_id: Optional[int] = None
    department_id: Optional[int] = None


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    semester: Optional[int] = None
    teacher_id: Optional[int] = None
    department_id: int
    department_name: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
