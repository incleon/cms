"""
Course Model
==============

Represents academic courses offered by departments.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.base import BaseModel


class Course(BaseModel):
    """
    Course model (e.g., B.Tech Computer Science, MBA Finance).

    Relationships:
    - MANY-TO-ONE: Course belongs to Department
    - ONE-TO-MANY: Course has many Subjects
    """

    __tablename__ = "courses"

    name = Column(String(200), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    semester = Column(Integer, nullable=True)
    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── RELATIONSHIPS ────────────────────────────────────────
    department = relationship("Department", back_populates="courses", lazy="joined")
    teacher = relationship("Teacher", backref="assigned_courses", lazy="joined")
    subjects = relationship(
        "Subject",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, code='{self.code}')>"
