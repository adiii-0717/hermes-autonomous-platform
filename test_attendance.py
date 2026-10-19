from attendance_logic import mark_attendance, generate_monthly_report
import datetime

def test():
    # Clear existing data or ensure fresh run
    # Test 1: Mark Attendance
    success1, msg1 = mark_attendance("STUDENT001")
    print(f"Test 1 (Marking valid): Expected Success. Got: {success1} - {msg1}")

    # Test 2: Duplicate marking
    success2, msg2 = mark_attendance("STUDENT001")
    print(f"Test 2 (Duplicate): Expected False for already marked item. Got: {success2} - {msg2}")

    # Test 3: Different student same day
    success3, msg3 = mark_attendance("STUDENT002")
    print(f"Test 3 (Different Student): Expected Success. Got: {success3} - {msg3}")

    # Test 4: Report Generation (current month)
    today_month = datetime.datetime.now().strftime("%Y-%m")
    report, err = generate_monthly_report(today_month)
    print(f"Test 4 (Report for current month {today_month}): Expected report if data exists. Error: {err}")
    if not err:
        print(f"Report content:\n{report[:100]}...")

if __name__ == "__main__":
    test()
