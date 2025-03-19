import os
import subprocess
import sys

print("Setting up dummy data for the college attendance system...")

# Get the Python executable path
python_executable = sys.executable

# Run the classes script first
print("\n=== CREATING DUMMY CLASSES ===\n")
subprocess.run([python_executable, "create_dummy_classes.py"])

# Then run the students script
print("\n=== CREATING DUMMY STUDENTS AND ATTENDANCE ===\n")
subprocess.run([python_executable, "create_dummy_students.py"])

# Create HOD user
print("\n=== CREATING HOD USER ===\n")
subprocess.run([python_executable, "create_hod_user.py"])

print("\n=== SETUP COMPLETE ===\n")
print("Dummy data has been created successfully!")
print("You can now log in with the following credentials:")
print("HOD: username=cs_hod, password=password123")
print("Staff: username=staff_user, password=password123")
print("Students: username=student_s{semester}_{number}, password=password123")
print("Example: student_s1_1, student_s2_3, etc.") 