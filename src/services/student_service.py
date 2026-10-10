"""Business logic and JSON persistence for student records (CRUD)."""
import json
import logging
import os
import tempfile
from typing import Dict, List

from src.models.student import Student
from src.utils.exceptions import (
    DuplicateStudentError,
    StorageError,
    StudentNotFoundError,
    ValidationError,
)

logger = logging.getLogger("sis.service")

# Fields a caller is allowed to change through update_student().
UPDATABLE_FIELDS = {"first_name", "last_name", "email", "course", "year_level"}


class StudentService:
    """Create, read, update and delete students stored in a JSON file."""

    def __init__(self, data_file: str):
        self.data_file = data_file
        self._ensure_file()

    # ---------- storage helpers ----------
    def _ensure_file(self) -> None:
        """Create the data file (and folder) if it does not exist."""
        try:
            os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)
            if not os.path.exists(self.data_file):
                self._save({})
                logger.info("Created new data file: %s", self.data_file)
        except OSError as exc:
            raise StorageError(f"Cannot prepare data file: {exc}") from exc

    def _load(self) -> Dict[str, Student]:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as exc:
            logger.error("Corrupted JSON in %s: %s", self.data_file, exc)
            raise StorageError("Data file is corrupted (invalid JSON).") from exc
        except OSError as exc:
            logger.error("Cannot read %s: %s", self.data_file, exc)
            raise StorageError(f"Cannot read data file: {exc}") from exc

        records = raw.values() if isinstance(raw, dict) else raw  # accept list or dict
        students = [Student.from_dict(item) for item in records]
        return {s.student_id: s for s in students}

    def _save(self, students: Dict[str, Student]) -> None:
        """Write atomically so a crash never leaves a half-written file."""
        payload = {sid: s.to_dict() for sid, s in students.items()}
        directory = os.path.dirname(self.data_file) or "."
        try:
            fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.data_file)
        except OSError as exc:
            logger.error("Cannot write %s: %s", self.data_file, exc)
            raise StorageError(f"Cannot save data: {exc}") from exc

    # ---------- CRUD ----------
    def add_student(self, student: Student) -> Student:
        students = self._load()
        if student.student_id in students:
            raise DuplicateStudentError(
                f"Student ID '{student.student_id}' already exists."
            )
        students[student.student_id] = student
        self._save(students)
        logger.info("Added student %s (%s)", student.student_id, student.full_name)
        return student

    def get_student(self, student_id: str) -> Student:
        students = self._load()
        try:
            return students[student_id.strip()]
        except KeyError:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.") from None

    def list_students(self) -> List[Student]:
        return sorted(self._load().values(), key=lambda s: s.last_name.lower())

    def search_students(self, keyword: str) -> List[Student]:
        keyword = keyword.lower().strip()
        return [
            s
            for s in self.list_students()
            if keyword in s.full_name.lower()
            or keyword in s.course.lower()
            or keyword in s.student_id.lower()
        ]

    def update_student(self, student_id: str, **changes) -> Student:
        unknown = set(changes) - UPDATABLE_FIELDS
        if unknown:
            raise ValidationError(f"Cannot update field(s): {', '.join(sorted(unknown))}")
        students = self._load()
        student_id = student_id.strip()
        if student_id not in students:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.")

        data = students[student_id].to_dict()
        data.update({k: v for k, v in changes.items() if v not in (None, "")})
        updated = Student.from_dict(data)  # re-validates everything
        students[student_id] = updated
        self._save(students)
        logger.info("Updated student %s", student_id)
        return updated

    def delete_student(self, student_id: str) -> None:
        students = self._load()
        student_id = student_id.strip()
        if student_id not in students:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.")
        del students[student_id]
        self._save(students)
        logger.info("Deleted student %s", student_id)
