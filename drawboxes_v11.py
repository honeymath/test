#!/usr/bin/env python3
import fitz, shutil, sys, os, json

def parse_synctex(synctex_path):
    data = []
    files = {}
    with open(synctex_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    content_mode = False
    current_pdf_page_index = None

    for line in lines:
        line = line.strip()
#following code added by human
        if line.startswith("Input:"):
            _, file_index, file_path = line.split(":")
            files[file_index] = os.path.normpath(file_path) ## normalize the path
#above codes added by human
        if not content_mode:
            if line.startswith("Content:"):
                content_mode = True
        else:
            if line.startswith("{") and line[1:].isdigit():
                current_pdf_page_index = int(line[1:]) - 1
            elif line.startswith("}") and line[1:].isdigit():
                current_pdf_page_index = None
            elif line.startswith("!"):
                continue
            elif current_pdf_page_index is not None and line and (line[0].isalpha() or line[0] in "($)"):
                record_type = ''
                i = 0
                while i < len(line) and not line[i].isdigit() and line[i] not in "([":
                    record_type += line[i]
                    i += 1
                try:
                    left, coords_part = line[len(record_type):].split(":", 1)
                    # 从这里直接解析 file_num 和 line_num
                    file_num_str, line_num_str = left.split(",", 1)
                    file_num = int(file_num_str)
                    line_num = int(line_num_str)
                    pdf_coords = coords_part.split(":")[0]
                    pdf_x, pdf_y = map(float, pdf_coords.split(","))
                    data.append({
                        "type": record_type,
                        "tag": file_num,   # tag 就是 file_num
                        "line": line_num,
                        "file_num": file_num,
                        "pdf_page_index": current_pdf_page_index,
                        "pdf_x": pdf_x / 65536.0,
                        "pdf_y": pdf_y / 65536.0
                    })
                except:
                    pass
    return data, files

def type_color(t):
    if t.startswith('k'):
        return (1, 0, 0)  # red
    elif t.startswith('g'):
        return (0, 0, 1)  # blue
    elif t.startswith('x'):
        return (0, 0.5, 0)  # green
    elif t.startswith('$'):
        return (0.5, 0, 0.5)  # purple
    else:
        return (0, 0, 0)  # black

def build_forward_map(records):
    forward_map = {}
    seen = set()
    for rec in records:
        key = (rec['file_num'], rec['line'])
        if key not in seen:
            seen.add(key)
            forward_map.setdefault(str(rec['file_num']), {})[str(rec['line'])] = {
                "x": rec['pdf_x'],
                "y": rec['pdf_y']
            }
    # 排序 key
    forward_map_sorted = {k: dict(sorted(v.items(), key=lambda kv: int(kv[0]))) for k, v in sorted(forward_map.items(), key=lambda kv: int(kv[0]))}
    return forward_map_sorted

def build_reverse_map(records):
    reverse_map = {}
    for rec in records:
        page = str(rec['pdf_page_index']+1)  # 1-based page
        y = f"{rec['pdf_y']:.2f}"
        x = f"{rec['pdf_x']:.2f}"
        reverse_map.setdefault(page, {}).setdefault(y, {})
        reverse_map[page][y][x] = [rec['file_num'], rec['line']]
    # 合并相邻x，并排序
    for page, ydict in reverse_map.items():
        new_ydict = {}
        for y, xdict in sorted(ydict.items(), key=lambda kv: float(kv[0])):
            xs_sorted = sorted(xdict.keys(), key=lambda v: float(v))
            merged = {}
            prev_x = None
            prev_val = None
            for x in xs_sorted:
                val = xdict[x]
                if prev_x is not None and val == prev_val:
                    continue
                merged[x] = val
                prev_x = x
                prev_val = val
            new_ydict[y] = merged
        reverse_map[page] = new_ydict
    reverse_map_sorted = dict(sorted(reverse_map.items(), key=lambda kv: int(kv[0])))
    return reverse_map_sorted

def draw_boxes(pdf_path, synctex_path, output_path, limit):
    shutil.copyfile(pdf_path, output_path)
    doc = fitz.open(output_path)
    records , filetable = parse_synctex(synctex_path)

    forward_map = build_forward_map(records)
    reverse_map = build_reverse_map(records)
    with open("./static/forward_map.json", "w", encoding="utf-8") as f:
        json.dump(forward_map, f, indent=2)
    with open("./static/reverse_map.json", "w", encoding="utf-8") as f:
        json.dump(reverse_map, f, indent=2)
    with open("./static/file_map.json", "w", encoding="utf-8") as f: ## added by human
        json.dump(filetable, f, indent = 2)

    for idx, rec in enumerate(records[:limit]):
        if rec["type"].startswith('g'):
            continue
        page_index = rec["pdf_page_index"]
        if 0 <= page_index < len(doc):
            page = doc[page_index]
            x = rec["pdf_x"]
            y = rec["pdf_y"]
            w, h = 5, -10
            color = type_color(rec["type"])
            page.draw_rect(fitz.Rect(x, y + h, x + w, y), color=color, width=0.5)
            page.insert_text((x+1, y-5), f"{rec['type']}{rec['tag']}:{rec['line']}", fontsize=3, color=color)
    doc.saveIncr()

if __name__ == "__main__":
    limit = 6000
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            pass
    os.makedirs("./static", exist_ok=True)
    pdf_in = "main.pdf"
    synctex_in = "main.synctex"
    pdf_out = "./static/mainbox.pdf"
    draw_boxes(pdf_in, synctex_in, pdf_out, limit)
    print(f"✅ Boxes drawn to {pdf_out} (first {limit} records)")
    print(f"✅ Forward map saved to ./static/forward_map.json")
    print(f"✅ Reverse map saved to ./static/reverse_map.json")
    print(f"✅ Reverse map saved to ./static/file_map.json")
