"""Attendance System package."""
from .db import initialize_db
from .attendance import (
    add_student,
    get_student,
    list_students,
    mark_attendance,
    generate_monthly_report,
    format_report_text,
)

__all__ = [
    "initialize_db",
    "add_student",
    "get_student",
    "list_students",
    "mark_attendance",
    "generate_monthly_report",
    "format_report_text",
]
