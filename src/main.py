"""Command-line entry point for the Student Information System.

Run from the project root:
    python -m src.main
"""
import logging
import sys

from src.models.student import Student
from src.services.student_service import StudentService
from src.utils.config import load_config
from src.utils.exceptions import StudentError
from src.utils.logger import setup_logging

logger = logging.getLogger("sis.main")

MENU = """
========== Student Information System ==========
 1. Add student
 2. View all students
 3. Find student by ID
 4. Search students
 5. Update student
 6. Delete student
 0. Exit
================================================"""


def print_student(s: Student) -> None:
    print(
        f"  [{s.student_id}] {s.full_name} | {s.email} | "
        f"{s.course}, Year {s.year_level} | added {s.created_at}"
    )


def add_student(service: StudentService) -> None:
    student = Student(
        student_id=input("Student ID: "),
        first_name=input("First name: "),
        last_name=input("Last name: "),
        email=input("Email: "),
        course=input("Course: "),
        year_level=input("Year level (1-6): "),
    )
    service.add_student(student)
    print("Student added.")


def view_all(service: StudentService) -> None:
    students = service.list_students()
    if not students:
        print("No student records yet.")
    for s in students:
        print_student(s)


def find_one(service: StudentService) -> None:
    print_student(service.get_student(input("Student ID: ")))


def search(service: StudentService) -> None:
    results = service.search_students(input("Keyword (name/course/ID): "))
    if not results:
        print("No matches.")
    for s in results:
        print_student(s)


def update(service: StudentService) -> None:
    sid = input("ID of student to update: ")
    current = service.get_student(sid)
    print("Current record:")
    print_student(current)
    print("Press Enter to keep the current value.")
    updated = service.update_student(
        sid,
        first_name=input("New first name: "),
        last_name=input("New last name: "),
        email=input("New email: "),
        course=input("New course: "),
        year_level=input("New year level: "),
    )
    print("Updated:")
    print_student(updated)


def delete(service: StudentService) -> None:
    sid = input("ID of student to delete: ")
    if input(f"Delete '{sid}'? (y/N): ").strip().lower() == "y":
        service.delete_student(sid)
        print("Student deleted.")
    else:
        print("Cancelled.")


ACTIONS = {
    "1": add_student,
    "2": view_all,
    "3": find_one,
    "4": search,
    "5": update,
    "6": delete,
}


def main() -> int:
    try:
        config = load_config()
        setup_logging(config["log_file"], config["log_level"])
        service = StudentService(config["data_file"])
    except StudentError as exc:
        print(f"Startup error: {exc}")
        return 1

    logger.info("Application started")
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            logger.info("Application exited")
            print("Goodbye!")
            return 0
        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option, please try again.")
            continue
        try:
            action(service)
        except StudentError as exc:  # expected, user-facing errors
            logger.warning("%s: %s", type(exc).__name__, exc)
            print(f"Error: {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\nInput cancelled.")
        except Exception:  # unexpected bug: log full traceback, keep app alive
            logger.exception("Unexpected error")
            print("Something went wrong. Check logs/app.log for details.")


if __name__ == "__main__":
    sys.exit(main())
