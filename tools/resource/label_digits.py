"""
从 20_processed/ 里的 binary 图标注数字模板，存到 30_templates/。

用法：
  1. 先用 make_digits_template.py 截图并生成 binary 图
  2. 打开 20_processed/ 确认 binary 图里数字清晰可见
  3. 运行本脚本，按提示输入每张图显示的数字
  4. 重复直到 0-9 全部收集完毕
"""

import sys
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

PROC_DIR   = ROOT / "data" / "resource" / "20_processed"
TMPL_DIR   = ROOT / "data" / "resource" / "30_templates"
DIGIT_SIZE = (32, 48)   # 模板统一尺寸 (宽, 高)


def _filter_left_outlier(boxes: list) -> list:
    if len(boxes) < 2:
        return boxes
    x0, _, w0, _ = boxes[0]
    if boxes[1][0] - (x0 + w0) > 20:
        return boxes[1:]
    return boxes


def find_digit_boxes(binary: np.ndarray) -> list[tuple[int, int, int, int]]:
    h = binary.shape[0]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if ch > h * 0.3 and cw >= 8:
            boxes.append((x, y, cw, ch))
    boxes.sort(key=lambda b: b[0])
    return _filter_left_outlier(boxes)


def save_debug(binary: np.ndarray, boxes: list, binary_path: Path) -> None:
    """把轮廓框和序号画在图上存成 _debug.png，方便核对顺序。"""
    debug = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    for i, (x, y, cw, ch) in enumerate(boxes):
        cv2.rectangle(debug, (x, y), (x + cw, y + ch), (0, 200, 255), 1)
        cv2.putText(debug, str(i + 1), (x, y - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 255), 1)
    debug_path = binary_path.parent / binary_path.name.replace("_binary.png", "_debug.png")
    cv2.imwrite(str(debug_path), debug)
    print(f"  → debug 图: {debug_path.name}  (共 {len(boxes)} 个轮廓)")


def label_one(binary_path: Path) -> None:
    binary = cv2.imread(str(binary_path), cv2.IMREAD_GRAYSCALE)
    boxes  = find_digit_boxes(binary)

    save_debug(binary, boxes, binary_path)

    user_input = input(f"  按序号输入数字（如 2665962），回车跳过: ").strip()
    if not user_input.isdigit():
        print("  跳过")
        return

    if len(boxes) != len(user_input):
        print(f"  [WARN] 找到 {len(boxes)} 个轮廓，输入了 {len(user_input)} 个数字，不匹配，跳过")
        return

    TMPL_DIR.mkdir(parents=True, exist_ok=True)
    for (x, y, cw, ch), digit_char in zip(boxes, user_input):
        crop    = binary[y:y + ch, x:x + cw]
        resized = cv2.resize(crop, DIGIT_SIZE)
        cv2.imwrite(str(TMPL_DIR / f"{digit_char}.png"), resized)

    print(f"  保存了 {len(user_input)} 个模板")


def report() -> None:
    collected = sorted(p.stem for p in TMPL_DIR.glob("?.png") if p.stem.isdigit())
    missing   = sorted(set("0123456789") - set(collected))
    print(f"\n[模板进度] 已收集: {collected if collected else '无'}")
    print(f"           还缺:   {missing   if missing   else '全部完成 ✓'}")


def main() -> None:
    binaries = sorted(PROC_DIR.glob("*_binary.png"))
    if not binaries:
        print(f"[ERROR] {PROC_DIR} 里没有 binary 图，先运行 make_digits_template.py")
        return

    print(f"找到 {len(binaries)} 张 binary 图，逐一标注（回车跳过）：\n")
    for p in binaries:
        label_one(p)

    report()


if __name__ == "__main__":
    main()