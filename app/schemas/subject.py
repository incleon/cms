"""Subject Schemas"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SubjectCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    credits: int = 3
    semester: int
    course_id: int


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None
    course_id: Optional[int] = None


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    credits: int
    semester: int
    course_id: int
    course_name: Optional[str] = None
    teachers: list = []
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SubjectTeacherAssign(BaseModel):
    subject_id: int
    teacher_id: int
    section: Optional[str] = None
