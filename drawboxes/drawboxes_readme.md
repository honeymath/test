# drawboxes 项目文档

## 1. 项目简介
本项目的目标是从 `.synctex` 文件中解析出 LaTeX 源文件行号与 PDF 坐标的对应关系，并在 PDF 中以矩形框和文本标签的形式可视化这些映射，同时生成正向映射表 `forward_map.json` 和反向映射表 `reverse_map.json`，方便后续查询和调试。

---

## 2. 技术栈
- **Python 3**
- **PyMuPDF (fitz)**：用于在 PDF 上绘制矩形和插入文本。
- **JSON**：存储正向与反向映射表。
- **Synctex 文本解析**：手动解析 `.synctex` 格式内容，提取文件号、行号、PDF 页码、PDF 坐标等信息。

---

## 3. `.synctex` 文件结构解析
### 关键标记
- `{n`：PDF 第 `n` 页开始（1-based 页码）。
- `}n`：PDF 第 `n` 页结束。
- `!m`：TeX 页号（不直接用于 PDF 页映射）。
- `Input:file_num:/path/to/file`：声明接下来的记录来自哪个源文件。
- `k<file_num>,<line_num>:<x>,<y>:...`：普通坐标记录（type=`k`）。
- `g<file_num>,<line_num>:...`：另一类坐标记录（type=`g`，在 v8 之后绘制时忽略）。
- `x<file_num>,<line_num>:...`：另一类坐标记录（type=`x`）。
- 坐标 `<x>,<y>` 为 PDF 原始单位，需除以 `65536` 转为实际 PDF 坐标（pt 单位）。

---

## 4. 实现原理
### 4.1 解析流程
1. **进入 Content 模式**：从 `Content:` 行之后开始解析有效记录。
2. **解析页码**：通过 `{n` / `}n` 控制当前 PDF 页索引。
3. **解析记录**：
   - 提取 `type`（k/g/x/$ 等）。
   - 从 `k123,45` 中解析出 `file_num=123`，`line_num=45`。
   - 提取 PDF 坐标 `(pdf_x, pdf_y)`，并除以 `65536.0`。
4. **存储记录**：记录类型、文件号、行号、页码、PDF 坐标。

---

### 4.2 绘制流程
1. 复制原 PDF（避免污染 `main.pdf`）。
2. 遍历前 `limit` 条记录（默认 5000）。
3. 过滤规则：如果 `type` 以 `g` 开头，则跳过绘制。
4. 按类型选取颜色（`type_color()` 函数）：
   - `k*` → 红色 `(1,0,0)`
   - `g*` → 蓝色 `(0,0,1)`（虽然跳过绘制）
   - `x*` → 绿色 `(0,0.5,0)`
   - `$*` → 紫色 `(0.5,0,0.5)`
5. 绘制矩形：
   ```python
   page.draw_rect(fitz.Rect(x, y + h, x + w, y), color=color, width=0.5)
   ```
   这样无论 `h` 正负都不会颠倒。
6. 绘制文本标签：
   ```
   f"{type}{file_num}:{line_num}"
   ```
   字体大小固定为 3pt。

---

### 4.3 映射表生成
#### forward_map.json
- **结构**：
  ```json
  {
    "file_num": {
      "line_num": { "x": <float>, "y": <float> }
    }
  }
  ```
- **规则**：
  - 第一层 key：`file_num`（字符串形式）
  - 第二层 key：`line_num`（字符串形式）
  - 值：第一次出现该 `(file_num, line_num)` 时的 PDF 坐标
  - 所有 key 按数值排序

#### reverse_map.json
- **结构**：
  ```json
  {
    "page_num": {
      "y_coord": {
        "x_coord": [file_num, line_num]
      }
    }
  }
  ```
- **规则**：
  - 第一层 key：PDF 页码（字符串，1-based）
  - 第二层 key：y 坐标值（字符串，保留两位小数）
  - 第三层 key：x 坐标值（字符串，保留两位小数）
  - 值：`[file_num, line_num]`
  - 合并规则：同一 y 下，相邻的 x 若指向相同 `(file_num, line_num)`，则只保留较小的 x 作为 key
  - 所有 key 按数值排序

---

## 5. 迭代过程与反馈修改记录
1. **v1-v2**：基础 Synctex 解析器，初步画框。
2. **v3**：增加 `limit` 参数控制绘制数量，输出至 `./static/mainbox.pdf`。
3. **v4-v5**：调试页码分布问题，发现 `!` 不是 PDF 页码标志，改为 `{n` / `}n`。
4. **v6-v7**：彻底使用 `{n` / `}n` 控制 PDF 页切换，解决只在奇数页绘制的问题。
5. **v8**：忽略 `g` 类型绘制，矩形尺寸改为 `w=5, h=-10`，并调整绘制代码顺序保证负高正常。
6. **v9**：首次生成 `forward_map.json` 和 `reverse_map.json`，但 `file_num` 解析依赖 `Input:`，导致 null。
7. **v10**：从 `k/g/x` 行直接解析 `file_num` 与 `line_num`，去掉 null；恢复颜色逻辑；对 JSON key 排序。

---

## 6. 变量说明
| 变量名 | 类型 | 含义 |
|--------|------|------|
| `record_type` | str | Synctex 记录类型（k/g/x/$ 等） |
| `file_num` | int | 源文件编号 |
| `line_num` | int | 源文件行号 |
| `pdf_page_index` | int | PDF 页索引（0-based） |
| `pdf_x` | float | PDF 坐标系 X 值（pt） |
| `pdf_y` | float | PDF 坐标系 Y 值（pt） |
| `forward_map` | dict | 正向映射表 |
| `reverse_map` | dict | 反向映射表 |
| `limit` | int | 绘制记录数量上限 |
| `w`, `h` | float | 绘制矩形宽度和高度（pt） |

---

## 7. 复现步骤
1. 准备 `main.pdf` 和 `main.synctex`。
2. 安装依赖：
   ```bash
   pip install pymupdf
   ```
3. 运行：
   ```bash
   python drawboxes_v10.py 5000
   ```
4. 查看结果：
   - `./static/mainbox.pdf`
   - `./static/forward_map.json`
   - `./static/reverse_map.json`

---

## 8. 注意事项
- Synctex 坐标单位需除以 `65536` 转换为 PDF 单位。
- `{n` / `}n` 是 PDF 页切换标志，不要与 `!` 混淆。
- `forward_map` 仅记录第一次出现的坐标，适合快速跳转。
- `reverse_map` 适合根据 PDF 点击位置查找源文件行号。
