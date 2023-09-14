import subprocess
import time

# Path to your .exe file
exe_path = "./xrotor.exe"

# Start the .exe without blocking and set up communication pipes
process = subprocess.Popen(exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Send the command and wait for a short time
process.stdin.write("LOAD\n")
process.stdin.flush()
time.sleep(1)  # adjust this delay as needed

process.stdin.write("geom_test.txt\n")
process.stdin.flush()
time.sleep(1)

process.stdin.write("\n")
process.stdin.flush()
time.sleep(1)

process.stdin.write("VPUT\n")
process.stdin.flush()
time.sleep(1)

process.stdin.write("test_slip.txt\n")
process.stdin.flush()
time.sleep(1)

# Close stdin when done sending commands
process.stdin.close()

# Capture output if needed
output = process.stdout.read()
print(output)

# Ensure the process finishes
process.wait()

pass
