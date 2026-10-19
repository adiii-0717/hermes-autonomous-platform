from attendance_logic import mark_attendance, generate_monthly_report

def main():
    while True:
        print("\n--- Student Attendance System ---")
        print("1. Mark Attendance (Student)")
        print("2. Generate Monthly Report (Teacher)")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            roll_number = input("Enter your Roll Number: ")
            success, message = mark_attendance(roll_number)
            print(message)
        elif choice == "2":
            month = input("Enter month (YYYY-MM, e.g., 2024-08): ")
            report, error = generate_monthly_report(month)
            if error:
                print(error)
            else:
                print("\n--- Monthly Report ---")
                print(report)
        elif choice == "3":
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
