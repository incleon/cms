"""
Timetable Model
=================

Weekly class schedule entries.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Time
from sqlalchemy.orm import relationship
import enum

from app.database.base import BaseModel


class DayOfWeek(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class Timetable(BaseModel):
    """
    Timetable entry — a single class slot in the weekly schedule.

    Relationships:
    - MANY-TO-ONE: Timetable → Subject
    - MANY-TO-ONE: Timetable → Teacher
    """

    __tablename__ = "timetables"

    subject_id = Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    teacher_id = Column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    day = Column(SAEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_number = Column(String(50), nullable=True)
    section = Column(String(10), nullable=True)
    semester = Column(Integer, nullable=False)

    # ── RELATIONSHIPS ────────────────────────────────────────
    subject = relationship("Subject", back_populates="timetable_entries")
    teacher = relationship("Teacher", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<Timetable(day={self.day}, subject={self.subject_id}, "
            f"time={self.start_time}-{self.end_time})>"
        )
