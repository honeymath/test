import subprocess
import sys
import datetime
import json
import os

def handler(file_path, args="", **kwargs):
    try:
        args_list = args.split(',') if args else []
        result = subprocess.run(
            [sys.executable, file_path] + args_list,
            text=True,
            capture_output=True,
            check=True
        )
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "file": file_path,
            "args": args_list,
            "stdout": result.stdout[:200],
            "stderr": result.stderr[:200],
            "returncode": result.returncode
        }
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "result": result.returncode
        }
    except subprocess.CalledProcessError as e:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "file": file_path,
            "args": args_list,
            "stdout": e.stdout[:200],
            "stderr": e.stderr[:200],
            "returncode": e.returncode
        }
        return {
            "stdout": e.stdout,
            "stderr": e.stderr,
            "result": e.returncode
        }

print(json.dumps(handler("./synctex.py", "edit,-o,3:100:200:main.pdf"),indent=4))
