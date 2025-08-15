#!/usr/bin/env python3
import fitz, shutil, sys, os

def parse_synctex(synctex_path):
    data = []
    with open(synctex_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    content_mode = False
    current_pdf_page_index = None

    for line in lines:
        line = line.strip()
        if not content_mode:
            if line.startswith("Content:"):
                content_mode = True
        else:
            if line.startswith("{") and line[1:].isdigit():
                # page start
                current_pdf_page_index = int(line[1:]) - 1
            elif line.startswith("}") and line[1:].isdigit():
                # page end
                current_pdf_page_index = None
            elif line.startswith("!"):
                # TeX page number, ignore
                continue
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
                        "pdf_page_index": current_pdf_page_index,
                        "pdf_x": pdf_x / 65536.0,
                        "pdf_y": pdf_y / 65536.0
                    })
                except:
                    pass
    return data

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

def draw_boxes(pdf_path, synctex_path, output_path, limit):
    shutil.copyfile(pdf_path, output_path)
    doc = fitz.open(output_path)
    records = parse_synctex(synctex_path)

    for idx, rec in enumerate(records[:limit]):
        page_index = rec["pdf_page_index"]
        if 0 <= page_index < len(doc):
            if idx < 5:
                print(f"[DEBUG] Record {idx}: pdf_page_index={page_index}, coords=({rec['pdf_x']:.2f},{rec['pdf_y']:.2f})")
            page = doc[page_index]
            x = rec["pdf_x"]
            y = rec["pdf_y"]  # no flip
            w, h = 20, 10
            color = type_color(rec["type"])
            page.draw_rect(fitz.Rect(x, y, x + w, y + h), color=color, width=0.5)
            page.insert_text((x+1, y+5), f"{rec['type']}{rec['tag']}:{rec['line']}", fontsize=3, color=color)
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