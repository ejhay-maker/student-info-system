"""Unit tests for the Student model and StudentService."""
import json
import os
import tempfile
import unittest

from src.models.student import Student
from src.services.student_service import StudentService
from src.utils.exceptions import (
    DuplicateStudentError,
    StorageError,
    StudentNotFoundError,
    ValidationError,
)


def make_student(sid="2024-001", **overrides):
    data = dict(
        student_id=sid, first_name="Juan", last_name="Dela Cruz",
        email="juan@example.com", course="BSIT", year_level=3,
    )
    data.update(overrides)
    return Student(**data)


class StudentServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "students.json")
        self.service = StudentService(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_and_get(self):
        self.service.add_student(make_student())
        self.assertEqual(self.service.get_student("2024-001").first_name, "Juan")

    def test_data_is_stored_as_json(self):
        self.service.add_student(make_student())
        with open(self.path, encoding="utf-8") as f:
            self.assertIn("2024-001", json.load(f))

    def test_duplicate_id_rejected(self):
        self.service.add_student(make_student())
        with self.assertRaises(DuplicateStudentError):
            self.service.add_student(make_student())

    def test_list_and_search(self):
        self.service.add_student(make_student("1"))
        self.service.add_student(make_student("2", first_name="Maria", last_name="Santos"))
        self.assertEqual(len(self.service.list_students()), 2)
        self.assertEqual(self.service.search_students("maria")[0].student_id, "2")

    def test_update(self):
        self.service.add_student(make_student())
        updated = self.service.update_student("2024-001", course="BSCS", year_level="4")
        self.assertEqual((updated.course, updated.year_level), ("BSCS", 4))

    def test_update_blank_keeps_value(self):
        self.service.add_student(make_student())
        updated = self.service.update_student("2024-001", first_name="")
        self.assertEqual(updated.first_name, "Juan")

    def test_update_invalid_email_rejected(self):
        self.service.add_student(make_student())
        with self.assertRaises(ValidationError):
            self.service.update_student("2024-001", email="not-an-email")

    def test_delete(self):
        self.service.add_student(make_student())
        self.service.delete_student("2024-001")
        with self.assertRaises(StudentNotFoundError):
            self.service.get_student("2024-001")

    def test_missing_student_errors(self):
        with self.assertRaises(StudentNotFoundError):
            self.service.delete_student("nope")
        with self.assertRaises(StudentNotFoundError):
            self.service.update_student("nope", course="X")

    def test_corrupted_file_raises_storage_error(self):
        with open(self.path, "w") as f:
            f.write("{ not json")
        with self.assertRaises(StorageError):
            self.service.list_students()


class StudentModelTests(unittest.TestCase):
    def test_invalid_values(self):
        for bad in (
            dict(email="bad"), dict(year_level=9), dict(year_level="abc"),
            dict(first_name=" "), dict(student_id="has space"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    make_student(**bad)


if __name__ == "__main__":
    unittest.main()
