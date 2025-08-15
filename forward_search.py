### this is forward search, given latex script address and line number, search using forward_map.json and file_map.json
#ai: please polish my goce dcode code
import json
import os
import sys

FILE_MAP_PATH = "./static/file_map.json"
FORWARD_MAP_PATH = "./static/forward_map.json"

with open(FILE_MAP_PATH, "r", encoding="utf-8") as f:
    file_map = json.load(f)

with open(FORWARD_MAP_PATH, "r", encoding="utf-8") as f:
    forward_map = json.load(f)

def handler(path, line):
    path = os.path.normpath(os.path.expanduser(path)).strip()
    filekey = None

    for key, value in file_map.items():
        if value.strip() == path:
            filekey = key
            break

    if filekey is None:
        raise Exception(f"Not able to find the suggested file {path}")

    if filekey not in forward_map:
        raise Exception(f"Not able to identify the file in the forward map {path} with filekey {filekey}")

    line_dict = forward_map[filekey]
    parsed_lines = sorted(map(int, line_dict.keys()))

    until = None
    for l in parsed_lines:
        if l <= line:
            until = l
        else:
            break

    if until is None:
        raise Exception(f"No valid line found in forward map for {path} with given line {line}")

    return line_dict[str(until)]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path> <line>")
        sys.exit(1)

    path_arg = sys.argv[1]
    try:
        line_arg = int(sys.argv[2])
    except ValueError:
        print("Line number must be an integer")
        sys.exit(1)

    result = handler(path_arg, line_arg)
    print(result)
#end
        
        
        

