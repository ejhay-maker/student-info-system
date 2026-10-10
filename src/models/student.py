"""Student data model with built-in validation."""
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime

from src.utils.exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ID_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")


@dataclass
class Student:
    """Represents a single student record."""

    student_id: str
    first_name: str
    last_name: str
    email: str
    course: str
    year_level: int
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """Raise ValidationError if any field is invalid."""
        self.student_id = str(self.student_id).strip()
        if not ID_PATTERN.match(self.student_id):
            raise ValidationError(
                "Student ID is required and may only contain letters, numbers and hyphens."
            )
        for label, value in (
            ("First name", self.first_name),
            ("Last name", self.last_name),
            ("Course", self.course),
        ):
            if not str(value).strip():
                raise ValidationError(f"{label} cannot be empty.")
        if not EMAIL_PATTERN.match(str(self.email).strip()):
            raise ValidationError(f"Invalid email address: '{self.email}'.")
        try:
            self.year_level = int(self.year_level)
        except (TypeError, ValueError):
            raise ValidationError("Year level must be a whole number.")
        if not 1 <= self.year_level <= 6:
            raise ValidationError("Year level must be between 1 and 6.")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        try:
            return cls(**data)
        except TypeError as exc:
            raise ValidationError(f"Malformed student record: {exc}") from exc
