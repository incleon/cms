"""
CRUD Services — Business Logic for All Modules
==================================================

Each service:
1. Implements IService (ABSTRACTION via ABC)
2. Composes a Repository (COMPOSITION)
3. Adds business validation and transformation logic
4. Is injected into routes via FastAPI's Depends

OOP Concepts: Inheritance, Composition, Polymorphism, Method Overriding
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
import uuid

from app.services.base import IService
from app.repositories.concrete import (
    UserRepository, RoleRepository, PermissionRepository,
    StudentRepository, TeacherRepository, CourseRepository, DepartmentRepository,
    SubjectRepository, AttendanceRepository,
    MarksRepository, FeeRepository, LibraryBookRepository,
    BookIssueRepository, AuditLogRepository,
)
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.teacher import Teacher
from app.core.security import PasswordHasher
from app.core.exceptions import (
    NotFoundException, ConflictException, ValidationException, BadRequestException,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════
# USER SERVICE
# ══════════════════════════════════════════════════════════════

class UserService(IService):
    """
    User service — implements IService interface.

    Demonstrates:
    - INHERITANCE from IService (ABC)
    - COMPOSITION with UserRepository and RoleRepository
    - METHOD OVERRIDING (implements abstract methods)
    """

    def __init__(self, db: Session):
        self._user_repo = UserRepository(db)
        self._role_repo = RoleRepository(db)
        self._db = db

    def get(self, id: int) -> Optional[User]:
        user = self._user_repo.get_by_id(id)
        if not user:
            raise NotFoundException("User", id)
        return user

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._user_repo.search(
                ["email", "full_name", "username"], search, skip, page_size
            )
            total = self._user_repo.search_count(
                ["email", "full_name", "username"], search
            )
        else:
            items = self._user_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._user_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]) -> User:
        # Check for duplicate email
        if self._user_repo.get_by_email(data.get("email", "")):
            raise ConflictException(detail="Email already registered")
        if self._user_repo.get_by_username(data.get("username", "")):
            raise ConflictException(detail="Username already taken")

        role_ids = data.pop("role_ids", [])
        password = data.pop("password")
        data["hashed_password"] = PasswordHasher.hash_password(password)

        user = self._user_repo.create(data)

        # Assign roles
        for role_id in role_ids:
            self._user_repo.assign_role(user.id, role_id)

        self._db.refresh(user)
        return user

    def update(self, id: int, data: Dict[str, Any]) -> Optional[User]:
        user = self._user_repo.get_by_id(id)
        if not user:
            raise NotFoundException("User", id)

        role_ids = data.pop("role_ids", None)

        # Filter None values
        update_data = {k: v for k, v in data.items() if v is not None}
        if update_data:
            self._user_repo.update(id, update_data)

        if role_ids is not None:
            # Remove existing roles and assign new ones
            existing = self._db.query(UserRole).filter(UserRole.user_id == id).all()
            for ur in existing:
                self._db.delete(ur)
            self._db.flush()
            for role_id in role_ids:
                self._user_repo.assign_role(id, role_id)

        self._db.refresh(user)
        return user

    def delete(self, id: int) -> bool:
        return self._user_repo.soft_delete(id)


# ══════════════════════════════════════════════════════════════
# STUDENT SERVICE
# ══════════════════════════════════════════════════════════════

class StudentService(IService):
    """Student service — creates both User and Student records."""

    def __init__(self, db: Session):
        self._student_repo = StudentRepository(db)
        self._user_repo = UserRepository(db)
        self._role_repo = RoleRepository(db)
        self._db = db

    def get(self, id: int):
        student = self._student_repo.get_by_id(id)
        if not student:
            raise NotFoundException("Student", id)
        return student

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._student_repo.search(
                ["enrollment_number"], search, skip, page_size
            )
            total = self._student_repo.search_count(["enrollment_number"], search)
        else:
            items = self._student_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._student_repo.count()

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        # Check duplicate enrollment
        if self._student_repo.get_by_enrollment(data.get("enrollment_number", "")):
            raise ConflictException(detail="Enrollment number already exists")
        if self._user_repo.get_by_email(data.get("email", "")):
            raise ConflictException(detail="Email already registered")

        # Create user first
        user_data = {
            "email": data.pop("email"),
            "username": data.pop("username"),
            "hashed_password": PasswordHasher.hash_password(data.pop("password")),
            "full_name": data.pop("full_name"),
            "phone": data.pop("phone", None),
            "gender": data.pop("gender", None),
        }
        user = self._user_repo.create(user_data)

        # Assign student role
        student_role = self._role_repo.get_by_name("student")
        if student_role:
            self._user_repo.assign_role(user.id, student_role.id)

        # Create student profile
        data["user_id"] = user.id
        student = self._student_repo.create(data)
        self._db.refresh(student)
        return student

    def update(self, id: int, data: Dict[str, Any]):
        student = self._student_repo.get_by_id(id)
        if not student:
            raise NotFoundException("Student", id)

        # Update user fields
        user_fields = {}
        for field in ["full_name", "phone"]:
            if field in data and data[field] is not None:
                user_fields[field] = data.pop(field)
        if user_fields:
            self._user_repo.update(student.user_id, user_fields)

        # Update student fields
        update_data = {k: v for k, v in data.items() if v is not None}
        if update_data:
            self._student_repo.update(id, update_data)

        self._db.refresh(student)
        return student

    def delete(self, id: int) -> bool:
        student = self._student_repo.get_by_id(id)
        if not student:
            return False
        self._user_repo.soft_delete(student.user_id)
        return self._student_repo.soft_delete(id)


# ══════════════════════════════════════════════════════════════
# TEACHER SERVICE
# ══════════════════════════════════════════════════════════════

class TeacherService(IService):
    """Teacher service — creates both User and Teacher records."""

    def __init__(self, db: Session):
        self._teacher_repo = TeacherRepository(db)
        self._user_repo = UserRepository(db)
        self._role_repo = RoleRepository(db)
        self._db = db

    def get(self, id: int):
        teacher = self._teacher_repo.get_by_id(id)
        if not teacher:
            raise NotFoundException("Teacher", id)
        return teacher

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._teacher_repo.search(
                ["employee_id"], search, skip, page_size
            )
            total = self._teacher_repo.search_count(["employee_id"], search)
        else:
            items = self._teacher_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._teacher_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        if not data.get("employee_id"):
            last_teacher = self._db.query(Teacher).order_by(Teacher.id.desc()).first()
            next_seq = (last_teacher.id + 1) if last_teacher else 1
            data["employee_id"] = f"EMP-{datetime.now().year}-{next_seq:04d}"
        elif self._teacher_repo.get_by_employee_id(data.get("employee_id", "")):
            raise ConflictException(detail="Employee ID already exists")
            
        if self._user_repo.get_by_email(data.get("email", "")):
            raise ConflictException(detail="Email already registered")

        user_data = {
            "email": data.pop("email"),
            "username": data.pop("username"),
            "hashed_password": PasswordHasher.hash_password(data.pop("password")),
            "full_name": data.pop("full_name"),
            "phone": data.pop("phone", None),
            "gender": data.pop("gender", None),
        }
        user = self._user_repo.create(user_data)

        teacher_role = self._role_repo.get_by_name("teacher")
        if teacher_role:
            self._user_repo.assign_role(user.id, teacher_role.id)

        data["user_id"] = user.id
        teacher = self._teacher_repo.create(data)
        self._db.refresh(teacher)
        return teacher

    def update(self, id: int, data: Dict[str, Any]):
        teacher = self._teacher_repo.get_by_id(id)
        if not teacher:
            raise NotFoundException("Teacher", id)

        user_fields = {}
        for field in ["full_name", "phone"]:
            if field in data and data[field] is not None:
                user_fields[field] = data.pop(field)
        if user_fields:
            self._user_repo.update(teacher.user_id, user_fields)

        update_data = {k: v for k, v in data.items() if v is not None}
        if update_data:
            self._teacher_repo.update(id, update_data)

        self._db.refresh(teacher)
        return teacher

    def delete(self, id: int) -> bool:
        teacher = self._teacher_repo.get_by_id(id)
        if not teacher:
            return False
        self._user_repo.soft_delete(teacher.user_id)
        return self._teacher_repo.soft_delete(id)


# ══════════════════════════════════════════════════════════════
# COURSE SERVICE
# ══════════════════════════════════════════════════════════════

class CourseService(IService):
    def __init__(self, db: Session):
        self._course_repo = CourseRepository(db)
        self._db = db

    def get(self, id: int):
        course = self._course_repo.get_by_id(id)
        if not course:
            raise NotFoundException("Course", id)
        return course

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._course_repo.search(["name", "code"], search, skip, page_size)
            total = self._course_repo.search_count(["name", "code"], search)
        else:
            items = self._course_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._course_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        if self._course_repo.get_by_code(data.get("code", "")):
            raise ConflictException(detail="Course code already exists")
        return self._course_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        result = self._course_repo.update(id, update_data)
        if not result:
            raise NotFoundException("Course", id)
        return result

    def delete(self, id: int) -> bool:
        return self._course_repo.soft_delete(id)


# ══════════════════════════════════════════════════════════════
# DEPARTMENT SERVICE
# ══════════════════════════════════════════════════════════════

class DepartmentService(IService):
    def __init__(self, db: Session):
        self._dept_repo = DepartmentRepository(db)
        self._db = db

    def get(self, id: int):
        dept = self._dept_repo.get_by_id(id)
        if not dept:
            raise NotFoundException("Department", id)
        return dept

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._dept_repo.search(["name", "code"], search, skip, page_size)
            total = self._dept_repo.search_count(["name", "code"], search)
        else:
            items = self._dept_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._dept_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        if self._dept_repo.get_by_code(data.get("code", "")):
            raise ConflictException(detail="Department code already exists")
        return self._dept_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        result = self._dept_repo.update(id, update_data)
        if not result:
            raise NotFoundException("Department", id)
        return result

    def delete(self, id: int) -> bool:
        return self._dept_repo.soft_delete(id)


# ══════════════════════════════════════════════════════════════
# SUBJECT SERVICE
# ══════════════════════════════════════════════════════════════

class SubjectService(IService):
    def __init__(self, db: Session):
        self._subject_repo = SubjectRepository(db)
        self._db = db

    def get(self, id: int):
        subject = self._subject_repo.get_by_id(id)
        if not subject:
            raise NotFoundException("Subject", id)
        return subject

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._subject_repo.search(["name", "code"], search, skip, page_size)
            total = self._subject_repo.search_count(["name", "code"], search)
        else:
            items = self._subject_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._subject_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        if self._subject_repo.get_by_code(data.get("code", "")):
            raise ConflictException(detail="Subject code already exists")
        return self._subject_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        result = self._subject_repo.update(id, update_data)
        if not result:
            raise NotFoundException("Subject", id)
        return result

    def delete(self, id: int) -> bool:
        return self._subject_repo.soft_delete(id)

    def assign_teacher(self, subject_id: int, teacher_id: int, section: str = None):
        return self._subject_repo.assign_teacher(subject_id, teacher_id, section)


# ══════════════════════════════════════════════════════════════
# ATTENDANCE SERVICE
# ══════════════════════════════════════════════════════════════

class AttendanceService(IService):
    def __init__(self, db: Session):
        self._attendance_repo = AttendanceRepository(db)
        self._db = db

    def get(self, id: int):
        att = self._attendance_repo.get_by_id(id)
        if not att:
            raise NotFoundException("Attendance", id)
        return att

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        items = self._attendance_repo.get_all(skip, page_size, sort_by, sort_order)
        total = self._attendance_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        return self._attendance_repo.create(data)

    def bulk_create(self, subject_id: int, att_date: date, records: list, teacher_id: int = None):
        """Bulk create attendance for a class."""
        created = []
        for record in records:
            att_data = {
                "student_id": record["student_id"],
                "subject_id": subject_id,
                "date": att_date,
                "status": record.get("status", "present"),
                "teacher_id": teacher_id,
                "remarks": record.get("remarks"),
            }
            created.append(self._attendance_repo.create(att_data))
        return created

    def update(self, id: int, data: Dict[str, Any]):
        return self._attendance_repo.update(id, data)

    def delete(self, id: int) -> bool:
        return self._attendance_repo.soft_delete(id)

    def get_student_stats(self, student_id: int):
        return self._attendance_repo.get_student_attendance_stats(student_id)


# ══════════════════════════════════════════════════════════════
# MARKS SERVICE
# ══════════════════════════════════════════════════════════════

class MarksService(IService):
    def __init__(self, db: Session):
        self._marks_repo = MarksRepository(db)
        self._db = db

    def get(self, id: int):
        marks = self._marks_repo.get_by_id(id)
        if not marks:
            raise NotFoundException("Marks", id)
        return marks

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        items = self._marks_repo.get_all(skip, page_size, sort_by, sort_order)
        total = self._marks_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        if data.get("marks_obtained", 0) > data.get("max_marks", 100):
            raise ValidationException("Marks obtained cannot exceed maximum marks")
        return self._marks_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        return self._marks_repo.update(id, update_data)

    def delete(self, id: int) -> bool:
        return self._marks_repo.soft_delete(id)

    def get_student_marks(self, student_id: int, semester: int = None):
        return self._marks_repo.get_student_marks(student_id, semester)


# ══════════════════════════════════════════════════════════════
# FEE SERVICE
# ══════════════════════════════════════════════════════════════

class FeeService(IService):
    def __init__(self, db: Session):
        self._fee_repo = FeeRepository(db)
        self._db = db

    def get(self, id: int):
        fee = self._fee_repo.get_by_id(id)
        if not fee:
            raise NotFoundException("Fee", id)
        return fee

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        items = self._fee_repo.get_all(skip, page_size, sort_by, sort_order)
        total = self._fee_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        return self._fee_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        return self._fee_repo.update(id, update_data)

    def delete(self, id: int) -> bool:
        return self._fee_repo.soft_delete(id)

    def record_payment(self, fee_id: int, paid_amount: float, payment_method: str = "cash"):
        """Record a fee payment."""
        fee = self.get(fee_id)
        new_paid = fee.paid_amount + paid_amount
        receipt = f"RCP-{uuid.uuid4().hex[:8].upper()}"

        update_data = {
            "paid_amount": new_paid,
            "payment_method": payment_method,
            "receipt_number": receipt,
            "paid_date": date.today(),
        }

        if new_paid >= fee.amount:
            update_data["status"] = "paid"
        else:
            update_data["status"] = "partial"

        self._fee_repo.update(fee_id, update_data)
        self._db.refresh(fee)
        return fee

    def get_pending_fees(self):
        return self._fee_repo.get_pending_fees()


# ══════════════════════════════════════════════════════════════
# LIBRARY SERVICE
# ══════════════════════════════════════════════════════════════

class LibraryService(IService):
    def __init__(self, db: Session):
        self._book_repo = LibraryBookRepository(db)
        self._issue_repo = BookIssueRepository(db)
        self._db = db

    def get(self, id: int):
        book = self._book_repo.get_by_id(id)
        if not book:
            raise NotFoundException("Book", id)
        return book

    def list(self, page=1, page_size=10, search=None, sort_by="id", sort_order="desc"):
        skip = (page - 1) * page_size
        if search:
            items = self._book_repo.search(
                ["title", "author", "isbn", "category"], search, skip, page_size
            )
            total = self._book_repo.search_count(
                ["title", "author", "isbn", "category"], search
            )
        else:
            items = self._book_repo.get_all(skip, page_size, sort_by, sort_order)
            total = self._book_repo.count()
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def create(self, data: Dict[str, Any]):
        data["available_copies"] = data.get("total_copies", 1)
        return self._book_repo.create(data)

    def update(self, id: int, data: Dict[str, Any]):
        update_data = {k: v for k, v in data.items() if v is not None}
        return self._book_repo.update(id, update_data)

    def delete(self, id: int) -> bool:
        return self._book_repo.soft_delete(id)

    def issue_book(self, book_id: int, student_id: int, due_date: date):
        book = self.get(book_id)
        if book.available_copies <= 0:
            raise ValidationException("No copies available for issue")

        issue_data = {
            "book_id": book_id,
            "student_id": student_id,
            "issue_date": date.today(),
            "due_date": due_date,
            "status": "issued",
        }
        issue = self._issue_repo.create(issue_data)

        # Decrement available copies
        self._book_repo.update(book_id, {"available_copies": book.available_copies - 1})
        return issue

    def return_book(self, issue_id: int, fine: int = 0):
        issue = self._issue_repo.get_by_id(issue_id)
        if not issue:
            raise NotFoundException("BookIssue", issue_id)

        self._issue_repo.update(issue_id, {
            "return_date": date.today(),
            "status": "returned",
            "fine_amount": fine,
        })

        # Increment available copies
        book = self._book_repo.get_by_id(issue.book_id)
        if book:
            self._book_repo.update(book.id, {"available_copies": book.available_copies + 1})

        self._db.refresh(issue)
        return issue

    def get_active_issues(self, student_id: int = None):
        return self._issue_repo.get_active_issues(student_id)


# ══════════════════════════════════════════════════════════════
# AUDIT SERVICE
# ══════════════════════════════════════════════════════════════

class AuditService:
    """Audit logging service."""

    def __init__(self, db: Session):
        self._audit_repo = AuditLogRepository(db)

    def log(self, user_id: int, action: str, resource: str,
            resource_id: int = None, details: str = None,
            old_values: dict = None, new_values: dict = None,
            ip_address: str = None, user_agent: str = None):
        return self._audit_repo.create({
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details,
            "old_values": old_values,
            "new_values": new_values,
            "ip_address": ip_address,
            "user_agent": user_agent,
        })

    def get_user_activity(self, user_id: int, limit: int = 50):
        return self._audit_repo.get_by_user(user_id, limit)
