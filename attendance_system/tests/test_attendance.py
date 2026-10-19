#!/usr/bin/env python3
"""
Comprehensive tests for the attendance_system package.

Covers all 8 requirements:
  1. Student marks attendance by roll number
  2. Persistent storage (SQLite)
  3. Duplicate attendance handling
  4. Monthly report generation
  5. Report distinguishes present/absent
  6. Invalid roll numbers handled
  7. Database initialization from clean state
  8. End-to-end workflow
"""
import os
import sys
import tempfile
import unittest

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from attendance_system.db import initialize_db, get_connection
from attendance_system.attendance import (
    add_student,
    get_student,
    list_students,
    mark_attendance,
    generate_monthly_report,
    format_report_text,
)


class AttendanceTestBase(unittest.TestCase):
    """Base class that creates a fresh temp database for each test."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        # Remove the auto-created file so initialize_db starts clean
        os.unlink(self.db_path)
        initialize_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)


class TestDatabaseInitialization(AttendanceTestBase):
    """Requirement 7: Database initialization works from a clean state."""

    def test_tables_created(self):
        conn = get_connection(self.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [t["name"] for t in tables]
        self.assertIn("students", table_names)
        self.assertIn("attendance", table_names)
        conn.close()

    def test_idempotent_init(self):
        """Calling initialize_db twice should not fail."""
        initialize_db(self.db_path)
        initialize_db(self.db_path)
        conn = get_connection(self.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        self.assertTrue(len(tables) >= 2)
        conn.close()


class TestStudentRegistration(AttendanceTestBase):
    """Teacher registering students."""

    def test_add_student_success(self):
        ok, msg = add_student("CS101", "Alice", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIn("Alice", msg)

    def test_duplicate_roll_number(self):
        add_student("CS101", "Alice", db_path=self.db_path)
        ok, msg = add_student("CS101", "Bob", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("already registered", msg)

    def test_empty_roll_number(self):
        ok, msg = add_student("", "Alice", db_path=self.db_path)
        self.assertFalse(ok)

    def test_empty_name(self):
        ok, msg = add_student("CS101", "", db_path=self.db_path)
        self.assertFalse(ok)

    def test_list_students(self):
        add_student("CS102", "Bob", db_path=self.db_path)
        add_student("CS101", "Alice", db_path=self.db_path)
        students = list_students(db_path=self.db_path)
        self.assertEqual(len(students), 2)
        # Should be sorted by roll number
        self.assertEqual(students[0]["roll_number"], "CS101")

    def test_get_student(self):
        add_student("CS101", "Alice", db_path=self.db_path)
        stu = get_student("CS101", db_path=self.db_path)
        self.assertIsNotNone(stu)
        self.assertEqual(stu["name"], "Alice")

    def test_get_nonexistent_student(self):
        stu = get_student("NOPE", db_path=self.db_path)
        self.assertIsNone(stu)


class TestMarkAttendance(AttendanceTestBase):
    """Requirements 1, 3, 6: Mark attendance, handle duplicates, invalid rolls."""

    def setUp(self):
        super().setUp()
        add_student("CS101", "Alice", db_path=self.db_path)
        add_student("CS102", "Bob", db_path=self.db_path)

    def test_mark_present(self):
        """Requirement 1: Student marks attendance by roll number."""
        ok, msg = mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIn("Present", msg)

    def test_mark_absent(self):
        ok, msg = mark_attendance("CS101", "2026-08-15", "A", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIn("Absent", msg)

    def test_duplicate_attendance(self):
        """Requirement 3: Duplicate attendance is handled correctly."""
        mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)
        ok, msg = mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("already recorded", msg)

    def test_same_student_different_days(self):
        ok1, _ = mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)
        ok2, _ = mark_attendance("CS101", "2026-08-16", "P", db_path=self.db_path)
        self.assertTrue(ok1)
        self.assertTrue(ok2)

    def test_different_students_same_day(self):
        ok1, _ = mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)
        ok2, _ = mark_attendance("CS102", "2026-08-15", "P", db_path=self.db_path)
        self.assertTrue(ok1)
        self.assertTrue(ok2)

    def test_invalid_roll_number(self):
        """Requirement 6: Invalid roll numbers are handled."""
        ok, msg = mark_attendance("INVALID999", "2026-08-15", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("not registered", msg)

    def test_empty_roll_number(self):
        ok, msg = mark_attendance("", "2026-08-15", db_path=self.db_path)
        self.assertFalse(ok)

    def test_invalid_status(self):
        ok, msg = mark_attendance("CS101", "2026-08-15", "X", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("Invalid status", msg)

    def test_invalid_date_format(self):
        ok, msg = mark_attendance("CS101", "15-08-2026", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("Invalid date", msg)


class TestPersistence(AttendanceTestBase):
    """Requirement 2: Attendance is stored persistently."""

    def test_data_persists_across_connections(self):
        add_student("CS101", "Alice", db_path=self.db_path)
        mark_attendance("CS101", "2026-08-15", "P", db_path=self.db_path)

        # Open a new connection and verify data is there
        conn = get_connection(self.db_path)
        row = conn.execute(
            "SELECT roll_number, date, status FROM attendance"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["roll_number"], "CS101")
        self.assertEqual(row["date"], "2026-08-15")
        self.assertEqual(row["status"], "P")
        conn.close()


class TestMonthlyReport(AttendanceTestBase):
    """Requirements 4, 5: Monthly report with present/absent distinction."""

    def setUp(self):
        super().setUp()
        add_student("CS101", "Alice", db_path=self.db_path)
        add_student("CS102", "Bob", db_path=self.db_path)

        # August 2026: Alice present on 1st, 4th, 5th; absent on 2nd
        mark_attendance("CS101", "2026-08-01", "P", db_path=self.db_path)
        mark_attendance("CS101", "2026-08-02", "A", db_path=self.db_path)
        mark_attendance("CS101", "2026-08-04", "P", db_path=self.db_path)
        mark_attendance("CS101", "2026-08-05", "P", db_path=self.db_path)

        # Bob present on 1st only
        mark_attendance("CS102", "2026-08-01", "P", db_path=self.db_path)

    def test_report_structure(self):
        """Requirement 4: Teacher generates report for a selected month."""
        report = generate_monthly_report(2026, 8, db_path=self.db_path)
        self.assertEqual(report["year"], 2026)
        self.assertEqual(report["month"], 8)
        self.assertEqual(report["days_in_month"], 31)
        self.assertEqual(len(report["students"]), 2)

    def test_present_absent_distinction(self):
        """Requirement 5: Report correctly distinguishes present/absent."""
        report = generate_monthly_report(2026, 8, db_path=self.db_path)

        alice = next(s for s in report["students"] if s["roll_number"] == "CS101")
        self.assertEqual(alice["present_count"], 3)   # Aug 1, 4, 5
        self.assertEqual(alice["absent_count"], 1)     # Aug 2
        self.assertEqual(alice["unmarked_count"], 27)  # rest of month

        # Verify individual day statuses
        self.assertEqual(alice["records"]["2026-08-01"], "P")
        self.assertEqual(alice["records"]["2026-08-02"], "A")
        self.assertEqual(alice["records"]["2026-08-03"], "-")  # unmarked

        bob = next(s for s in report["students"] if s["roll_number"] == "CS102")
        self.assertEqual(bob["present_count"], 1)
        self.assertEqual(bob["absent_count"], 0)
        self.assertEqual(bob["unmarked_count"], 30)

    def test_empty_month(self):
        report = generate_monthly_report(2026, 1, db_path=self.db_path)
        # Should still return all students with all days unmarked
        self.assertEqual(len(report["students"]), 2)
        alice = report["students"][0]
        self.assertEqual(alice["present_count"], 0)
        self.assertEqual(alice["absent_count"], 0)

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            generate_monthly_report(2026, 13, db_path=self.db_path)

    def test_format_report_text(self):
        report = generate_monthly_report(2026, 8, db_path=self.db_path)
        text = format_report_text(report)
        self.assertIn("2026-08", text)
        self.assertIn("Alice", text)
        self.assertIn("Bob", text)
        self.assertIn("Present:", text)
        self.assertIn("Absent:", text)


class TestEndToEndWorkflow(AttendanceTestBase):
    """Requirement 8: Complete end-to-end attendance workflow."""

    def test_full_workflow(self):
        # Teacher registers 3 students
        add_student("S001", "Alice", db_path=self.db_path)
        add_student("S002", "Bob", db_path=self.db_path)
        add_student("S003", "Charlie", db_path=self.db_path)

        # Day 1: all present
        for roll in ("S001", "S002", "S003"):
            ok, _ = mark_attendance(roll, "2026-09-01", "P", db_path=self.db_path)
            self.assertTrue(ok)

        # Day 2: Alice absent, Bob present, Charlie present
        mark_attendance("S001", "2026-09-02", "A", db_path=self.db_path)
        mark_attendance("S002", "2026-09-02", "P", db_path=self.db_path)
        mark_attendance("S003", "2026-09-02", "P", db_path=self.db_path)

        # Day 3: only Bob marks attendance
        mark_attendance("S002", "2026-09-03", "P", db_path=self.db_path)

        # Attempt duplicate — should fail
        ok, msg = mark_attendance("S002", "2026-09-03", "P", db_path=self.db_path)
        self.assertFalse(ok)
        self.assertIn("already recorded", msg)

        # Attempt unregistered student
        ok, msg = mark_attendance("S999", "2026-09-03", db_path=self.db_path)
        self.assertFalse(ok)

        # Generate September report
        report = generate_monthly_report(2026, 9, db_path=self.db_path)
        self.assertEqual(len(report["students"]), 3)
        self.assertEqual(report["days_in_month"], 30)

        alice = next(s for s in report["students"] if s["roll_number"] == "S001")
        self.assertEqual(alice["present_count"], 1)
        self.assertEqual(alice["absent_count"], 1)
        self.assertEqual(alice["unmarked_count"], 28)

        bob = next(s for s in report["students"] if s["roll_number"] == "S002")
        self.assertEqual(bob["present_count"], 3)
        self.assertEqual(bob["absent_count"], 0)

        charlie = next(s for s in report["students"] if s["roll_number"] == "S003")
        self.assertEqual(charlie["present_count"], 2)

        # Verify text report renders
        text = format_report_text(report)
        self.assertIn("Alice", text)
        self.assertIn("Bob", text)
        self.assertIn("Charlie", text)
        self.assertIn("Present: 3", text)  # Bob's count


if __name__ == "__main__":
    unittest.main()
