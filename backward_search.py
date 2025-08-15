
### this is forward search, given latex script address and line number, search using forward_map.json and file_map.json
#ai: please polish my goce dcode code
import json
import os
import sys

FILE_MAP_PATH = "./static/file_map.json"
REVERSE_MAP_PATH = "./static/reverse_map.json"

with open(FILE_MAP_PATH, "r", encoding="utf-8") as f:
    file_map = json.load(f)

with open(REVERSE_MAP_PATH, "r", encoding="utf-8") as f:
    reverse_map = json.load(f)

def handler(page, x, y):
    if page not in reverse_map:
        raise Exception(f"Cannot identify page {page} in the reverse map")

    page_details = reverse_map[page]
    all_y = sorted(map(float, page_details.keys()))

    nexty = None
    for val in all_y:
        if val > y:
            nexty = val
            break
    if nexty is None:
        raise Exception(f"No y-coordinate greater than {y} found for page {page}")

    line_details = page_details[str(nexty)]
    all_x = sorted(map(float, line_details.keys()))

    nextx = None
    for val in all_x:
        if val > x:
            nextx = val
            break
    if nextx is None:
        nextx = all_x[-1]

    fileindex, line = line_details[str(nextx)]

##    print(f"Filekeys: {file_map.keys()}")
    fileindex = str(fileindex)
    if fileindex not in file_map:
        raise Exception(f"Not able to find the file index {fileindex} in the file map")

    filepath = os.path.normpath(os.path.expanduser(file_map[fileindex])).strip()
    return filepath, line

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <page> <x> <y>")
        sys.exit(1)

    try:
        page_arg = str(sys.argv[1])
        x_arg = float(sys.argv[2])
        y_arg = float(sys.argv[3])
    except ValueError:
        print("x and y must be numbers")
        sys.exit(1)

    result_path, result_line = handler(page_arg, x_arg, y_arg)
    print(result_path, result_line)
#end
        
        
        

