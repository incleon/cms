"""
Concrete Repositories — Each extends BaseRepository with custom queries
=========================================================================

OOP Concept: INHERITANCE + METHOD OVERRIDING
Each repository inherits generic CRUD from BaseRepository and adds
model-specific query methods.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.repositories.base import BaseRepository
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.course import Course
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.department import Department
from app.models.subject import Subject, SubjectTeacher
from app.models.attendance import Attendance
from app.models.marks import Marks
from app.models.fee import Fee
from app.models.library import LibraryBook, BookIssue
from app.models.audit_log import AuditLog
from app.models.timetable import Timetable
from app.models.notification import Notification


# ══════════════════════════════════════════════════════════════
# USER REPOSITORY
# ══════════════════════════════════════════════════════════════

class UserRepository(BaseRepository[User]):
    """
    User repository — INHERITS BaseRepository and OVERRIDES/EXTENDS it.

    Demonstrates:
    - INHERITANCE: Gets create, get_by_id, get_all, update, delete for free
    - METHOD OVERRIDING: Adds user-specific query methods
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Custom query — not in base repository."""
        return (
            self._db.query(User)
            .options(joinedload(User.user_roles).joinedload(UserRole.role))
            .filter(User.email == email, User.is_deleted == False)
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self._db.query(User)
            .filter(User.username == username, User.is_deleted == False)
            .first()
        )

    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[User]:
        """OVERRIDE: Eager-load roles and permissions for users."""
        query = (
            self._db.query(User)
            .options(
                joinedload(User.user_roles)
                .joinedload(UserRole.role)
                .joinedload(Role.role_permissions)
                .joinedload(RolePermission.permission)
            )
            .filter(User.id == id)
        )
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.first()

    def assign_role(self, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self._db.add(user_role)
        self._db.commit()
        return user_role

    def remove_role(self, user_id: int, role_id: int) -> bool:
        ur = (
            self._db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )
        if ur:
            self._db.delete(ur)
            self._db.commit()
            return True
        return False


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        return self._db.query(Role).filter(Role.name == name).first()

    def assign_permission(self, role_id: int, permission_id: int) -> RolePermission:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self._db.add(rp)
        self._db.commit()
        return rp


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: Session):
        super().__init__(Permission, db)

    def get_by_name(self, name: str) -> Optional[Permission]:
        return self._db.query(Permission).filter(Permission.name == name).first()

    def get_by_resource(self, resource: str) -> List[Permission]:
        return self._db.query(Permission).filter(Permission.resource == resource).all()


# ══════════════════════════════════════════════════════════════
# STUDENT REPOSITORY
# ══════════════════════════════════════════════════════════════

class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_enrollment(self, enrollment: str) -> Optional[Student]:
        return (
            self._db.query(Student)
            .options(joinedload(Student.user), joinedload(Student.department))
            .filter(Student.enrollment_number == enrollment, Student.is_deleted == False)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[Student]:
        return (
            self._db.query(Student)
            .options(joinedload(Student.user), joinedload(Student.department))
            .filter(Student.user_id == user_id, Student.is_deleted == False)
            .first()
        )

    def get_by_department(self, department_id: int) -> List[Student]:
        return (
            self._db.query(Student)
            .options(joinedload(Student.user))
            .filter(Student.department_id == department_id, Student.is_deleted == False)
            .all()
        )

    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[Student]:
        """OVERRIDE: Eager load user and department."""
        query = (
            self._db.query(Student)
            .options(joinedload(Student.user), joinedload(Student.department))
            .filter(Student.id == id)
        )
        if not include_deleted:
            query = query.filter(Student.is_deleted == False)
        return query.first()


# ══════════════════════════════════════════════════════════════
# TEACHER REPOSITORY
# ══════════════════════════════════════════════════════════════

class TeacherRepository(BaseRepository[Teacher]):
    def __init__(self, db: Session):
        super().__init__(Teacher, db)

    def get_by_employee_id(self, emp_id: str) -> Optional[Teacher]:
        return (
            self._db.query(Teacher)
            .options(joinedload(Teacher.user), joinedload(Teacher.department))
            .filter(Teacher.employee_id == emp_id, Teacher.is_deleted == False)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[Teacher]:
        return (
            self._db.query(Teacher)
            .options(joinedload(Teacher.user), joinedload(Teacher.department))
            .filter(Teacher.user_id == user_id, Teacher.is_deleted == False)
            .first()
        )

    def get_by_department(self, department_id: int) -> List[Teacher]:
        return (
            self._db.query(Teacher)
            .options(joinedload(Teacher.user))
            .filter(Teacher.department_id == department_id, Teacher.is_deleted == False)
            .all()
        )

    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[Teacher]:
        query = (
            self._db.query(Teacher)
            .options(joinedload(Teacher.user), joinedload(Teacher.department))
            .filter(Teacher.id == id)
        )
        if not include_deleted:
            query = query.filter(Teacher.is_deleted == False)
        return query.first()


# ══════════════════════════════════════════════════════════════
# COURSE REPOSITORY
# ══════════════════════════════════════════════════════════════

class CourseRepository(BaseRepository[Course]):
    def __init__(self, db: Session):
        super().__init__(Course, db)

    def get_by_code(self, code: str) -> Optional[Course]:
        return (
            self._db.query(Course)
            .filter(Course.code == code, Course.is_deleted == False)
            .first()
        )


# ══════════════════════════════════════════════════════════════
# DEPARTMENT REPOSITORY
# ══════════════════════════════════════════════════════════════

class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: Session):
        super().__init__(Department, db)

    def get_by_code(self, code: str) -> Optional[Department]:
        return (
            self._db.query(Department)
            .filter(Department.code == code, Department.is_deleted == False)
            .first()
        )


# ══════════════════════════════════════════════════════════════
# SUBJECT REPOSITORY
# ══════════════════════════════════════════════════════════════

class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, db: Session):
        super().__init__(Subject, db)

    def get_by_code(self, code: str) -> Optional[Subject]:
        return (
            self._db.query(Subject)
            .options(joinedload(Subject.department), joinedload(Subject.teacher))
            .filter(Subject.code == code, Subject.is_deleted == False)
            .first()
        )

    def get_by_department(self, department_id: int) -> List[Subject]:
        return (
            self._db.query(Subject)
            .options(joinedload(Subject.department), joinedload(Subject.teacher))
            .filter(Subject.department_id == department_id, Subject.is_deleted == False)
            .all()
        )

    def assign_teacher(self, subject_id: int, teacher_id: int, section: str = None) -> SubjectTeacher:
        st = SubjectTeacher(subject_id=subject_id, teacher_id=teacher_id, section=section)
        self._db.add(st)
        self._db.commit()
        return st

    def get_teacher_subjects(self, teacher_id: int) -> List[Subject]:
        return (
            self._db.query(Subject)
            .options(joinedload(Subject.department), joinedload(Subject.teacher))
            .filter(Subject.teacher_id == teacher_id, Subject.is_deleted == False)
            .all()
        )


# ══════════════════════════════════════════════════════════════
# ATTENDANCE REPOSITORY
# ══════════════════════════════════════════════════════════════

class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: Session):
        super().__init__(Attendance, db)

    def get_by_student_subject(
        self, student_id: int, subject_id: int
    ) -> List[Attendance]:
        return (
            self._db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == subject_id,
                Attendance.is_deleted == False,
            )
            .order_by(Attendance.date.desc())
            .all()
        )

    def get_student_attendance_stats(self, student_id: int):
        """Get attendance percentage for a student."""
        total = (
            self._db.query(func.count(Attendance.id))
            .filter(Attendance.student_id == student_id, Attendance.is_deleted == False)
            .scalar()
        )
        present = (
            self._db.query(func.count(Attendance.id))
            .filter(
                Attendance.student_id == student_id,
                Attendance.status == "present",
                Attendance.is_deleted == False,
            )
            .scalar()
        )
        percentage = (present / total * 100) if total > 0 else 0
        return {"total": total, "present": present, "percentage": round(percentage, 2)}


# ══════════════════════════════════════════════════════════════
# MARKS REPOSITORY
# ══════════════════════════════════════════════════════════════

class MarksRepository(BaseRepository[Marks]):
    def __init__(self, db: Session):
        super().__init__(Marks, db)

    def get_student_marks(self, student_id: int, semester: int = None) -> List[Marks]:
        query = (
            self._db.query(Marks)
            .options(joinedload(Marks.subject))
            .filter(Marks.student_id == student_id, Marks.is_deleted == False)
        )
        if semester:
            query = query.filter(Marks.semester == semester)
        return query.all()

    def get_by_subject(self, subject_id: int, exam_type: str = None) -> List[Marks]:
        query = (
            self._db.query(Marks)
            .options(joinedload(Marks.student).joinedload(Student.user))
            .filter(Marks.subject_id == subject_id, Marks.is_deleted == False)
        )
        if exam_type:
            query = query.filter(Marks.exam_type == exam_type)
        return query.all()


# ══════════════════════════════════════════════════════════════
# FEE REPOSITORY
# ══════════════════════════════════════════════════════════════

class FeeRepository(BaseRepository[Fee]):
    def __init__(self, db: Session):
        super().__init__(Fee, db)

    def get_student_fees(self, student_id: int) -> List[Fee]:
        return (
            self._db.query(Fee)
            .filter(Fee.student_id == student_id, Fee.is_deleted == False)
            .order_by(Fee.created_at.desc())
            .all()
        )

    def get_pending_fees(self) -> List[Fee]:
        return (
            self._db.query(Fee)
            .options(joinedload(Fee.student).joinedload(Student.user))
            .filter(Fee.status.in_(["pending", "partial", "overdue"]), Fee.is_deleted == False)
            .all()
        )

    def get_total_pending(self) -> float:
        result = (
            self._db.query(func.sum(Fee.amount - Fee.paid_amount))
            .filter(Fee.status.in_(["pending", "partial", "overdue"]), Fee.is_deleted == False)
            .scalar()
        )
        return result or 0.0

    def get_total_collected(self) -> float:
        result = (
            self._db.query(func.sum(Fee.paid_amount))
            .filter(Fee.is_deleted == False)
            .scalar()
        )
        return result or 0.0


# ══════════════════════════════════════════════════════════════
# LIBRARY REPOSITORIES
# ══════════════════════════════════════════════════════════════

class LibraryBookRepository(BaseRepository[LibraryBook]):
    def __init__(self, db: Session):
        super().__init__(LibraryBook, db)

    def get_by_isbn(self, isbn: str) -> Optional[LibraryBook]:
        return (
            self._db.query(LibraryBook)
            .filter(LibraryBook.isbn == isbn, LibraryBook.is_deleted == False)
            .first()
        )

    def get_available_books(self) -> List[LibraryBook]:
        return (
            self._db.query(LibraryBook)
            .filter(LibraryBook.available_copies > 0, LibraryBook.is_deleted == False)
            .all()
        )


class BookIssueRepository(BaseRepository[BookIssue]):
    def __init__(self, db: Session):
        super().__init__(BookIssue, db)

    def get_active_issues(self, student_id: int = None) -> List[BookIssue]:
        query = (
            self._db.query(BookIssue)
            .options(
                joinedload(BookIssue.book),
                joinedload(BookIssue.student).joinedload(Student.user),
            )
            .filter(BookIssue.status == "issued", BookIssue.is_deleted == False)
        )
        if student_id:
            query = query.filter(BookIssue.student_id == student_id)
        return query.all()

    def get_overdue_count(self) -> int:
        from datetime import date
        return (
            self._db.query(BookIssue)
            .filter(
                BookIssue.status == "issued",
                BookIssue.due_date < date.today(),
                BookIssue.is_deleted == False,
            )
            .count()
        )


# ══════════════════════════════════════════════════════════════
# AUDIT LOG REPOSITORY
# ══════════════════════════════════════════════════════════════

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def get_by_user(self, user_id: int, limit: int = 50) -> List[AuditLog]:
        return (
            self._db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_resource(self, resource: str, resource_id: int = None) -> List[AuditLog]:
        query = self._db.query(AuditLog).filter(AuditLog.resource == resource)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        return query.order_by(AuditLog.created_at.desc()).all()


# ══════════════════════════════════════════════════════════════
# TIMETABLE REPOSITORY
# ══════════════════════════════════════════════════════════════

class TimetableRepository(BaseRepository[Timetable]):
    def __init__(self, db: Session):
        super().__init__(Timetable, db)

    def get_by_student(self, semester: int, section: str = None) -> List[Timetable]:
        query = self._db.query(Timetable).filter(Timetable.semester == semester)
        if section:
            query = query.filter(Timetable.section == section)
        return query.all()

    def get_by_teacher(self, teacher_id: int) -> List[Timetable]:
        return self._db.query(Timetable).filter(Timetable.teacher_id == teacher_id).all()


# ══════════════════════════════════════════════════════════════
# NOTIFICATION REPOSITORY
# ══════════════════════════════════════════════════════════════

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = self._db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_all_read(self, user_id: int) -> int:
        notifications = self._db.query(Notification).filter(
            Notification.user_id == user_id, 
            Notification.is_read == False
        ).all()
        for n in notifications:
            n.is_read = True
        self._db.commit()
        return len(notifications)
