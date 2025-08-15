#!/usr/bin/env python3
import sys
import subprocess

def run_synctex(args):
    """调用系统 synctex 并传入参数"""
    cmd = ["synctex"] + args
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
    except subprocess.CalledProcessError as e:
        print(e.stdout, end="")
        print(e.stderr, file=sys.stderr, end="")
        sys.exit(e.returncode)

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python synctex.py edit -o <page>:<x>:<y>:<pdf>")
        print("  python synctex.py view -i <line>:<col>:<src> -o <pdf>")
        sys.exit(1)
    run_synctex(sys.argv[1:])

if __name__ == "__main__":
    main()

