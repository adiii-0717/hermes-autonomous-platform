#!/usr/bin/env python3
"""
Student Attendance System – CLI entry point.

Usage:
    python -m attendance_system

Menu:
    1. Add Student         (Teacher)
    2. Mark Attendance     (Student)
    3. Monthly Report      (Teacher)
    4. List Students
    5. Exit
"""
from datetime import date

from .db import initialize_db
from .attendance import (
    add_student,
    list_students,
    mark_attendance,
    generate_monthly_report,
    format_report_text,
)


def main():
    initialize_db()
    print("=" * 50)
    print("  Student Attendance System")
    print("=" * 50)

    while True:
        print("\n1. Add Student         (Teacher)")
        print("2. Mark Attendance     (Student)")
        print("3. Monthly Report      (Teacher)")
        print("4. List Students")
        print("5. Exit")
        choice = input("\nSelect option: ").strip()

        if choice == "1":
            name = input("Student name: ").strip()
            roll = input("Roll number : ").strip()
            ok, msg = add_student(roll, name)
            print(msg)

        elif choice == "2":
            roll = input("Enter your roll number: ").strip()
            ok, msg = mark_attendance(roll)
            print(msg)

        elif choice == "3":
            try:
                year = int(input("Year  (e.g. 2026): ").strip())
                month = int(input("Month (1-12)     : ").strip())
                report = generate_monthly_report(year, month)
                print("\n" + format_report_text(report))
            except (ValueError, Exception) as e:
                print(f"Error: {e}")

        elif choice == "4":
            students = list_students()
            if students:
                for s in students:
                    print(f"  {s['roll_number']}  —  {s['name']}")
            else:
                print("  No students registered yet.")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Enter 1-5.")


if __name__ == "__main__":
    main()
