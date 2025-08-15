#!/usr/bin/env python3
import fitz, shutil, sys, os

def parse_synctex(synctex_path):
    data = []
    with open(synctex_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    content_mode = False
    current_page = None
    page_list = []
    for line in lines:
        line = line.strip()
        if not content_mode:
            if line.startswith("Content:"):
                content_mode = True
        else:
            if line.startswith("!"):
                try:
                    current_page = int(line[1:])
                    if current_page not in page_list:
                        page_list.append(current_page)
                except:
                    pass
            elif line and (line[0].isalpha() or line[0] in "($)"):
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
                        "page": current_page,
                        "pdf_x": pdf_x / 65536.0,
                        "pdf_y": pdf_y / 65536.0
                    })
                except:
                    pass
    return data, page_list

def draw_boxes(pdf_path, synctex_path, output_path, limit):
    shutil.copyfile(pdf_path, output_path)
    doc = fitz.open(output_path)
    records, page_list = parse_synctex(synctex_path)

    for rec in records[:limit]:
        if rec["page"] in page_list:
            page_index = page_list.index(rec["page"])
        else:
            continue
        page = doc[page_index]
        page_height = page.rect.height
        x = rec["pdf_x"]
        y = page_height - rec["pdf_y"]
        w, h = 20, 10
        rect = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(rect, color=(1, 0, 0), width=0.5)
        page.insert_text((x+1, y+7), f"{rec['type']}{rec['tag']}:{rec['line']}", fontsize=6, color=(0, 0, 0))
    doc.saveIncr()

if __name__ == "__main__":
    limit = 20
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