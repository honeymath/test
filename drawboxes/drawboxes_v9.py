#!/usr/bin/env python3
import fitz, shutil, sys, os, json

def parse_synctex(synctex_path):
    data = []
    with open(synctex_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    content_mode = False
    current_pdf_page_index = None
    current_file_num = None

    for line in lines:
        line = line.strip()
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
            elif line.startswith("Input:"):
                # parse file_num from Input line
                try:
                    parts = line.split(":")
                    current_file_num = int(parts[1])
                except:
                    current_file_num = None
            elif current_pdf_page_index is not None and line and (line[0].isalpha() or line[0] in "($)"):
                record_type = ''
                i = 0
                while i < len(line) and not line[i].isdigit() and line[i] not in "([":
                    record_type += line[i]
                    i += 1
                try:
                    left, coords_part = line[len(record_type):].split(":", 1)
                    tag_str, line_str = left.split(",", 1)
                    pdf_coords = coords_part.split(":")[0]
                    pdf_x, pdf_y = map(float, pdf_coords.split(","))
                    data.append({
                        "type": record_type,
                        "tag": int(tag_str),
                        "line": int(line_str),
                        "file_num": current_file_num,
                        "pdf_page_index": current_pdf_page_index,
                        "pdf_x": pdf_x / 65536.0,
                        "pdf_y": pdf_y / 65536.0
                    })
                except:
                    pass
    return data

def build_forward_map(records):
    forward_map = {}
    seen = set()
    for rec in records:
        key = (rec['file_num'], rec['line'])
        if key not in seen and rec['file_num'] is not None:
            seen.add(key)
            forward_map.setdefault(str(rec['file_num']), {})[str(rec['line'])] = {
                "x": rec['pdf_x'],
                "y": rec['pdf_y']
            }
    return forward_map

def build_reverse_map(records):
    reverse_map = {}
    for rec in records:
        page = str(rec['pdf_page_index']+1)  # store as 1-based page number
        y = f"{rec['pdf_y']:.2f}"
        x = f"{rec['pdf_x']:.2f}"
        reverse_map.setdefault(page, {}).setdefault(y, {})
        reverse_map[page][y][x] = [rec['file_num'], rec['line']]
    # 合并相邻x
    for page, ydict in reverse_map.items():
        for y, xdict in list(ydict.items()):
            xs_sorted = sorted(xdict.keys(), key=lambda v: float(v))
            merged = {}
            prev_x = None
            prev_val = None
            for x in xs_sorted:
                val = xdict[x]
                if prev_x is not None and val == prev_val:
                    # merge: use smaller x
                    continue
                merged[x] = val
                prev_x = x
                prev_val = val
            reverse_map[page][y] = merged
    return reverse_map

def draw_boxes(pdf_path, synctex_path, output_path, limit):
    shutil.copyfile(pdf_path, output_path)
    doc = fitz.open(output_path)
    records = parse_synctex(synctex_path)

    forward_map = build_forward_map(records)
    reverse_map = build_reverse_map(records)
    with open("./static/forward_map.json", "w", encoding="utf-8") as f:
        json.dump(forward_map, f, indent=2)
    with open("./static/reverse_map.json", "w", encoding="utf-8") as f:
        json.dump(reverse_map, f, indent=2)

    for idx, rec in enumerate(records[:limit]):
        if rec["type"].startswith('g'):
            continue
        page_index = rec["pdf_page_index"]
        if 0 <= page_index < len(doc):
            page = doc[page_index]
            x = rec["pdf_x"]
            y = rec["pdf_y"]
            w, h = 5, -10
            color = (1, 0, 0)
            page.draw_rect(fitz.Rect(x, y, x + w, y + h), color=color, width=0.5)
            page.insert_text((x+1, y-5), f"{rec['type']}{rec['tag']}:{rec['line']}", fontsize=3, color=color)
    doc.saveIncr()

if __name__ == "__main__":
    limit = 5000
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