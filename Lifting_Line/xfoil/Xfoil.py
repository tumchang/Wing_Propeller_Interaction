"""
============================================================================
This script is used for conducting XFoil analysis to get
airfoil polar data based on airfoil shape

main script name: xrotor_liftingline_main

Xfoil: https://web.mit.edu/drela/Public/web/xfoil/
-------------
Author: Chang Xu   TUM   03739064  August.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

import subprocess
import time


def xfoil_polar(path_xfoil, airfoil):
    # Start the .exe without blocking and set up communication pipes
    process = subprocess.Popen(path_xfoil, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)

    sleep_time = 0.1

    # Send the first command and wait for a short time
    process.stdin.write("LOAD\n")
    process.stdin.flush()
    time.sleep(sleep_time)  # adjust this delay as needed

    process.stdin.write(f"xfoil/{airfoil}.txt\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("oper\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("visc\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{1000000}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("mach\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{0.44}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("iter\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{40}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("alfa\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{-5}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("alfa\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{-10}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"pacc\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{airfoil}_polar.txt\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write("\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"aseq\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{-10}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{10}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    process.stdin.write(f"{0.25}\n")
    process.stdin.flush()
    time.sleep(sleep_time)

    # Close stdin when done sending commands
    process.stdin.close()

    # Capture output if needed
    output = process.stdout.read()
    print(output)

    # Ensure the process finishes
    process.wait()

    return


if __name__ == '__main__':
    # Path to xfoil.exe file
    xfoil_path = "./xfoil.exe"
    airfoil_name = '65-212'

    xfoil_polar(xfoil_path, airfoil_name)
