"""
Course Schemas
==============
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    duration_years: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    duration_years: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    duration_years: Optional[str] = None
    department_count: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
