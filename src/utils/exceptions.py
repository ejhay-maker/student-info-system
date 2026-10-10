"""Custom exceptions used across the Student Information System."""


class StudentError(Exception):
    """Base class for all application-specific errors."""


class ValidationError(StudentError):
    """Raised when student data fails validation."""


class StudentNotFoundError(StudentError):
    """Raised when a student ID does not exist."""


class DuplicateStudentError(StudentError):
    """Raised when adding a student whose ID already exists."""


class StorageError(StudentError):
    """Raised when the JSON data file cannot be read or written."""
