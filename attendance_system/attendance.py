"""
Attendance System – Core business logic.

Functions for student registration, attendance marking, and report generation.
"""
import sqlite3
from datetime import date, datetime
from calendar import monthrange

from .db import get_connection, initialize_db


# ---------------------------------------------------------------------------
# Student management (teacher)
# ---------------------------------------------------------------------------

def add_student(roll_number: str, name: str, db_path=None) -> tuple[bool, str]:
    """Register a student.  Returns (success, message)."""
    roll_number = roll_number.strip()
    name = name.strip()
    if not roll_number:
        return False, "Roll number cannot be empty."
    if not name:
        return False, "Student name cannot be empty."
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO students (roll_number, name) VALUES (?, ?)",
            (roll_number, name),
        )
        conn.commit()
        return True, f"Student '{name}' (roll {roll_number}) registered."
    except sqlite3.IntegrityError:
        return False, f"Roll number '{roll_number}' is already registered."
    finally:
        conn.close()


def get_student(roll_number: str, db_path=None):
    """Return student row or None."""
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT roll_number, name FROM students WHERE roll_number = ?",
        (roll_number,),
    ).fetchone()
    conn.close()
    return row


def list_students(db_path=None) -> list[dict]:
    """Return all registered students."""
    conn = get_connection(db_path)
    rows = conn.execute("SELECT roll_number, name FROM students ORDER BY roll_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Attendance (student)
# ---------------------------------------------------------------------------

def mark_attendance(roll_number: str, attendance_date: str | None = None,
                    status: str = "P", db_path=None) -> tuple[bool, str]:
    """
    Mark a student present (P) or absent (A) for a given date.

    Parameters
    ----------
    roll_number : str
    attendance_date : str | None   YYYY-MM-DD; defaults to today
    status : str                   'P' or 'A'
    db_path : str | None

    Returns
    -------
    (success: bool, message: str)
    """
    roll_number = roll_number.strip()
    if not roll_number:
        return False, "Roll number cannot be empty."

    if status not in ("P", "A"):
        return False, f"Invalid status '{status}'. Use 'P' (present) or 'A' (absent)."

    target_date = attendance_date or date.today().isoformat()

    # Validate date format
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        return False, f"Invalid date format '{target_date}'. Use YYYY-MM-DD."

    conn = get_connection(db_path)

    # Check student exists
    student = conn.execute(
        "SELECT roll_number FROM students WHERE roll_number = ?",
        (roll_number,),
    ).fetchone()
    if not student:
        conn.close()
        return False, f"Roll number '{roll_number}' is not registered."

    try:
        conn.execute(
            "INSERT INTO attendance (roll_number, date, status) VALUES (?, ?, ?)",
            (roll_number, target_date, status),
        )
        conn.commit()
        label = "Present" if status == "P" else "Absent"
        return True, f"Attendance marked: {roll_number} → {label} on {target_date}."
    except sqlite3.IntegrityError:
        return False, f"Attendance already recorded for {roll_number} on {target_date}."
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Reports (teacher)
# ---------------------------------------------------------------------------

def generate_monthly_report(year: int, month: int, db_path=None) -> dict:
    """
    Generate a monthly attendance report.

    Returns
    -------
    {
        "year": int,
        "month": int,
        "days_in_month": int,
        "students": [
            {
                "roll_number": str,
                "name": str,
                "records": {  "YYYY-MM-DD": "P" | "A" | "-"  },
                "present_count": int,
                "absent_count": int,
                "unmarked_count": int,
            },
            ...
        ]
    }
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}")

    conn = get_connection(db_path)
    students = conn.execute(
        "SELECT roll_number, name FROM students ORDER BY roll_number"
    ).fetchall()

    days = monthrange(year, month)[1]
    month_prefix = f"{year:04d}-{month:02d}"

    report_students = []
    for stu in students:
        roll = stu["roll_number"]
        # Fetch attendance rows for this student in the month
        rows = conn.execute(
            "SELECT date, status FROM attendance "
            "WHERE roll_number = ? AND date LIKE ?",
            (roll, f"{month_prefix}-%"),
        ).fetchall()
        attendance_map = {r["date"]: r["status"] for r in rows}

        records = {}
        present = absent = unmarked = 0
        for d in range(1, days + 1):
            day_str = f"{month_prefix}-{d:02d}"
            st = attendance_map.get(day_str, "-")
            records[day_str] = st
            if st == "P":
                present += 1
            elif st == "A":
                absent += 1
            else:
                unmarked += 1

        report_students.append({
            "roll_number": roll,
            "name": stu["name"],
            "records": records,
            "present_count": present,
            "absent_count": absent,
            "unmarked_count": unmarked,
        })

    conn.close()
    return {
        "year": year,
        "month": month,
        "days_in_month": days,
        "students": report_students,
    }


def format_report_text(report: dict) -> str:
    """Pretty-print a monthly report as a text table."""
    lines = []
    lines.append(f"Attendance Report — {report['year']:04d}-{report['month']:02d}")
    lines.append(f"Days in month: {report['days_in_month']}")
    lines.append("=" * 70)

    for stu in report["students"]:
        lines.append(f"\n{stu['name']}  (Roll: {stu['roll_number']})")
        lines.append(f"  Present: {stu['present_count']}  |  "
                      f"Absent: {stu['absent_count']}  |  "
                      f"Unmarked: {stu['unmarked_count']}")
        # Day-by-day
        day_strs = []
        for day_date, st in sorted(stu["records"].items()):
            day_num = int(day_date.split("-")[2])
            day_strs.append(f"{day_num:2d}:{st}")
        # Print in rows of 10
        for i in range(0, len(day_strs), 10):
            lines.append("  " + "  ".join(day_strs[i:i+10]))

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
